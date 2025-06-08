from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user

from app import bcrypt
from app.auth.forms import LoginForm
from models import User


def login_():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session['user_uuid'] = str(user.id)  # Store user UUID in session for future use
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html', form=form)