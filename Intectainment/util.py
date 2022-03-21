from functools import wraps
from flask import session, render_template
from Intectainment.datamodels import User

def login_required(f, permission=User.PERMISSION.USER):
    """Wrapper function to ensure a logged in user with certain permissions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if User.isLoggedIn():
            if not permission or User.getCurrentUser().permission >= permission:
                return f(*args, **kwargs)
            else:
                #TODO
                return "zu geringe berechtigung"
        else:
            return render_template("main/login.html", force=True)
    return decorated_function

def admin_required(f):
    return login_required(f, User.PERMISSION.ADMIN)