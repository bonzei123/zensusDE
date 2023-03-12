from database.db import db


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userhash = db.Column(db.String(), default='')
    hash = db.Column(db.String(), nullable=False)
    created = db.Column(db.DateTime)
    schuld = db.Column(db.String(), default='')
