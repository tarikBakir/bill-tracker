from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
from models.account import Account


class changePasswordFrom(Form):
    currentPassword = PasswordField('password', validators=[InputRequired()])
    newPassword1 = PasswordField('password',
                                 validators=[InputRequired(), EqualTo('newPassword2', message='passwords must match.')])
    newPassword2 = PasswordField('confirm password', validators=[InputRequired()])
    submit = SubmitField('submit')

    def validate_on_submit(self):
        if not Form.validate(self):
            return False
        if self.currentPassword.data is None:
            return False
        if self.newPassword1.data is None:
            return False
        if self.newPassword2.data is None:
            return False

        return True
