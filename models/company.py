from database import db


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phoneNumber = db.Column(db.String(10))
    email = db.Column(db.String(100))
    bill = db.relationship('Bill', backref='companies')
