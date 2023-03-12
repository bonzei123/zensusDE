from database import db
import datetime


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
