from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from models.user import User

class UserEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20)
    ])
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=256)
    ])
    password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Update')
    
    def validate_email(self, email):
        """Validate that email is unique when changed"""
        user = User.query.filter_by(email=email.data).first()
        if user and (not hasattr(self, 'id') or user.id != self.id.data):
            raise ValidationError('This email is already in use by another account.')

class UserSearchForm(FlaskForm):
    query = StringField('Search Users', validators=[DataRequired()])
    submit = SubmitField('Search')