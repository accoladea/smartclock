from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail

app = Flask(__name__)

from smartclock.config import *

db = SQLAlchemy(app)
ma = Marshmallow(app)
mail = Mail(app)


login_manager=LoginManager(app)
login_manager.login_view = 'login'

from smartclock.view import *
from smartclock.api import *


