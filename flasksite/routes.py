from urllib.parse import urlparse, urljoin

import sqlalchemy.exc
from flask import render_template, url_for, flash, redirect, request, session, g, abort
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_

from flasksite import app, bcrypt, db
# from flask_bcrypt import Bcrypt
from flasksite.forms import RegistrationForm, LoginForm, SearchForm, ListingForm
# from flask_behind_proxy import FlaskBehindProxy
# from flask_sqlalchemy import SQLAlchemy
from flasksite.model import User, Listing


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

    #   github_form = GitHubForm()
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        user = User(username=reg_form.username.data, email=reg_form.email.data, password_hash=hash_pass(reg_form.password.data))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created for {reg_form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', register_form=reg_form)


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
        given_user = login_form.existing_user.data  # form inputs
        given_pass = login_form.existing_pass.data
        user_obj = User.query.filter_by(username=given_user).first()

        if user_obj and bcrypt.check_password_hash(user_obj.password_hash, given_pass):
            login_user(user_obj)

            next_url = request.args.get('next')
            print(f"nexturl: {next_url}")

            if not is_safe_url(next_url):
                return abort(400)

            flash(f'Successfully logged in as {login_form.existing_user.data}!', 'success')
            return redirect(next_url or url_for('home'))
        else:
            flash(f'Invalid username and/or password', 'danger')
    return render_template('login.html', title="Login", login_form=login_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/new_listing", methods=['GET', 'POST'])
def new_listing():
    form = ListingForm()
    print(current_user.username)
    print(Listing.query.all())
    if form.validate_on_submit():
        listing = Listing(username=current_user.username, profile_pic=current_user.profile_pic, title=form.title.data,
                    description=form.content.data)
        print(listing)
        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_listing.html', listing_form=form)


@app.route("/profile")
@login_required
def profile():
    user = current_user

    subtitle = "My Profile" if user == current_user else "Profile"
    profile_pic = url_for('static', filename=f"img/{user.profile_pic}")  # change to GitHub pic


    return render_template("profile.html", subtitle=subtitle, user=user)

@app.route("/listings")
def listings():
    return render_template("listings.html")


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def hash_pass(password):
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return pw_hash
