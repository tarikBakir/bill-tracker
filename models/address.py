from database import db


class Address(db.Model):
    __tablename__ = 'addresses'
    postal_code = db.Column(db.String(100), primary_key=True)
    cityName = db.Column(db.String(100))
    user = db.relationship('User', backref='addresses')
