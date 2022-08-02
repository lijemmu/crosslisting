from flask import Flask
from flask_bcrypt import Bcrypt
from flask_behind_proxy import FlaskBehindProxy
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# import config


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='063b5d59f24fbf66d126cfb5e661902f',
        SQLALCHEMY_DATABASE_URI='postgresql://iiilnvexangtgy:328a3f5230946f9d6069e5df35270ed672eeca6b2dee1f1374cec106317c67ea@ec2-54-159-175-38.compute-1.amazonaws.com:5432/dca3us5ktus2ad'


        # SQLALCHEMY_DATABASE_URI='postgresql://zghuakjjjmaizw:e7eb618d0d9815a8c487ec7b5505cb5200bc079fa1516dfc1d61f9daafb57e77@ec2-44-206-197-71.compute-1.amazonaws.com:5432/d9jqgsjfb7ptd5',
        
        # SQLALCHEMY_DATABASE_URI='sqlite:///site.db',
        # GITHUB_CLIENT_ID=config.CLIENT_ID,
        # GITHUB_CLIENT_SECRET=config.CLIENT_SECRET
    )

    return app


login_manager = LoginManager()

app = create_app()
proxied = FlaskBehindProxy(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
postdb = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flasksite import routes
