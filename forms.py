from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp

from models import User, UserProfile, Address, SocialProfile, EducationHistory, WorkExperience, Skill

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired(), Length(min=10, max=15)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    street_address = StringField('Street Address', validators=[Length(max=100)])
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    zip_code = StringField('Zip Code', validators=[Length(max=10)])
    country = StringField('Country', validators=[Length(max=50)])
    password = PasswordField('Password',
        validators=[
        DataRequired(),
        Length(min=8,max=30),
        Regexp(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
            message="Password must contain uppercase, lowercase, digits, and special characters."
            )
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password'),
            Length(min=8,max=30)
        ]
    )


    bio = TextAreaField('Bio', validators=[Length(max=300)])
    hobbies = TextAreaField('Hobbies', validators=[Length(max=200)])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    street_address = StringField('Street Address', validators=[Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    hobbies = StringField('Hobbies', validators=[Length(max=200)])
    bio = TextAreaField('Bio', validators=[Length(max=300)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    street_address = StringField('Street Address', validators=[Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    hobbies = StringField('Hobbies', validators=[Length(max=200)])
    bio = TextAreaField('Bio', validators=[Length(max=300)])
    submit = SubmitField('Update Profile')
