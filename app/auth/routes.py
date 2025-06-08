
from datetime import datetime, timedelta, timezone

import jwt
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Mail, Message

from app import current_app
from app import limiter, bcrypt
from app.auth import bp
from app.auth.forms import LoginForm, RequestResetForm
from models import User

mail = Mail(current_app)



def send_email(to, subject, template):
    msg = Message(subject=subject,
                  recipients=[to],
                  sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body = template
    mail.send(msg)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def login():
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
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    session.pop('user_uuid', None)
    logout_user()
    return redirect(url_for('main.index'))

from app import limiter




@bp.route('/reset_request', methods=['GET', 'POST'])
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
            token = jwt.encode(token_data, current_app.config['SECRET_KEY'], algorithm='HS256')
            reset_link = url_for('auth/reset_token', token=token, _external=True)
            send_email(to=user.email, subject='Password Reset Request', template=f'your reset link is: {reset_link}')

        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth/login'))

    return render_template('reset_request.html', title='Reset Password', form=form)





