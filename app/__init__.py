from flask import Flask, current_app
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_mail import Mail
from flask_limiter.util import get_remote_address


login_manager = LoginManager()  # Create an instance of LoginManager
bcrypt = Bcrypt()
db = SQLAlchemy() # Create an instance of SQLAlchemy orm


limiter = Limiter(  # initialize rate limiter with universal limits
        key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
    )

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize the db object with the app



    login_manager.init_app(app)  # and initialize it with the app
    login_manager.login_view = 'login'



    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.registration import bp as registration_bp
    app.register_blueprint(registration_bp)

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'],
                    app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

    return app
