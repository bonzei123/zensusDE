from flask import render_template, Blueprint, session, request, abort
from functions import is_valid_state, get_token, get_userdata, hash_prep
from forms.Zensus import ZensusForm
from database import Entry, State
from database.db import db
import datetime

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=["GET", "POST"])
def main():
    error = request.args.get('error', '')
    form = ZensusForm()
    if error:
        return "Error: " + error
    if request.args.get('state', ''):
        state = request.args.get('state', '')
        if not is_valid_state(state):
            abort(403)
        code = request.args.get('code')
        access_token = get_token(code)
        session['access_token'] = access_token
        session['state'] = state
        name = get_userdata(access_token)['name']
        msg = '<p>Sooo, dann mal viel Spaß beim Ausfüllen!</p>'
        return render_template('main.html', name=name, form=form, msg=msg)
    if 'access_token' in session:
        user_agent = request.headers.get('User-Agent')
        user_ip = request.remote_addr
        userdata = get_userdata(session['access_token'])
        created = userdata['created']
        userid = userdata['userid']
        name = userdata['name']
        browser_hash = hash_prep(user_agent, user_ip)
        user_hash = hash_prep(name, userid)
        chk_browser_hash = db.session.query(Entry).filter(Entry.hash == browser_hash).first()
        chk_user_hash = db.session.query(Entry).filter(Entry.userhash == user_hash).first()
        if chk_browser_hash or chk_user_hash:
            msg = '<p>Sorrüüüü, du hast leider irgendwie schon dran teilgenommen... 👉👈</p>'
            return render_template('main.html', msg=msg)
        if form.validate_on_submit():
            schuld = form.schuld.data
            schuldtext = form.schuld.choices[int(form.schuld.data)-1][1]
            if not chk_browser_hash and not chk_user_hash:
                db.session.add(Entry(userhash=user_hash,
                                     hash=browser_hash,
                                     created=datetime.datetime.fromtimestamp(created),
                                     schuld=schuld))
                db.session.query(State).filter_by(state=session['state']).delete()
                one_hour = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
                db.session.query(State).filter(State.timestamp > one_hour).delete()
                db.session.query()
                db.session.commit()
            msg = '<p>Danke schön! Gut zu wissen, dass ' + schuldtext + ' Schuld hat.</p>'
            return render_template('main.html', msg=msg)
    msg = '<a href="%s" class="btn btn-danger">Authentifiziere dich mit Reddit!</a>' % make_authorization_url()
    return render_template('main.html', msg=msg)
