from flask import Flask, request, abort, render_template
from flask_hashing import Hashing
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import requests.auth
import urllib.parse


app = Flask(__name__)
hashing = Hashing(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zensus_de:fg9wT11CO00sr6k0xbixbFiT5EipOhKT@dpg-cg501lfdvk4n2c1k14tg-a/zensus_de'
db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(60), nullable=False)
    hash = db.Column(db.String(64), nullable=False)


CLIENT_ID = 'MOFG59uULfGTfEeNSNxlbA'
CLIENT_SECRET = 'lhp6cBFRZs3AjDFlwDMB5FpM-uHZhw'
REDIRECT_URI = 'https://zensusde.onrender.com'
# REDIRECT_URI = 'http://127.0.0.1:5000/'


def base_headers():
    return {"User-Agent": "ZensusDE - der große r/de Zensus von /u/%s" % "bonzei"}


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass


def is_valid_state(state):
    return True


@app.route('/')
def main():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    if request.args.get('state', ''):
        state = request.args.get('state', '')
        if not is_valid_state(state):
            # Uh-oh, this request wasn't started by us!
            abort(403)
        code = request.args.get('code')
        access_token = get_token(code)
        user_agent = request.headers.get('User-Agent')
        user_ip = request.remote_addr
        h = hashing.hash_value(user_agent, salt=user_ip)
        # Note: In most cases, you'll want to store the access token, in, say,
        # a session for use in other parts of your web app.
        return render_template('main.html', user=get_username(access_token))
    text = '<a href="%s">Authenticate with reddit</a>'
    return text % make_authorization_url()


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]


def get_username(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    print(me_json)
    return me_json['name']


if __name__ == '__main__':
    app.run(debug=True, port=5000)
