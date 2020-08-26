import os
import sys

import connexion
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

connexian_app = connexion.App(__name__, specification_dir=basedir)

app = connexian_app.app

sqlite_url = "sqlite:////" + os.path.join(basedir, "Second.db")
mysql_url = "mysql+pymysql://root:root_pass@172.17.0.2/tolkuchka"

app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["WTF_CSRF_SECRET_KEY"] = 'SKJDFHG8FY4GFLJKEDfodji'
app.config["SECRET_KEY"] = 'liuh498hfkmsdnf0984gfD'
app.config["TEMPLATES_AUTO_RELOAD"] = True
sys.setrecursionlimit(300)

# Settings application
DAYS_SHOW_AD = 60


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


db = SQLAlchemy(app)
lm = LoginManager(app)
ma = Marshmallow(app)
bc = Bcrypt(app)

lm.login_view = '.login'
