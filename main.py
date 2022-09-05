from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
main = Flask(__name__)
main.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite3'
db = SQLAlchemy(main)




class Company(db.Model):
    __tablename__ = 'company'
    code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phoneNumber = db.Column(db.Integer)
    mail = db.Column(db.String(100), unique=True)
    bill = db.relationship('Bill', backref='Company')



class Bill(db.Model):
    __tablename__ = 'bill'
    code = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.String(100))
    paid = db.Column(db.String(3))
    createDate = db.Column(db.Date)
    modifiedDate = db.Column(db.Date)
    dueDate = db.Column(db.Date)
    CompanyCode = db.Column(db.Integer, db.ForeignKey('company.code'), nullable=False)
    categoryID = db.Column(db.Integer, db.ForeignKey('category.ID'), nullable=False)

class Category(db.Model):
    __tablename__ = 'category'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    bill = db.relationship('Bill', backref='category')



class User(db.Model):
    __tablename__ = 'user'
    ID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    account_mail = db.Column(db.String(100), db.ForeignKey('account.mail'), nullable=False)
    postalCode = db.Column(db.String(100), db.ForeignKey('address.PostalCode'), nullable=False)
    notification = db.relationship('notification', backref='user')

class Account(db.Model):
    __tablename__ = 'account'
    mail = db.Column(db.String(100), primary_key=True)
    userName = db.Column(db.String(64), unique=True)
    Password = db.Column(db.String(128))
    user = db.relationship('User', backref='Account')
    Account_Preferences = db.relationship('User', backref='Account_Preferences')
    notification = db.relationship('notification', backref='account')

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.Password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.Password, password)


class Account_Preferences(db.Model):
    __tablename__ = 'Account Preferences'
    ID = db.Column(db.Integer, primary_key=True)
    account_mail = db.Column(db.String(100), db.ForeignKey('account.mail'))



class Notfication(db.Model):
   __tablename__ = 'notfication'
   code = db.Column(db.String(100), primary_key=True)
   description = db.Column(db.Text)
   date = db.Column(db.Date)
   type = db.Column(db.String(64))
   User_id = db.Column(db.Integer, db.ForeignKey('user.ID'), nullable=False)
   Account_mail = db.Column(db.String(100), db.ForeignKey('account.mail'), nullable=False)

class Address(db.Model):
    __tablename__ = 'address'
    PostalCode = db.Column(db.String(100), primary_key=True)
    cityName = db.Column(db.String(100))
    user = db.relationship('User', backref='address')
