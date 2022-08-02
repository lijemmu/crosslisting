from urllib.parse import urlparse, urljoin

import sqlalchemy.exc
from flask import render_template, url_for, flash, redirect, request, session, g, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_

from flasksite import app, bcrypt, db
# from flask_bcrypt import Bcrypt
from flasksite.forms import RegistrationForm, LoginForm, SearchForm, ListingForm
# from flask_behind_proxy import FlaskBehindProxy
# from flask_sqlalchemy import SQLAlchemy
from flasksite.api import ebay_api
from flasksite.model import User, Listing
from flasksite.api import country

import ebay_rest.a_p_i as ebay
from ebay_rest import Error


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template('home.html', subtitle="Catalog")


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    if not form.validate_on_submit():
        return redirect(url_for('home'))
    else:
        search_query = form.searched.data
        user_obj = User.query.filter(or_(
            (User.username.like(f'%{search_query}%')),
            (User.email.like(f'{search_query}%'))
        )).all()

        return render_template("search.html", form=form, searched=search_query, users=user_obj)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    reg_form = RegistrationForm()

    try:
        reg_form.state.choices = country.get_states(reg_form.country.data)
    except KeyError:
        reg_form.state.choices = ["- Select -"]


    if reg_form.validate_on_submit():
        full_address = f"{reg_form.street_address.data}, {reg_form.unit_type.data} {reg_form.unit_number.data}, \
                        {reg_form.city.data}, {reg_form.state.data} {reg_form.zipcode.data}, {reg_form.country.data}"
        address_line2 = f"{reg_form.unit_type.data} {reg_form.unit_number.data}"
        if "- Select -" in address_line2:  # when address line 2 isn't filled out in the form
            user = User(first_name=reg_form.first_name.data, last_name=reg_form.last_name.data,
                        email=reg_form.email.data,
                        street_address=reg_form.street_address.data, city=reg_form.city.data,
                        state=reg_form.state.data, zipcode=reg_form.zipcode.data, country=reg_form.country.data,
                        password_hash=hash_pass(reg_form.password.data))
        else:
            user = User(first_name=reg_form.first_name.data, last_name=reg_form.last_name.data,
                        email=reg_form.email.data,
                        street_address=reg_form.street_address.data, address_line2=address_line2,
                        city=reg_form.city.data,
                        state=reg_form.state.data, zipcode=reg_form.zipcode.data, country=reg_form.country.data,
                        password_hash=hash_pass(reg_form.password.data))

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created for {reg_form.first_name.data} {reg_form.last_name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', register_form=reg_form)


@app.route("/register/<my_country>")
def state(my_country):
    states = country.get_states(my_country)
    return jsonify({"states": states})


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # query the database to see if the username is present;
    # if so check for matching hash
    # if no username present reprompt;
    login_form = LoginForm()
    # reg_form = RegistrationForm()
    if login_form.validate_on_submit():
        given_user = login_form.existing_email.data  # form inputs
        given_pass = login_form.existing_pass.data
        user_obj = User.query.filter_by(email=given_user).first()

        if user_obj and bcrypt.check_password_hash(user_obj.password_hash, given_pass):
            login_user(user_obj)

            next_url = request.args.get('next')
            print(f"nexturl: {next_url}")

            if not is_safe_url(next_url):
                return abort(400)

            flash(f'Successfully logged in as {login_form.existing_email.data}!', 'success')
            return redirect(next_url or url_for('home'))
        else:
            flash(f'Invalid email and/or password', 'danger')
    return render_template('login.html', title="Login", login_form=login_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/listings", methods=['GET', 'POST'])
@login_required
def listings():
    form = ListingForm()
    #print(current_user.username)
    print(Listing.query.all())
    if form.validate_on_submit():
        listing = Listing(username=current_user.username, profile_pic=current_user.profile_pic, title=form.title.data,
                          description=form.content.data)
        print(listing)
        # ebay_init(form)
        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('listings.html', listing_form=form)


def ebay_init(listing_form):
    try:
        api = ebay.API(application='sandbox_1', user='sandbox_1', header='US')
    except Error as error:
        print(f'Error {error.number} is {error.reason}  {error.detail}.\n')
    else:

        # item_data = set_item_data()

        # sku = scraper.get_sku()

        offer_data = {
            "sku": listing_form.sku.data,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": listing_form.quantity.data,
            "categoryId": "30120",
            "listingDescription": listing_form.content.data,
            "listingPolicies": {
                "fulfillmentPolicyId": "3*********0",
                "paymentPolicyId": "3*********0",
                "returnPolicyId": "3*********0"
            },
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": listing_form.price.data
                }
            },
            "quantityLimitPerBuyer": 1,
            "includeCatalogProductDetails": True,
        }

        merchant_location_data = {
            "location": {
                "address": {
                    "addressLine1": "625 6th Ave",
                    "addressLine2": "Fl 2",
                    "city": "New York",
                    "stateOrProvince": "NY",
                    "postalCode": "10011",
                    "country": "US"
                }
            },
            "locationInstructions": "Items ship from here.",
            "name": "Cell Phone Vendor 6th Ave",
            "merchantLocationStatus": "ENABLED",
            "locationTypes": [
                "STORE"
            ]
        }
        merchant_loc_key = 'NYCLOC6TH'

        # ebay_api.create_listing(api, sku, item_data, offer_data, merchant_location_data, merchant_loc_key)
        # sql.prompt_user()
        # Uncomment line below to clear all inventory items, locations, listings, and clear the database
        # ebay_api.clear_entities(api


@app.route("/profile")
@login_required
def profile():
    user = current_user

    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic

    return render_template("profile.html", subtitle=subtitle, user=user, profile_pic=profile_pic)

'''
@app.route("/listings")
def listings():
    return render_template("listings.html")
'''


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def hash_pass(password):
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return pw_hash
