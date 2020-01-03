from smartclock import app
from .names import database_name

# FLASK
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba212'

# SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database_name

# MAIL
app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'testsmartclock@gmail.com'
app.config['MAIL_PASSWORD'] = 'Rochester2019'
app.config['MAIL_DEFAULT_SENDER'] = 'testsmartclock@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# MFA
app.config["MFA_APP_NAME"] = "MFA-Demo"