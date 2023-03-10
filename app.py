from flask import Flask, request, abort, render_template
from flask_hashing import Hashing
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from uuid import uuid4
from forms import ZensusForm
import requests.auth
import urllib.parse
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
hashing = Hashing(app)
db = SQLAlchemy(app)
cache = Cache(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(60), nullable=False)
    username_hash = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    age = db.Column(db.DateTime, nullable=False)
    schuld = db.Column(db.String(60), nullable=False)


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')


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
    cache.set('state', state)


def is_valid_state(state):
    valid = False
    if state == cache.get("state"):
        valid = True
    return valid


@app.route('/', methods=["GET", "POST"])
def main():
    error = request.args.get('error', '')
    form = ZensusForm()
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
        return render_template('main.html', user=get_userdata(access_token)['name'], form=form)
    if form.validate_on_submit():
        return render_template('main.html', choice=form.schuld.choices[int(form.schuld.data)][1])
    return render_template('main.html', link=make_authorization_url())


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


def get_userdata(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    ret = {'name': me_json['name'], 'created': me_json['created']}
    return ret


if __name__ == '__main__':
    app.run(debug=True, port=5000)
