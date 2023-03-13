from database.db import db
from database import Admin


def chk_admin(userhash):
    ret = False
    if db.session.query(Admin).filter(Admin.userhash == userhash).first():
        ret = True
    return ret
