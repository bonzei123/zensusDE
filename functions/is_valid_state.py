from database.db import db
from database import State


def is_valid_state(state):
    valid = False
    if db.session.query(State).filter_by(state=state).first():
        valid = True
    return valid
