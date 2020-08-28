from flask import redirect, url_for
from flask_login import login_required, logout_user, login_user, current_user

from config import db, bc
from forms import LoginForm
from models import User


def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user:
            if bc.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.merge(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("home"))
    return redirect(url_for('.user_login'))


@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.merge(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('.user_login'))
