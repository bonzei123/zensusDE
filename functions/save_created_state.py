from database.db import db
from database import State


def save_created_state(state):
    db.session.add(State(state=state))
    db.session.commit()
