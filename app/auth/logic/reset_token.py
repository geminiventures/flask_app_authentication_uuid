from datetime import datetime
import jwt
import uuid
from flask import render_template, redirect, url_for, flash
from app import current_app, bcrypt, db
from app.auth.forms import ResetPasswordForm
from models import User

def reset_token(token):
    try:
        # Decode the token and check if it's expired
        token_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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
            return redirect(url_for('auth.login'))

        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password_hash = hashed_password
            db.session.commit()
            flash('Your password has been updated! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

    except jwt.ExpiredSignatureError:
        flash('The reset link has expired.', 'danger')
        return redirect(url_for('auth.reset_request'))

    except Exception as e:
        flash(f'Invalid or expired token: {str(e)}', 'danger')

    form = ResetPasswordForm()
    return render_template('auth/password_reset.html', title='Reset Password', form=form, token=token)
