import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flasksite.model import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    # insert inventory location here

    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user_obj = User.query.filter_by(username=username.data).first()
        if user_obj:
            raise ValidationError("Username already in use.")

    def validate_email(self, email):
        user_obj = User.query.filter_by(email=email.data).first()
        if user_obj:
            raise ValidationError("Email already in use.")


class LoginForm(FlaskForm):
    existing_user = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    existing_pass = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Log In')


class SearchForm(FlaskForm):
    searched = StringField("Search for a profile", validators=[DataRequired()])
    search_btn = SubmitField("Search")


class ListingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    post_btn = SubmitField("Post")
