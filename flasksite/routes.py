import json
from urllib.parse import urlparse, urljoin

"""Ref https://github.com/matecsaj/ebay_rest for selenium install and ebay_rest setup"""
import selenium.common
import sqlalchemy.exc
from flask import render_template, url_for, flash, redirect, request, session, g, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_

from flasksite import app, bcrypt, db
# from flask_bcrypt import Bcrypt
from flasksite.forms import RegistrationForm, LoginForm, SearchForm, ListingForm, UpdateAccountForm
# from flask_behind_proxy import FlaskBehindProxy
# from flask_sqlalchemy import SQLAlchemy
from flasksite.api import ebay_api
from flasksite.model import User, Listing
from flasksite.api import country
import ebay_rest.a_p_i as ebay
from ebay_rest import Error
from flasksite.api.mercadolibre import MercadoLibreAPI

MERCADOLIBRE_APP_ID = "5200906880853734"


@app.route("/")
@app.route("/home", methods=["POST"])
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

def create_ebay_inventory_location(api):
    merchant_location_data = {
        "location": {
            "address": {
                "addressLine1": current_user.street_address,
                "addressLine2": current_user.address_line2,
                "city": current_user.city,
                "stateOrProvince": current_user.state,
                "postalCode": current_user.zipcode,
                "country": current_user.country
            }
        },
        "locationInstructions": "Items ship from here.",
        "name": "Inventory Location 1",
        "merchantLocationStatus": "ENABLED",
        "locationTypes": [
            "STORE"
        ]
    }

    merchant_loc_key = f"LOC{current_user.zipcode}"
    ebay_api.create_inventory_location(api, location_data=merchant_location_data, loc_key=merchant_loc_key)

@app.route("/listings", methods=['GET', 'POST'])
def listings():
    form = ListingForm()
    user_listings = Listing.query.filter_by(username=current_user.first_name+" "+current_user.last_name).all()
    if form.validate_on_submit():
        listing = Listing(username=current_user.first_name + " " + current_user.last_name,
                          profile_pic=current_user.profile_pic, title=form.title.data,
                          description=form.description.data)
        ebay_api_obj = ebay_init()

        try:
            create_ebay_inventory_location(ebay_api_obj)
            create_ebay_listing(ebay_api_obj, form)
        except:
            flash("Unable to create eBay listing.", 'danger')

        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('listings'))

    return render_template('listings.html', listing_form=form, listings=user_listings)

@app.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    # TODO ensure users cannot delete listings that aren't theirs
    listing_to_delete = Listing.query.filter_by(id=id).first()

    user_is_authorized = listing_to_delete.username == (current_user.first_name + current_user.last_name)

    if listing_to_delete and user_is_authorized:
        db.session.delete(listing_to_delete)
        db.session.commit()
    return redirect(url_for('listings'))


def ebay_init():  # sets up ebay api credentials
    application = {
        "app_id": "AlbertTe-Resellin-SBX-db14cffb5-cfd1ac3b",
        "cert_id": "SBX-b14cffb5e502-9d55-4736-8403-4947",
        "dev_id": "85b11c14-7d19-40e2-8452-afd0f7687b58",
        "redirect_uri": "Albert_Terc-AlbertTe-Resell-zeijgqsp"
    }

    try:
        username = session['ebayUsername']
        password = session['ebayPassword']
    except KeyError:
        flash("Please connect to your eBay account on the Profile page before creating a listing.", 'danger')
        return

    user = {
        "email_or_username": session['ebayUsername'],
        "password": session["ebayPassword"],
        "refresh_token": "",
        "refresh_token_expiry": ""
    }

    header = {
        "accept_language": "en-US",
        "affiliate_campaign_id": "",
        "affiliate_reference_id": "",
        "content_language": "en-US",
        "country": "US",
        "currency": "USD",
        "device_id": "",
        "marketplace_id": "EBAY_US",
        "zip": ""
    }

    try:
        api = ebay.API(application=application, user=user, header=header)
    except Error as error:
        print(f'Error {error.number} is {error.reason}  {error.detail}.\n')
    else:
        return api

        # item_data = set_item_data()

