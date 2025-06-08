from flask import Blueprint, render_template
from app import app

# bp = Blueprint('errors', __name__)

# from app.errors import handlers

@app.route("/")
@app.route("/index")
def index():
    current_user = {'username': 'Mark', 'is_authenticated': True}
    return render_template('home.html', title='Home', current_user=current_user)

# @app.route("/logout")
# def logout():
#     return "Logging out"
#
# @app.route("/account")
# def account():
#     return "Account"
#
# @app.route("/profile")
# def profile():
#     return "Profile"
#
# @app.route("/register")
# def register():
#     return "Register"
#
# @app.route("/login")
# def login():
#     return "Login"

