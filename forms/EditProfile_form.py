from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from flask import flash, request
from models.account import Account


class editProfileForm(Form):
    firstname = StringField('firstname',
                            validators=[InputRequired(),
                                        Length(max=64, message='Your first name is too many characters.'),
                                        Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                               'FirstName must have only letters')])
    lastname = StringField('lastname',
                           validators=[InputRequired(),
                                       Length(max=64, message='Your last name is too many characters.'),
                                       Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                              'FirstName must have only letters')])
    submit = SubmitField('update')

    def validate_on_submit(self):
        if not Form.validate(self):
            return False
        if self.firstname.data is None:
            self.firstname.errors.append('please insert your first name!')
            return False
        if self.lastname.data is None:
            self.lastname.errors.append('please insert your last name!')
            return False

        return True
