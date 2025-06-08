from app import app
from flask import redirect, url_for, session
from flask_login import login_required, logout_user

@app.route('/logout')
@login_required
def logout():
    session.pop('user_uuid', None)
    logout_user()
    return redirect(url_for('home'))