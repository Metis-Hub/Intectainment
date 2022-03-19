from ast import dump
from dbm import dumb
import os
from flask import render_template, send_from_directory, request, redirect, url_for, Blueprint, Markup

from Intectainment.app import app
from Intectainment.datamodels import Favorites, User, Channel

gui: Blueprint = Blueprint("gui", __name__)
ap: Blueprint = Blueprint("interface", __name__, url_prefix="/interface")

# reset user timeout
@gui.before_request
def before_request():
	User.resetTimeout()
	pass


##### Home/Start ######
@gui.route("/")
def start():
	return render_template("main/start.html", user=User.getCurrentUser())

@gui.route("/home")
def home():
	return render_template("main/home.html")
#	if not User.isLoggedIn():
#		return redirect(url_for("interface.login"))
#	else:
#h		return render_template("main/home.html")

@gui.route("/home/dashboard")
def dashboard():
	return render_template("main/home/dashboard.html")

@gui.route("/home/discover")
def discover():
	return render_template("main/home/discover.html", channels=Channel.query.paginate(per_page=20, page=1, error_out=False))

@gui.route("/home/userchannel")
def userchannel():
	return render_template("main/home/userchannel.html")

@gui.route("/home/favorites")
def favorites():
	dump(User.getCurrentUser())
	favorites = User.getFavoritePosts(User.getCurrentUser())
	return render_template("main/home/dashboard.html", favs=favorites)



##### Profile #####
@gui.route("/profile/<search>")
@gui.route("/p/<search>")
def profile(search):
	# TODO: paginate query result

	user = User.query.filter_by(username=search).first()
	return render_template("main/user/userProfile.html", searchUser=user)


@gui.route("/profiles", methods=["GET"])
def profileSearch():
	search = request.args.get('username')
	query = User.query.filter(User.username.like(f"%{search}%"))

	return render_template("main/user/profiles.html", users=query.all())

#TODO: remove
@gui.route("/test")
def test():
	return render_template("main/LoginLogoutTest.html", user=User.getCurrentUser())

##### Access Points #####
@ap.route("/user/login", methods = ["POST"])
def login():
	"""login access point"""
	if User.isLoggedIn():
		return redirect(request.form.get("redirect") or url_for("gui.home"))

	if request.method == "POST":
		if "username" and "password" in request.form:
			if User.logIn(request.form["username"], request.form["password"]):
				#success
				return redirect(request.form.get("redirect") or url_for("gui.home"))
			else:
				#failed login
				url = request.referrer
				if "?failedLogin=1" not in url:
					url += "?failedLogin=1"
				return redirect(url)
		else:
			#form nicht ausgefüllt
			return redirect(request.referrer)

@ap.route("/user/logout", methods = ["POST"])
def logout():
	"""logout access point"""
	User.logOut()
	return redirect(url_for("gui.start"))

#Import other routing files
from Intectainment.webpages import admin, channelsCategories, RestInterface


app.register_blueprint(ap)
app.register_blueprint(gui)


##### Favicon #####
@app.route("/favicon.ico")
def getIcon():
    return send_from_directory(os.path.join(app.root_path, 'webpages/static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

##### Errors #####
@app.errorhandler(404)
def page_not_found(e):
	return render_template("errors/error_404.html"), 404
	
@app.errorhandler(500)
def server_error(e):
	return render_template("errors/error_500.html"), 500