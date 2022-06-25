import os, feedparser
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
from Intectainment.datamodels import User, Post, Channel, RSS
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


@gui.route("/rss")
def rss():
    feeds = RSS.query.all()

    for feed in feeds:
        url = feed.rss
        parsedFeed = feedparser.parse(url)

        readFeed = 0
        for entry in parsedFeed["entries"]:
            print(entry["title"])
            if str(entry["guid"]) == str(feed.guid):
                break
            readFeed += 1

        print(readFeed)

        feed.guid = parsedFeed["entries"][0]["guid"]
        for i in range(readFeed, 0, -1):
            # das für alle abonnierten channels
            channels = feed.channel_id

            for channel in channels:
                entry = parsedFeed["entries"][i]

                title = ""
                author = ""
                link = ""
                summary = ""
                description = ""
                pubDate = "Veröffentlichung: " + entry.published + "  \n"

                if "title" in entry:
                    title = "# " + entry["title"] + "\n"
                if "author" in entry:
                    author = "_von " + entry["author"] + "_  \n"
                if "link" in entry:
                    link = "[Link zum Artikel](" + entry["link"] + ")\n  \n"
                if "description" in entry:
                    description = entry["description"]
                elif "summary" in entry:
                    summary = entry["summary"]

                entryMd = title + pubDate + author + link + description + summary
                # adding post
                post = Post(
                    channel_id=channel, owner=User.query.filter_by(id=1).first()
                )
                db.session.add(post)
                db.session.commit()

                post.createFile()
                post.setContent(entryMd)

    return "done"


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
