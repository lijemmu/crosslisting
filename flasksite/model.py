from flasksite import app, db, login_manager, postdb
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.png')
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_pic}', '{self.password_hash}')"


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.png')
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(20), nullable=False)

    def __str__(self):
        return f"Post('{self.username}', '{self.title}', '{self.profile_pic}','{self.description}')"