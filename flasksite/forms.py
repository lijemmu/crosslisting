import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NoneOf

from flasksite.api import country
from flasksite.model import User


class RegistrationForm(FlaskForm):
    unit_types_list = [
        "- Select -",
        "APT - Apartment",
        "BSMT - Basement",
        "BLDG - Building",
        "DEPT - Department",
        "FL - Floor",
        "FRNT - Front",
        "HNGR - Hanger",
        "KEY - Key",
        "LBBY - Lobby",
        "LOT - Lot",
        "LOWR - Lower",
        "OFC - Office",
        "Other",
        "PH - Penthouse",
        "PIER - Pier",
        "REAR - Rear",
        "RM - Room",
        "SIDE - Side",
        "SLIP - Slip",
        "SPC - Space",
        "STOP - Stop",
        "STE - Suite",
        "TRLR - Trailer",
        "Unable to determine",
        "UNIT - Unit",
        "UPPR - Upper"
    ]

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    # insert inventory location here
    street_address = StringField('Street Address', validators=[DataRequired()])
    unit_type = SelectField('Unit Type', choices=unit_types_list)
    unit_number = StringField('Unit Number')
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State/Province', choices=[], validators=[NoneOf("- Select -",
                                                                         message="This field is required.")])
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    country = SelectField('Country', choices=["- Select -"] + country.get_countries(),
                          validators=[NoneOf("- Select -", message="This field is required.")])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user_obj = User.query.filter_by(email=email.data).first()
        if user_obj:
            raise ValidationError("Email already in use.")


class LoginForm(FlaskForm):
    existing_email = StringField('Email', validators=[DataRequired(), Email()])
    existing_pass = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Log In')


class SearchForm(FlaskForm):
    searched = StringField("Search for an item", validators=[DataRequired()])
    search_btn = SubmitField("Search")


class ListingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    post_btn = SubmitField("Post")
