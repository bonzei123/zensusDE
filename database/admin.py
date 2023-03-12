from database import db


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userhash = db.Column(db.String(), default='')
