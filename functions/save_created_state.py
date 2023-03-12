from database import db, State


def save_created_state(state):
    db.session.add(State(state=state))
    db.session.commit()