def create_ebay_listing(api, listing_form):
    offer_data = {
        "sku": "234234BH",
        "marketplaceId": "EBAY_US",
        "format": "FIXED_PRICE",
        "availableQuantity": 1,
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
                "value": "34.99"
            }
        },
        "quantityLimitPerBuyer": 1,
        "includeCatalogProductDetails": True,
    }


    item_data = {"condition": "USED_GOOD", "packageWeightAndSize": {
        "dimensions": {
            "height": 6,
            "length": 2,
            "width": 1,
            "unit": "INCH"
        },
        "weight": {
            "value": 1,
            "unit": "POUND"
        }
    }, "availability": {
        "shipToLocationAvailability": {
            "quantity": 1
        }
    }, 'product': {}}

    product_info = item_data['product']
    product_info['title'] = listing_form.title.data
    # product_info['aspects'] = scraper.get_details()
    # product_info['imageURLs'] = scraper.get_pictures()

    ebay_api.create_listing(api, offer_data['sku'], item_data, offer_data)
    # sql.prompt_user()
    # Uncomment line below to clear all inventory items, locations, listings, and clear the database
    # ebay_api.clear_entities(api


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user



    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic


    updateForm = UpdateAccountForm()



    ebayLogin = LoginForm()


 


    return render_template("profile.html", subtitle=subtitle, user=user, 
    profile_pic=profile_pic, login_form = ebayLogin, 
    update_form = updateForm)


@app.route("/profile/ebay", methods=['POST'])
@login_required
def ebay_login():
    user = current_user



    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic

    updateForm = UpdateAccountForm()

    ebayLogin = LoginForm()

    if ebayLogin.validate_on_submit():
        print("added credentials to session")
        session["ebayUsername"] = ebayLogin.existing_email.data
        session["ebayPassword"] = ebayLogin.existing_pass.data
        return redirect(url_for('profile'))


    return render_template("profile.html", subtitle=subtitle, user=user, 
    profile_pic=profile_pic, login_form = ebayLogin, 
    update_form = updateForm)



@app.route("/profile/update", methods=['POST'])
@login_required
def update_profile():
    user = current_user



    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic


    updateForm = UpdateAccountForm()
    validate =  updateForm.validate_on_submit()
    if validate:
        address_line2 = f"{updateForm.unit_type.data} {updateForm.unit_number.data}"
        if "- Select -" in address_line2:  # when address line 2 isn't filled out in the form
            current_user.first_name = updateForm.first_name.data, 
            current_user.last_name= updateForm.last_name.data,
            current_user.email= updateForm.email.data,
            current_user.street_address= updateForm.street_address.data, 
            current_user.city= updateForm.city.data,
            current_user.state= updateForm.state.data, 
            current_user.zipcode= updateForm.zipcode.data, 
            current_user.country= updateForm.country.data,
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('profile'))

        else:
            current_user.first_name = updateForm.first_name.data, 
            current_user.last_name= updateForm.last_name.data,
            current_user.email= updateForm.email.data,
            current_user.street_address= updateForm.street_address.data,
            current_user.address_line2 = address_line2, 
            current_user.city= updateForm.city.data,
            current_user.state= updateForm.state.data, 
            current_user.zipcode= updateForm.zipcode.data, 
            current_user.country= updateForm.country.data,
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('profile'))
    else:
        print(updateForm.errors)
        flash('Your account failed to update ' + " ".join("=".join(map(str, updateForm.errors.values())) for dictionary in updateForm.errors) , 'danger')
        return redirect(url_for('profile'))

    
    # ebayLogin = LoginForm()



    # return render_template("profile.html", subtitle=subtitle, user=user,
    # profile_pic=profile_pic, login_form = ebayLogin,
    # update_form = updateForm)


@app.route("/profile/ebay/response", methods=['GET', 'POST'])
def validate_ebay_login():
    ebayLogin = LoginForm()

    if ebayLogin.validate_on_submit():

        print("valid ebay login")
        return jsonify({"valid": True})
    else:
        print("wrong ebay login")
        return jsonify(ebayLogin.errors)



@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    pass

'''
@app.route("/listings")
def listings():
    return render_template("listings.html")
'''

@app.route("/mercadolibre_oauth", methods=['GET'])
def mercadolibreoauth():
    url = "https://auth.mercadolibre.com.pe/authorization?response_type=code&client_id=" + MERCADOLIBRE_APP_ID + "&redirect_uri=https://crosslisting-testdb.herokuapp.com/profile"
    return redirect(url, code=302)


@app.route("/profile?code=<code>")
def get_code():
    pass
    #code = request.args.get("code")
    #mercado_libre_api = MercadoLibreAPI(code)
    #access_token, refresh_token = mercado_libre_api.get_access_token()
    #set_cookie("at", value = access_token, httponly = True)    
    #set_cookie("rt", value = refresh_token, httponly = True)
    #access_tokenNNN = cookies.get("at")
    #print(access_token) 



def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def hash_pass(password):
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return pw_hash
