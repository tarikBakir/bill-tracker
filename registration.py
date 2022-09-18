from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo
import email_validator
from models.account import Account


class RegistrationForm(Form):
    email = StringField('Email', validators=[InputRequired(), Length(1, 100), Email()])
    firstName = StringField('FirstName',
                            validators=[InputRequired(),
                                        Length(max=64, message='Your first name is too many characters.'),
                                        Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                               'FirstName must have only letters')])
    lastName = StringField('LastName',
                           validators=[InputRequired(),
                                       Length(max=64, message='Your first name is too many characters.'),
                                       Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                              'FirstName must have only letters')])
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
