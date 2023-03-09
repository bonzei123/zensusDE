from flask import Flask, request
import praw

app = Flask(__name__)

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR CLIENT SECRET'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/lol')
def hello_world():  # put application's code here
    return 'lololol'


if __name__ == '__main__':
    app.run()
