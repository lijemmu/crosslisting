import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired

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

    states_list = [
        "- Select -",
        "AL - Alabama",
        "AK - Alaska",
        "AS - American Samoa",
        "AZ - Arizona",
        "AR - Arkansas",
        "CA - California",
        "CO - Colorado",
        "CT - Connecticut",
        "DE - Delaware",
        "DC - District of Columbia",
        "FL - Florida",
        "GA - Georgia",
        "GU - Guam",
        "HI - Hawaii",
        "ID - Idaho",
        "IL - Illinois",
        "IN - Indiana",
        "IA - Iowa",
        "KS - Kansas",
        "KY - Kentucky",
        "LA - Louisiana",
        "ME - Maine",
        "MD - Maryland",
        "MA - Massachusetts",
        "MI - Michigan",
        "MN - Minnesota",
        "MS - Mississippi",
        "MO - Missouri",
        "MT - Montana",
        "NE - Nebraska",
        "NV - Nevada",
        "NH - New Hampshire",
        "NJ - New Jersey",
        "NM - New Mexico",
        "NY - New York",
        "NC - North Carolina",
        "ND - North Dakota",
        "MP - Northern Mariana Islands",
        "OH - Ohio",
        "OK - Oklahoma",
        "OR - Oregon",
        "PA - Pennsylvania",
        "PR - Puerto Rico",
        "RI - Rhode Island",
        "SC - South Carolina",
        "SD - South Dakota",
        "TN - Tennessee",
        "TX - Texas",
        "UM - United States Minor Outlying Islands",
        "UT - Utah",
        "VT - Vermont",
        "VI - Virgin Islands",
        "VA - Virginia",
        "WA - Washington",
        "WV - West Virginia",
        "WI - Wisconsin",
        "WY - Wyoming",
        "AA - Armed Forces Americas",
        "AE - Armed Forces Africa",
        "AE - Armed Forces Canada",
        "AE - Armed Forces Europe",
        "AE - Armed Forces Middle East",
        "AP - Armed Forces Pacific"
    ]

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    # insert inventory location here
    street_address = StringField('Street Address', validators=[DataRequired()])
    unit_type = SelectField('Unit Type', choices=unit_types_list, default="- Select -")
    unit_number = StringField('Unit Number')
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices=states_list, default="- Select -")
    zipcode = StringField('Zipcode', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user_obj = User.query.filter_by(username=username.data).first()
        if user_obj:
            raise ValidationError("Username already in use.")
        if requests.get(" https://leetcode.com/" + username.data).status_code == 404:
            raise ValidationError("Leetcode ID does not exists. Please enter a valid Leetcode ID")

    def validate_email(self, email):
        user_obj = User.query.filter_by(email=email.data).first()
        if user_obj:
            raise ValidationError("Email already in use.")


class LoginForm(FlaskForm):
    existing_user = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    existing_pass = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Log In')


class SearchForm(FlaskForm):
    searched = StringField("Search for an item", validators=[DataRequired()])
    search_btn = SubmitField("Search")


class ListingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    post_btn = SubmitField("Post")
