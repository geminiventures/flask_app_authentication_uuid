from jwt import encode, decode
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

from config import Config
from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, UpdateProfileForm
from models import db, User, Address, UserProfile, SocialProfile, EducationHistory, WorkExperience, Skill, load_user, bcrypt


app = Flask(__name__)
app.config.from_object(Config)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
db.init_app(app)

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
            phone_number = form.phone_number.data
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
        print(f"User password hash: {user.password_hash}")

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session['user_uuid'] = str(user.id) # Store user UUID in session for future use
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
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
            reset_link = url_for('reset_token', token=token, _external=True)
            flash(f'Reset your password here: {reset_link}', 'info')
        else:
            flash('No account found with that email.', 'danger')
    return render_template('reset_request.html', title='Reset Password', form=form)

# Password Reset
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    try:
        user_id = decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
        user = User.query.get(user_id)
    except Exception as e:
        flash(f'Invalid or expired token: {str(e)}', 'danger')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)

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