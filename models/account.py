from database import db
from werkzeug.security import generate_password_hash, check_password_hash


# UserMixin we pass for User model because its have a method that make flask login works

class Account(db.Model):
    __tablename__ = 'accounts'
    email = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    user = db.relationship('User', backref='accounts')
    notification = db.relationship('Notification', backref='accounts')
    account_preferences = db.relationship('Account_Preference', backref='accounts')


    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
