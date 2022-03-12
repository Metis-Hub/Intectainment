from functools import wraps
from flask import session, render_template
from Intectainment.datamodels import User

def login_required(f):
    """Wrapper function to ensure a logged in user with certain permissions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if User.isLoggedIn():
            return f(*args, **kwargs)
        else:
            return render_template("main/login.html", force=True)
    return decorated_function