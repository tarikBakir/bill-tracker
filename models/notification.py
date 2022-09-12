from database import db


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    type = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_email = db.Column(db.String(100), db.ForeignKey('accounts.email'), nullable=False)
