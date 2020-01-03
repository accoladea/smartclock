from smartclock import app, db, ma, login_manager
from flask_login import UserMixin
from smartclock.sqlite_handler import tableDoesNotExist
from itsdangerous import TimedJSONWebSignatureSerializer \
    as Serializer
import base64, os, onetimepass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.Text)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    confirmed = db.Column(db.Boolean, default=False)  # False == Email not authenticated --> True == Email authenticated
    otp_secret = db.Column(db.String(64))

    # update constructor to choose a random TOTP secret
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.otp_secret is None:
            secret = base64.b32encode(os.urandom(40))
        self.otp_secret = secret.decode("utf-8")

    # add helper function to generate the URI for TOTP
    def get_totp_uri(self):
        return "otpauth://totp/{0}:{1}?secret={2}&issuer={0}" \
            .format(app.config["MFA_APP_NAME"], self.username,
                    self.otp_secret)

    # add helper function to check submitted tokens
    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

    # admin's privileges
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    def generate_reset_token(self, expiration=600):
        s = Serializer(app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id}).decode("utf-8")

    def confirmresettoken(self, token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except Exception:
            return False
        if data.get("reset") != self.id:
            return False
        return True

    def confirm(self, token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except Exception:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.commit()
        return True


class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    clock_in_time = db.Column(db.DateTime)
    clock_out_time = db.Column(db.DateTime)
    is_clocked_in = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    user = db.relationship("User", backref="timesheets")



class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_approved', 'is_admin', 'confirmed', 'timesheets')


class TimesheetSchema(ma.ModelSchema):
    class Meta:
        model = Timesheet
        fields = ('id', 'date', 'clock_in_time', 'clock_out_time', 'is_clocked_in', 'user_id')


timesheet_schema = TimesheetSchema()
timesheets_schema = TimesheetSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

if tableDoesNotExist(User.__tablename__):
    db.drop_all()
    db.create_all()
