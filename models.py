# run this in an interactive python shell to create the database tables:
# from app import app, db
# with app.app_context():
#     db.create_all()

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

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

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




# Define deleted user tables for soft delete
class DeletedUser(UserMixin, db.Model):
    __tablename__ = 'deleted_user'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    # Relationships
    address = db.relationship('DeletedAddress', backref='DeletedUser', uselist=False, cascade="all, delete-orphan")
    social_profiles = db.relationship('DeletedSocialProfile', backref='DeletedUser', lazy=True, cascade="all, delete-orphan")
    education_history = db.relationship('DeletedEducationHistory', backref='DeletedUser', lazy=True, cascade="all, delete-orphan")
    work_experience = db.relationship('DeletedWorkExperience', backref='DeletedUser', lazy=True, cascade="all, delete-orphan")
    skills = db.relationship('DeletedSkill', backref='DeletedUser', lazy=True, cascade="all, delete-orphan")
    profile = db.relationship('DeletedUserProfile', backref='DeletedUser', uselist=False, cascade="all, delete-orphan")

class DeletedAddress(db.Model):
    __tablename__ = 'deleted_address'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)    # This will be set to deleted_user.id
    street_address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)

class DeletedUserProfile(db.Model):
    __tablename__ = 'deleted_user_profile'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)  # This will be set to deleted_user.id
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.Text, nullable=True)

class DeletedSocialProfile(db.Model):
    __tablename__ = 'deleted_social_profile'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)  # This will be set to deleted_user.id
    platform = db.Column(db.String(50), nullable=False)
    profile_url = db.Column(db.String(200), nullable=False)

class DeletedEducationHistory(db.Model):
    __tablename__ = 'deleted_education_history'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)  # This will be set to deleted_user.id
    institution_name = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    graduation_date = db.Column(db.Date, nullable=True)

class DeletedWorkExperience(db.Model):
    __tablename__ = 'deleted_work_experience'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)  # This will be set to deleted_user.id
    company_name = db.Column(db.String(100), nullable=False)
    position_title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

class DeletedSkill(db.Model):
    __tablename__ = 'deleted_skill'
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('deleted_user.id'), nullable=False, primary_key=True)  # This will be set to deleted_user.id
    skill_name = db.Column(db.String(50), nullable=False)



def soft_delete_generic(user_model, user_id, deleted_model_map):
    """
    Generic function to handle soft deletion for a given model and its related models.

    :param user_model: The SQLAlchemy model class of the original table.
    :param user_id: The ID of the record that needs to be deleted.
    :param deleted_model_map: A dictionary mapping original models to their corresponding deleted models.
    """
    # Fetch the instance

    user_instance = db.session.query(user_model).get(uuid.UUID(user_id))
    if not user_instance:
        return None, f"{user_model.__name__} not found"

    # Inspect the columns of the model
    inspector = db.inspect(user_model)
    columns = [column.key for column in inspector.columns]

    # Create a new instance of the corresponding deleted model with the same data
    deleted_user_model = deleted_model_map.get(user_model, None)
    if deleted_user_model is None:
        raise ValueError(f"Deleted model not found for {user_model.__name__}")

    # Copy the data to the deleted model
    deleted_instance = deleted_user_model()
    for column in columns:
        setattr(deleted_instance, column, getattr(user_instance, column))

    db.session.add(deleted_instance)

    # Handle related models (one-to-many relationships)
    relationships = inspector.relationships
    for rel_name, relationship in relationships.items():
        if relationship.uselist:  # One-to-many relationships
            related_instances = getattr(user_instance, rel_name)
            deleted_related_model = deleted_model_map.get(relationship.mapper.entity, None)

            for instance in related_instances:
                new_deleted_instance = deleted_related_model()
                for column in columns:
                    setattr(new_deleted_instance, column, getattr(instance, column))
                db.session.add(new_deleted_instance)
        else:  # One-to-one relationships
            related_instance = getattr(user_instance, rel_name)
            if related_instance is not None:
                deleted_related_model = deleted_model_map.get(relationship.mapper.entity, None)
                new_deleted_instance = deleted_related_model()
                for column in columns:
                    setattr(new_deleted_instance, column, getattr(related_instance, column))
                db.session.add(new_deleted_instance)

    # Commit the copied data
    db.session.commit()

    # Delete the original record
    db.session.delete(user_instance)
    db.session.commit()

# Example of calling the soft_delete_generic function
#
# deleted_model_map = {
#     User: DeletedUser,
#     Address: DeletedAddress,
#     SocialProfile: DeletedSocialProfile,
#     EducationHistory: DeletedEducationHistory,
#     WorkExperience: DeletedWorkExperience,
#     Skill: DeletedSkill,
#     UserProfile: DeletedUserProfile
# }
# soft_delete_generic(User, 'some-user-id', deleted_model_map)
#

