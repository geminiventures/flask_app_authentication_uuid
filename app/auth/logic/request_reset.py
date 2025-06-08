
import jwt
from flask import render_template, redirect, url_for, flash
from app import current_app, mail
from flask_mail import Message
from app.auth.forms import RequestResetForm
from datetime import datetime, timedelta, timezone
from models import User

def send_email(to, subject, template):
    msg = Message(subject=subject,
                  recipients=[to],
                  sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body = template
    mail.send(msg)

def reset_req():

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
            reset_link = url_for('auth.password_reset', token=token, _external=True)
            print(reset_link)
            send_email(to=user.email, subject='Password Reset Request', template=f'your reset link is: {reset_link}')

        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.logout'))

    return render_template('auth/reset_request.html', title='Reset Password', form=form)

