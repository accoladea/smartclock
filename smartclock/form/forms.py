from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from smartclock.model.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("The username exists")
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError("The email exists")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')

class EmailPasswordForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    submit = SubmitField("Send password reset email")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            pass
        else:
            raise ValidationError("The email is not active on our server")

class TokenForm(FlaskForm):
    token = StringField("Token", validators=[DataRequired()])
    submit = SubmitField("Confirm")

class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Reset")

class SettingsForm(FlaskForm):
    fname = StringField('New First Name', validators=[Optional(), Length(min=2, max=20)])
    lname = StringField('New Last Name', validators=[Optional(), Length(min=2, max=20)])
    email = StringField('New Email', validators=[Optional(), Email()])
    confirm_email = StringField('Confirm New Email', validators=[EqualTo('email')])
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update Settings')
