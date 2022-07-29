from flasksite import app, db, login_manager, postdb
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    street_address = db.Column(db.String(120), nullable=False)
    address_line2 = db.Column(db.String(20))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(), nullable=False)
    profile_pic = db.Column(db.String(20), default='default.png')
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.street_address}', '{self.address_line2}', " \
               f"'{self.city}', '{self.state}', '{self.zipcode}', '{self.country}', '{self.profile_pic}', '{self.password_hash}')"


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.png')
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    def __str__(self):
        return f"Post('{self.username}', '{self.title}', '{self.profile_pic}','{self.description}')"
