from flask import Flask, current_app
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_mail import Mail
from flask_limiter.util import get_remote_address
from flask_debugtoolbar import DebugToolbarExtension


login_manager = LoginManager()  # Create an instance of LoginManager
bcrypt = Bcrypt()
db = SQLAlchemy() # Create an instance of SQLAlchemy orm
mail=Mail()


limiter = Limiter(  # initialize rate limiter with universal limits
        key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
    )

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    db.init_app(app)  # Initialize the db object with the app

    login_manager.init_app(app)  # and initialize logins with the app context
    login_manager.login_view = 'auth.login'

    mail.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.registration import bp as registration_bp
    app.register_blueprint(registration_bp)

    toolbar = DebugToolbarExtension(app)

    return app
