from flask import Flask, request, abort, render_template
from flask_hashing import Hashing
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from uuid import uuid4
from forms import ZensusForm
import requests.auth
import urllib.parse
import os


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE')
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_DEFAULT_TIMEOUT'))
app.config['CACHE_DIR'] = os.getenv('CACHE_DIR')
hashing = Hashing(app)
db = SQLAlchemy(app)
cache = Cache(app)
with app.app_context():
    db.create_all()
    db.session.commit()


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), default='')
    hash = db.Column(db.String(), nullable=False)
    created = db.Column(db.DateTime)
    schuld = db.Column(db.String(), default='')


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
        name = get_userdata(access_token)['name']
        cache.set('name', name)
        created = get_userdata(access_token)['created']
        cache.set('created', created)
        h = hashing.hash_value(hashing.hash_value(user_agent), hashing.hash_value(user_ip))
        cache.set('h', h)
        chk_h = db.session.query(Entry).filter(Entry.hash == h).first()
        chk_n = db.session.query(Entry).filter(Entry.name == name).first()
        if not chk_h and not chk_n:
            msg = '<p>Sorrüüüü, du hast leider irgendwie schon dran teilgenommen... 👉👈</p>'
            return render_template('main.html', msg=msg)
        # Note: In most cases, you'll want to store the access token, in, say,
        # a session for use in other parts of your web app.
        msg = '<p>Sooo, dann mal viel Spaß beim Ausfüllen!</p>'
        return render_template('main.html', name=name, form=form, msg=msg)
    if form.validate_on_submit():
        schuld = form.schuld.data
        schuldtext = form.schuld.choices[int(form.schuld.data)][1]
        with app.app_context():
            db.session.add(Entry(state=cache.get('state'),
                                 name=cache.get('name'),
                                 hash=cache.get('h'),
                                 created=cache.get('created'),
                                 schuld=schuld))
            db.session.query()
            db.session.commit()
        msg = '<p>danke schön! Gut zu wissen, dass ' + schuldtext + ' Schuld hat.</p>'
        return render_template('main.html', msg=msg)
    msg = '<a href="%s" class="btn btn-danger">Authentifiziere dich mit Reddit!</a>' % make_authorization_url()
    return render_template('main.html', msg=msg)


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
