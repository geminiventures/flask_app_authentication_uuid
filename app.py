import uuid

import jwt

# general Flask app functions and wrappers for routes, sessions and request handling, etc.
from flask import Flask, render_template, redirect, url_for, flash, request, session, get_flashed_messages
# flask login functions and wrappers
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
# to handle rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# to handle date of birth
from datetime import datetime, timedelta, timezone
from flask_bcrypt import Bcrypt

# Flask email to enable password reset functionality and the ability to send the email
from flask_mail import Mail, Message

import models
#import for handling the configuration as an object and importing the necessary settings from the config.py file.
from config import Config

# add forms used in the application here
from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, UpdateProfileForm

#import model functional components
from models import db, load_user, bcrypt, soft_delete_generic
# add models used in the application here
from models import User, Address, UserProfile, SocialProfile, EducationHistory, WorkExperience, Skill

app = Flask(__name__)

# Load from config which has a Config class with the necessary settings.
app.config.from_object(Config)

# request rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize db and sessions
db.init_app(app)

# Initialize and instantiate the Mail object within the app
mail = Mail(app)

# Create an instance of LoginManager and initialize it with the app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.user_loader(load_user)



@app.route('/')
def home():
    return render_template('home.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user: User = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            phone_number=form.phone_number.data
        )

        db.session.add(user)
        db.session.commit()

        address: Address = Address(
            user_id=user.id,
            street_address=form.street_address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            country=form.country.data
        )
        db.session.add(address)
        # Create user profile
        user_profile: UserProfile = UserProfile(
            user_id=user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=datetime.strptime(form.date_of_birth.data, '%d/%m/%Y'),
            bio=form.bio.data,
            hobbies=form.hobbies.data)
        db.session.add(user_profile)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session['user_uuid'] = str(user.id)  # Store user UUID in session for future use
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    session.pop('user_uuid', None)
    logout_user()
    return redirect(url_for('home'))


# User Profile
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.street_address = form.street_address.data
        current_user.phone_number = form.phone_number.data
        current_user.hobbies = form.hobbies.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.street_address.data = current_user.street_address
        form.phone_number.data = current_user.phone_number
        form.hobbies.data = current_user.hobbies
        form.bio.data = current_user.bio
    return render_template("account.html", form=form)


# Password Reset Request
@app.route('/reset_request', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token_expiry = datetime.now(tz=timezone.utc) + timedelta(hours=2)  # Token expires in 2 hours
            token_data = {
                'user_id': str(user.id),
                'exp': token_expiry  # Include expiry timestamp in the payload
            }
            token = jwt.encode(token_data, app.config['SECRET_KEY'], algorithm='HS256')
            reset_link = url_for('reset_token', token=token, _external=True)
            print(reset_link)
            send_email(to=user.email, subject='Password Reset Request', template=f'your reset link is: {reset_link}')

        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)



def send_email(to, subject, template):
    msg = Message(subject=subject,
                  recipients=[to],
                  sender=app.config['MAIL_DEFAULT_SENDER'])
    msg.body = template
    mail.send(msg)


# Password Reset
@app.route('/reset_token/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def reset_token(token):

    try:
        # Decode the token and check if it's expired
        token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_uuid = uuid.UUID(token_data['user_id'])
        print(user_uuid)
        print(datetime.now())
        print(datetime.fromtimestamp(token_data.get('exp', 0)))

        if datetime.now() > datetime.fromtimestamp(token_data.get('exp', 0)):
            flash('The reset link has expired.', 'danger')
            return redirect(url_for('home'))

        user = User.query.filter_by(id=user_uuid).first()
        if not user:
            flash('Invalid token.', 'danger')
            return redirect(url_for('login'))

        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password_hash = hashed_password
            db.session.commit()
            flash('Your password has been updated! You can now log in.', 'success')
            return redirect(url_for('login'))

    except jwt.ExpiredSignatureError:
        flash('The reset link has expired.', 'danger')
        return redirect(url_for('reset_request'))

    except Exception as e:
        flash(f'Invalid or expired token: {str(e)}', 'danger')

    form = ResetPasswordForm()
    return render_template('reset_token.html', title='Reset Password', form=form, token=token)




@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_uuid'])
    if not user:
        flash('User not found, data missing, please login.')
        return redirect(url_for('login'))

    form = UpdateProfileForm()
    if form.validate_on_submit():
        # Update user fields except username
        current_user.email = form.email.data
        current_user.street_address = form.street_address.data
        current_user.phone_number = form.phone_number.data
        current_user.hobbies = form.hobbies.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        # Pre-populate the form with existing user data
        form.email.data = current_user.email
        form.street_address.data = current_user.street_address
        form.phone_number.data = current_user.phone_number
        form.hobbies.data = current_user.hobbies
        form.bio.data = current_user.bio

    return render_template('profile.html', title='Profile Page', form=form)


if __name__ == '__main__':
    app.run(debug=True)
