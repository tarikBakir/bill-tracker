from flask_login import UserMixin
from database import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    session_token = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), db.ForeignKey('accounts.email'), nullable=False)
    postalcode = db.Column(db.String(100), db.ForeignKey('addresses.postal_code'), nullable=False)
    notification = db.relationship('Notification', backref='users')

    def get_id(self):
        # unicode(self.session_token)
        return self.session_token
