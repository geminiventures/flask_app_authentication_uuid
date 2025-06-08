from datetime import datetime

from flask import render_template, redirect, url_for, flash
from flask_login import current_user

from app.registration import bp
from app.registration.forms import RegistrationForm
from models import bcrypt
from models import db, User, Address, UserProfile


@bp.route("/registration", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

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
    return render_template('registration/register.html', form=form)