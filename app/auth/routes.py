from flask import redirect, url_for, session
from flask_login import login_required, logout_user

from app import limiter
from app.auth import bp
from app.auth.logic.login_ import login_
from app.auth.logic.request_reset import reset_req
from app.auth.logic.reset_token import reset_token


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def login():
    return login_()



@bp.route('/logout')
@limiter.limit("5 per minute", error_message="Too many login attempts.")
@login_required
def logout():
    session.pop('user_uuid', None)
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/reset_request', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def reset_request():
    return reset_req()


@bp.route('/password_reset/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts.")
def password_reset(token):
    return reset_token(token)
