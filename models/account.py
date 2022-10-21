from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, \
    fresh_login_required, UserMixin, login_manager


# UserMixin we pass for User model because its have a method that make flask login works

class Account(UserMixin, db.Model):
    __tablename__ = 'accounts'
    email = db.Column(db.String(128), primary_key=True)
    password_hash = db.Column(db.String(128))
    user = db.relationship('User', backref='accounts')
    notification = db.relationship('Notification', backref='accounts')
    account_preferences = db.relationship('Account_Preference', backref='accounts')

    # Custom property getter
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # Custom property setter
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.email)

    def get_password(self):
        return self.password_hash

    # def is_authenticated(self):
    #   return True

    def __repr__(self):
        return '<Email %r>' % self.email
