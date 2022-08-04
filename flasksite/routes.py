import json
import os
from urllib.parse import urlparse, urljoin

"""Ref https://github.com/matecsaj/ebay_rest for selenium install and ebay_rest setup"""
import selenium.common
import sqlalchemy.exc
from flask import render_template, url_for, flash, redirect, request, session, g, abort, jsonify, make_response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_

from flasksite import app, bcrypt, db
# from flask_bcrypt import Bcrypt
from flasksite.forms import ListingForm, RegistrationForm, LoginForm, SearchForm, TechForm, ClothingForm, UpdateAccountForm
# from flask_behind_proxy import FlaskBehindProxy
# from flask_sqlalchemy import SQLAlchemy
from flasksite.api import ebay_api
from flasksite.model import User, Listing
from flasksite.api import country
import ebay_rest.a_p_i as ebay
from ebay_rest import Error
from werkzeug.utils import secure_filename
from flasksite.api.mercadolibre import MercadoLibreAPI

MERCADOLIBRE_APP_ID = "5200906880853734"


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template('home.html', subtitle="Catalog")


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
                        street_address=reg_form.street_address.data,
                        city=reg_form.city.data,
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
        os.mkdir(os.path.join(
            'flasksite',
            'static',
            'assets',
            str(current_user.id)
        ))
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
    my_country = current_user.country
    if current_user.country == "United States":
        my_country = 'US'

    merchant_location_data = {
        "location": {
            "address": {
                "addressLine1": current_user.street_address,
                "addressLine2": current_user.address_line2,
                "city": current_user.city,
                "stateOrProvince": current_user.state,
                "postalCode": current_user.zipcode,
                "country": my_country
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

@app.route("/listings", methods=['GET'])
def listings():
    listing_form = ListingForm()
    tech_form = TechForm()
    clothing_form = ClothingForm()
    user_listings = Listing.query.filter_by(user_id=current_user.id).order_by(Listing.id.desc())

    cookie_exist = False

    if request.cookies.get("at") or (session.get('ebayUsername') and session.get('ebayPassword')):
        cookie_exist = True
        print(cookie_exist)
    
    else:
        #flash("Please go to your profile and click on the Mercado Libre button")
        flash("You must connect your account to an external marketplace before creating a listing.")


    return render_template('listings.html', listing_form=listing_form, tech_form=tech_form, clothing_form=clothing_form, listings=user_listings,cookie_exist=cookie_exist)

@app.route("/listings/create/tech", methods=['POST'])
def create_tech():
    listing_form = ListingForm()
    tech_form = TechForm()
    clothing_form = ClothingForm()
    user_listings = Listing.query.filter_by(user_id=current_user.id).all()

    cookie_exist = False

    if request.cookies.get("at"):
        cookie_exist = True
        print(cookie_exist)
    
    else:
        flash("Please go to your profile and click on the Mercado Libre button")


    if tech_form.validate_on_submit():
        image = tech_form.image.data
        filename = secure_filename(image.filename)
        if not os.path.exists(os.path.join('flasksite', 'static', 'assets', str(current_user.id))):
            os.mkdir(os.path.join('flasksite', 'static', 'assets', str(current_user.id)))
        filepath = os.path.join(
            'assets',
            str(current_user.id),
            filename
        )
        image.save(os.path.join('flasksite', 'static', filepath))

        ebay_listing_url = ""
        if session.get('ebayUsername') and session.get('ebayPassword'):
            ebay_api_obj = ebay_init()
            try:
                create_ebay_inventory_location(ebay_api_obj)
                ebay_listing_url = create_ebay_listing(ebay_api_obj, tech_form)
            except:
                flash("Unable to create eBay listing.", 'danger')

        url = ""

        if request.cookies.get("at"):
            try:
                url = create_mercadolibre_listing(tech_form)
            except Exception as e:
                print(e)
                flash("Unable to create Mercado Libre listing.", 'danger')

        listing = Listing(user_id=current_user.id,
                          listing_pic=filename,
                          title=tech_form.title.data,
                          description=tech_form.description.data,
                          price=tech_form.price.data,
                          quantity=tech_form.quantity.data,
                          condition=tech_form.condition.data,
                          brand=tech_form.brand.data,
                          color=tech_form.color.data,
                          model=tech_form.model.data,
                          line=tech_form.line.data,
                          os_name=tech_form.os_name.data,
                          processor_brand=tech_form.processor_brand.data,
                          ebay_url=ebay_listing_url,
                          mercadolibre_url = url,
                          )

        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('listings'))
    elif request.method == "POST":
        data = json.dumps(tech_form.errors, ensure_ascii=False)
        return jsonify(data)

    return render_template('listings.html', listing_form=listing_form, tech_form=tech_form, clothing_form=clothing_form, listings=user_listings,cookie_exist=cookie_exist)

@app.route("/listings/create/clothing", methods=['POST'])
def create_clothing():
    listing_form = ListingForm()
    tech_form = TechForm()
    clothing_form = ClothingForm()
    user_listings = Listing.query.filter_by(user_id=current_user.id).all()

    cookie_exist = False

    if request.cookies.get("at") or (session.get('ebayUsername') and session.get('ebayPassword')):
        cookie_exist = True
        print(cookie_exist)
    
    else:
        #flash("Please go to your profile and click on the Mercado Libre button")
        flash("You must connect your account to an external marketplace before creating a listing.")



    if clothing_form.validate_on_submit():
        image = clothing_form.image.data
        filename = secure_filename(image.filename)
        filepath = os.path.join(
            'assets',
            str(current_user.id),
            filename
        )
        image.save(os.path.join('flasksite', 'static', filepath))

        ebay_api_obj = ebay_init()

        ebay_listing_url = ""

        if session.get('ebayUsername') and session.get('ebayPassword'):
            try:
                create_ebay_inventory_location(ebay_api_obj)
                ebay_listing_url = create_ebay_listing(ebay_api_obj, clothing_form)
            except:
                flash("Unable to create eBay listing.", 'danger')

        url = ""


        if request.cookies.get("at"):
            try:
                url = create_mercadolibre_listing(clothing_form)


            except Exception as e: 
                print(e)
                flash("Unable to create Mercado Libre listing.", 'danger')

        listing = Listing(user_id=current_user.id,
                          listing_pic=filename,
                          title=clothing_form.title.data,
                          description=clothing_form.description.data,
                          price=clothing_form.price.data,
                          quantity=clothing_form.quantity.data,
                          condition=clothing_form.condition.data,
                          brand=clothing_form.brand.data,
                          color=clothing_form.color.data,
                          size=clothing_form.size.data,
                          ebay_url=ebay_listing_url,
                          mercadolibre_url = url,
                          )

        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('listings'))
    elif request.method == "POST":
        data = json.dumps(clothing_form.errors, ensure_ascii=False)
        return jsonify(data)

    return render_template('listings.html', listing_form=listing_form, tech_form=tech_form, clothing_form=clothing_form, listings=user_listings, cookie_exist=cookie_exist)

@app.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    listing_to_delete = Listing.query.filter_by(id=id).first()
    user_is_authorized = listing_to_delete.user_id == current_user.id
    if listing_to_delete and user_is_authorized:
        # os.remove(os.path.join('flasksite', 'static', listing_to_delete.listing_pic))
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

def create_mercadolibre_listing(form):
    api = MercadoLibreAPI()
    access_token = request.cookies.get("at")
    api.update_access_token(access_token)


    if isinstance(form, ClothingForm):
        url = api.post_listing_clothes(form.title.data, form.description.data, str(form.price.data), form.quantity.data, form.condition.data, "6 meses", form.brand.data, form.color.data, form.size.data)
    else:
        url = api.post_listing_tech(form.title.data, form.description.data, str(form.price.data), form.quantity.data, form.condition.data, "6 meses", form.brand.data, form.line.data, form.model.data, form.color.data, form.os_name.data,form.processor_brand.data)

    return url
        
def create_ebay_listing(api, listing_form):
    offer_data = {
        "sku": "234234BH",
        "marketplaceId": "EBAY_US",
        "format": "FIXED_PRICE",
        "availableQuantity": listing_form.quantity.data,
        "categoryId": "30120",
        "listingDescription": listing_form.description.data,
        "listingPolicies": {
            "fulfillmentPolicyId": "3*********0",
            "paymentPolicyId": "3*********0",
            "returnPolicyId": "3*********0"
        },
        "pricingSummary": {
            "price": {
                "currency": "USD",
                "value": str(listing_form.price.data)
            }
        },
        "quantityLimitPerBuyer": 1,
        "includeCatalogProductDetails": True,
    }

    condition = listing_form.condition.data
    if condition == 'used':
        condition = "USED_GOOD"
    elif condition == 'new':
        condition = "NEW"

    item_data = {
        "condition": condition,
        "packageWeightAndSize": {
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
                "quantity": listing_form.quantity.data
            }
        }, 'product': {}}

    product_info = item_data['product']
    product_info['title'] = listing_form.title.data
    # product_info['brand'] = listing_form.brand.data

    if isinstance(listing_form, ClothingForm):
        product_info['aspects'] = {
            "Size": [listing_form.size.data],
        }

    elif isinstance(listing_form, TechForm):
        product_info['aspects'] = {
            "Model": [listing_form.model.data],
            "Processor Brand": [listing_form.processor_brand.data],
            "Operating System": [listing_form.os_name.data],
            "Line": [listing_form.line.data]
        }

    product_info['aspects']['Color'] = [listing_form.color.data]
    product_info['aspects']['brand'] = [listing_form.brand.data]

    return ebay_api.create_listing(api, offer_data['sku'], item_data, offer_data)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():

    code = request.args.get('code')
    user = current_user
    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic
    updateForm = UpdateAccountForm()
    ebayLogin = LoginForm()

    resp = make_response(render_template("profile.html", subtitle=subtitle, user=user, 
        profile_pic=profile_pic, login_form = ebayLogin, 
        update_form = updateForm))

    if(code):
        mercado_libre_api = MercadoLibreAPI()
        access_token, refresh_token = mercado_libre_api.get_access_token(code)
        #res.set_cookie("at", value = access_token, httponly = True)    
        #set_cookie("rt", value = refresh_token, httponly = True)
        #access_tokenNNN = cookies.get("at")

        resp.set_cookie("at", value = access_token, httponly = True)
        print(request.cookies.get("at"))

    return resp



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




@app.route("/mercadolibre_oauth", methods=['GET'])
def mercadolibreoauth():
    url = "https://auth.mercadolibre.com.pe/authorization?response_type=code&client_id=" + MERCADOLIBRE_APP_ID + "&redirect_uri=https://a4a3-2800-200-e630-3495-5d11-6913-5f0-5295.ngrok.io/profile"
    return redirect(url, code=302)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def hash_pass(password):
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return pw_hash
