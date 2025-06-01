import uuid
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_uuid):
    return User.query.get(uuid.UUID(user_uuid))

class Address(db.Model):
    __tablename__ = 'address'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)    # This will be set to user.id
    street_address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)  # This will be set to user.id
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.Text, nullable=True)

class SocialProfile(db.Model):
    __tablename__ = 'social_profile'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)  # This will be set to user.id
    platform = db.Column(db.String(50), nullable=False)
    profile_url = db.Column(db.String(200), nullable=False)

class EducationHistory(db.Model):
    __tablename__ = 'education_history'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)  # This will be set to user.id
    institution_name = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    graduation_date = db.Column(db.Date, nullable=True)

class WorkExperience(db.Model):
    __tablename__ = 'work_experience'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)  # This will be set to user.id
    company_name = db.Column(db.String(100), nullable=False)
    position_title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

class Skill(db.Model):
    __tablename__ = 'skill'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, primary_key=True)  # This will be set to user.id
    skill_name = db.Column(db.String(50), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Relationships
    address = db.relationship('Address', backref='User', uselist=False, cascade="all, delete-orphan")
    social_profiles = db.relationship('SocialProfile', backref='user', lazy=True, cascade="all, delete-orphan")
    education_history = db.relationship('EducationHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    work_experience = db.relationship('WorkExperience', backref='user', lazy=True, cascade="all, delete-orphan")
    skills = db.relationship('Skill', backref='user', lazy=True, cascade="all, delete-orphan")
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)





# run this in an interactive python shell to create the database tables:
# from app import app, db
# with app.app_context():
#     db.create_all()

