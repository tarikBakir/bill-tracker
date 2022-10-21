from flask_login import UserMixin
from database import db
from itsdangerous import Serializer
from flask import current_app


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(100), db.ForeignKey('accounts.email'), nullable=False)
    postalcode = db.Column(db.String(100), db.ForeignKey('addresses.postal_code'), nullable=True)
    notification = db.relationship('Notification', backref='users')
    bill = db.relationship('Bill', backref='users')

    def get_id(self):
        # unicode(self.session_token)
        return self.session_token


