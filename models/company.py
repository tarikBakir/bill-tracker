from database import db


class Company(db.Model):
    __tablename__ = 'companies'
    code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phonenumber = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    bill = db.relationship('Bill', backref='companies')
