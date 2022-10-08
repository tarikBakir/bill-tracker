from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length, Email


class LoginForm(Form):
    email = StringField('email', validators=[InputRequired(), Length(1, 100), Email()])
    password = PasswordField('password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

    def validate_on_submit(self):
        return True
