import os
from flask import (
    render_template,
    send_from_directory,
    request,
    redirect,
    url_for,
    Blueprint,
    flash,
)
from sqlalchemy import desc

from Intectainment import app, db
from Intectainment.datamodels import User, Post, Channel
from Intectainment.util import login_required
from Intectainment.images import upload_image, display_image

gui: Blueprint = Blueprint("gui", __name__)
ap: Blueprint = Blueprint("interface", __name__, url_prefix="/interface")

# reset user timeout
@gui.before_request
def before_request():
    User.resetTimeout()


##### Home/Start ######
@gui.route("/")
def start():
    return render_template("main/start.html", user=User.getCurrentUser())


@gui.route("/home")
def home():
    return render_template("main/home.html", user=User.getCurrentUser())


@gui.route("/home/dashboard")
@login_required
def dashboard():
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    favs = (
        Post.query.filter(
            Post.channel_id.in_(
                [
                    subscription.id
                    for subscription in User.getCurrentUser().getSubscriptions().all()
                ]
            )
        )
        .order_by(desc(Post.creationDate))
        .paginate(page_num, 10, error_out=False)
    )
    return render_template(
        "main/home/dashboard.html", user=User.getCurrentUser(), favs=favs
    )


@gui.route("/home/discover")
def discover():
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    channels = Channel.query.filter(
        Channel.name.like(f"%{request.args.get('channel', '')}%")
    ).paginate(per_page=20, page=page_num, error_out=False)
    return render_template(
        "main/home/discover.html", user=User.getCurrentUser(), channels=channels
    )


@gui.route("/home/favorites")
@login_required
def favorites():
    return render_template(
        "main/home/favboard.html",
        user=User.getCurrentUser(),
        favs=User.getCurrentUser().getFavoritePosts().all(),
    )


##### Access Points #####
@ap.route("/user/login", methods=["POST"])
def login():
    """login access point"""
    if User.isLoggedIn():
        return redirect(request.form.get("redirect") or request.referrer)

    if request.method == "POST":
        if "username" and "password" in request.form:
            if User.logIn(request.form["username"], request.form["password"]):
                # success
                return redirect(request.form.get("redirect") or request.referrer)
            else:
                # failed login
                url = request.referrer
                if "?failedLogin=1" not in url:
                    url += "?failedLogin=1"
                return redirect(url)
        else:
            # form nicht ausgefüllt
            return redirect(request.referrer)


@ap.route("/user/logout", methods=["POST"])
def logout():
    """logout access point"""
    User.logOut()
    return redirect(url_for("gui.start"))


##### Images #####
@app.route("/upload/<type>/<id>/")
@login_required
def upload_form(type, id):
    return render_template("img/upload.html")


@app.route("/upload/<type>/<id>/", methods=["POST"])
@login_required
def upload_image_r(type, id):
    if type == "tmp":
        return upload_image(folder="usr/tmp/", subfolder=id, type=type)
    elif type == "c" or type == "usr":
        return upload_image(folder=type, name=id)
    elif type == "p":
        return upload_image(folder=type, subfolder=id, type=type)
    return


@app.route("/img/<type>/<filename>")
def display_image_(type, filename):
    return display_image(type, filename)


@app.route("/img/<type>/<post_id>/<filename>")
def display_image_posts(type, post_id, filename):
    if type == "tmp":
        return display_image("usr/tmp/" + post_id, filename)
    if type == "p" or type == "usr":
        return display_image(type + "/" + post_id, filename)


# Import other routing files
from Intectainment.webpages import channelsCategories


app.register_blueprint(ap)
app.register_blueprint(gui)


##### Favicon #####
@app.route("/favicon.ico")
def getIcon():
    return send_from_directory(
        os.path.join(app.root_path, "webpages/static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


##### Errors #####
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/error_404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/error_500.html"), 500
