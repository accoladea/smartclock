from smartclock import app, db
from flask import render_template, redirect, url_for, flash, request, session, abort
from smartclock.forms import RegistrationForm, LoginForm, EmailPasswordForm, PasswordResetForm,  SettingsForm
from smartclock.models import User
from smartclock.functions import check_password, hash_password
from flask_login import login_user, logout_user, login_required, current_user
from smartclock.email import send_email2
from io import BytesIO
import pyqrcode

@app.route("/")
@app.route("/home")
def home():
    return render_template('public/home.html')

@app.route("/about")
def about():
    return render_template('public/about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    # in case, if user is already logged in, it will redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = hash_password(password=form.password.data)
        user = User(username=form.username.data, password=hashed_password, email=form.email.data,
                    last_name=form.lname.data, first_name=form.fname.data)

        db.session.add(user)
        db.session.commit()

        flash("You have successfully created your account, confirm your email and start signing in", "success")

        send_email2(form.email.data, "Confirm your email! & Welcome to SmartClock!", render_template('emailforms/confirm.html', current_user=user, token=user.generate_confirmation_token()))

        # return redirect(url_for('home'))
        # redirect to auth page, passing username in session
        session["username"] = user.username
        return redirect(url_for("two_factor_setup"))

    return render_template('public/register.html', form=form, title='Register')

@app.route("/twofactor")
def two_factor_setup():
    if "username" not in session:
        return redirect(url_for("home"))
    username = session["username"]
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("home"))
    # since this page contains the sensitive qrcode,
    # make sure the browser does not cache it
    return render_template("public/two-factor-setup.html"), 200, {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"}

@app.route("/qrcode")
def qrcode():
    # validate user is currently registering and exists
    if "username" not in session: abort(404)
    username = session["username"]
    user = User.query.filter_by(username=username).first()
    if user is None: abort(404)
    # username removed so qr cannot be accessed again
    del session["username"]
    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
    "Content-Type": "image/svg+xml",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"}

@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password(password=form.password.data, hash_=user.password) and user.verify_totp(form.token.data):

            login_user(user, remember=form.remember.data)

            if user.confirmed:
                flash("Welcome back!", "info")
            else:
                flash("Please verify your email, a confirmation link is sent to your email.", "warning")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Invalid username, password, or token.")
            return redirect(url_for("login"))

    return render_template('public/login.html', form=form, title='Log in')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return render_template('auth/admin/admin.html', title='Dashboard')
    else:
        return render_template('auth/dashboard.html', title='Dashboard'), 200, {
    "Cache-Control": "no-cache, no-store",
    "Pragma": "no-cache",
    "Expires": "0"}

@app.route("/dashboard/<string:username>", methods=["GET"])
@login_required
def modify(username):
    if current_user.is_admin:
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template('auth/admin/user.html', selected_user=user, title='Manage Users')
            else:
                flash('There is no user with that username!','warning')
                return render_template('auth/admin/admin.html', title='Admin ')
        else:
            return render_template('auth/admin/admin.html', title="Admin ")
    else:
        return render_template('auth/dashboard.html', title='Dashboard')

@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        if(form.lname.data!=""):
            user = User.query.filter_by(id=current_user.id).first()
            user.last_name=form.lname.data
            db.session.commit()
        if (form.fname.data != ""):
            user = User.query.filter_by(id=current_user.id).first()
            user.first_name = form.fname.data
            db.session.commit()
        if (form.confirm_email.data != ""):
            user = User.query.filter_by(id=current_user.id).first()
            user.email = form.confirm_email.data
            db.session.commit()
        if (form.old_password.data != ""):
            user = User.query.filter_by(id=current_user.id).first()
            if user and check_password(password=form.old_password.data, hash_=user.password):
                if(form.confirm_password.data!=""):
                    user = User.query.filter_by(id=current_user.id).first()
                    hashed_password = hash_password(password=form.password.data)
                    user.password = hashed_password
                    db.session.commit()
                    flash("Updated!", "success")
                else:
                    flash("Password Not Match", "danger")
                    return redirect(url_for("settings"))
            else:
                flash("Password didn't match the original one!", "danger")
                return redirect(url_for("settings"))
        return redirect(url_for("dashboard"))
    return render_template('auth/settings.html', title='Settings', form=form)

@app.route("/view")
@login_required
def view():
    return render_template('auth/view.html', title='View Timesheets')


"""
    EMAIL Routes & Other Configs
"""

@app.route("/confirm/<string:id>/<string:token>")
def confirm(id, token):
    current_user = User.query.get(id)
    if current_user.confirmed:
        flash("Your account is already activated", "info")
    elif current_user.confirm(token):
        flash("Your account is now confirmed", "info")
        current_user.confirmed = True
        db.session.commit()
    else:
        flash("Your confirmation link is invalid or has expired", "danger")
    return redirect(url_for("home"))

@app.route("/reset/<string:id>/<string:token>", methods=['GET', 'POST'])
def reset(id, token):
    form = PasswordResetForm()
    user = User.query.get(id)
    if user.confirmresettoken(token):
        if (form.validate_on_submit()):
            hashed_password = hash_password(password = form.new_password.data)
            if(check_password(form.new_password.data, user.password)):
                flash("Cannot reset password to your current password", "danger")
            else:
                flash("Password reset!", "success")
                user.password = hashed_password
                db.session.commit()
                return redirect(url_for("home"))
    else:
        flash("Your token is invalid or expired, start over again", "warning")
        return redirect(url_for("home"))
    return render_template('public/reset.html', form=form, title= "Password Reset")

# resetmessage asks for a valid email, then it sends a password reset email to the user
@app.route("/resetmessage", methods=['GET','POST'])
def resetmessage():
    form = EmailPasswordForm()
    if(form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("If your email exists in our database, it will be sent to your email address for you to confirm!", "info")
            send_email2(form.email.data, "password reset email", render_template('emailforms/resetmessage.html', current_user=user, token=user.generate_reset_token()))
            return redirect(url_for("home"))
    return render_template('public/resetbyemail.html', form=form, title="Password Reset")
