from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length


class LoginForm(Form):
    password = PasswordField('password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

    def validate_on_submit(self):
        return True
