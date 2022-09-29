import datetime

from database import db


class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.String(100))
    paid = db.Column(db.Boolean)
    amount = db.Column(db.Float)
    createDate = db.Column(db.Date, default=datetime.datetime.utcnow)
    modifiedDate = db.Column(db.Date, default=datetime.datetime.utcnow)
    dueDate = db.Column(db.Date, default=datetime.datetime.utcnow)
    companyId = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    categoryId = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
