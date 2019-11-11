from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba212'
database_name = 'site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database_name

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager=LoginManager(app)
login_manager.login_view = 'login' # hidden page implementation starts here

"""
By default, when a user attempts to access a login_required view without being logged in, 
Flask-Login will flash a message and redirect them to the log in view. 
(If the login view is not set, it will abort with a 401 error.)
The name of the log in view can be set as LoginManager.login_view.
"""

from smartclock import routes
