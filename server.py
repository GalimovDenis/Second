from flask import render_template
from flask_login import login_required

import config
from forms import LoginForm
from models import User

connex_app = config.connexian_app

connex_app.add_api("openapi.yaml")


@config.lm.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (username) user to retrieve
    """
    return User.query.get(user_id)


@connex_app.route("/")
@login_required
def home():
    return render_template("home.html")


@connex_app.route("/login", methods=["GET"])
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


if __name__ == "__main__":
    connex_app.run(host="0.0.0.0", port=8080, debug=True)
