from database import db


class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.String(100))
    paid = db.Column(db.String(3))
    createDate = db.Column(db.Date)
    modifiedDate = db.Column(db.Date)
    dueDate = db.Column(db.Date)
    companyCode = db.Column(db.Integer, db.ForeignKey('companies.code'), nullable=False)
    categoryID = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
