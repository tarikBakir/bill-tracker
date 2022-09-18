from database import db


class Account_Preference(db.Model):
    __tablename__ = 'account_preferences'
    id = db.Column(db.Integer, primary_key=True)
    account_email = db.Column(db.String(100), db.ForeignKey('accounts.email'))