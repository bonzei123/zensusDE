from flask import Flask
from blueprints.main import main_blueprint
from database.db import db
from config.hashing import hashing


app = Flask(__name__)
app.register_blueprint(main_blueprint)
db.init_app(app)
hashing.init_app(app)


with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
