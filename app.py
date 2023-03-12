from flask import Flask
from blueprints.main import main
from database.db import db


app = Flask(__name__)
app.register_blueprint(main)


with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
