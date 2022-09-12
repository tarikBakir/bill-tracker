from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from models.account import Account
from models.user import User
from database import db


class RegistrationForm(Form):
    email = StringField('Email', validators=[InputRequired(), Length(1, 100), Email()])
    username = StringField('Username',
                           validators=[InputRequired(), Length(max=64, message='Your username is too many characters.'),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters, ' 'numbers, dots or underscores')])
    password = PasswordField('password',
                             validators=[InputRequired(), EqualTo('password2', message='passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Register')

    def validate_email(self, field):
        if Account.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use')

    def validate_username(self, field):
        if Account.query.filter_by(username=field.data).first():
            raise ValidationError('username already in use')

    def validate_on_submit(self):
        return True