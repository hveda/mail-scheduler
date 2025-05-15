"""Authentication forms for user registration and login."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import PasswordInput

from app.database.models.user import User


class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', widget=PasswordInput(),
                             validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', widget=PasswordInput(),
                              validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[Length(max=80)])
    last_name = StringField('Last Name', validators=[Length(max=80)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate that the username is not already in use."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Validate that the email is not already in use."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class UserEditForm(FlaskForm):
    """Form for editing user information."""

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=80)])
    last_name = StringField('Last Name', validators=[Length(max=80)])
    role = SelectField('Role', choices=[
        ('admin', 'Administrator'),
        ('user', 'Regular User'),
        ('guest', 'Guest User')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')


class PasswordChangeForm(FlaskForm):
    """Form for changing a user's password."""

    current_password = PasswordField('Current Password',
                                     validators=[DataRequired()])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(),
                                                 EqualTo('new_password')])
    submit = SubmitField('Change Password')
