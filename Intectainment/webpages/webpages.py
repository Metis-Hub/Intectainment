import os
from flask import render_template, send_from_directory, request, redirect, url_for, session, Blueprint, jsonify

from Intectainment.app import app, db
from Intectainment.database.models import User, Channel, Category

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
	if not User.isLoggedIn():
		return redirect(url_for("interface.login"))
	else:
		return render_template("main/home.html")

@gui.route("/dashboard")
def dashboard():
	return render_template("main/dashboard.html")
	pass

##### Profile #####
@gui.route("/profile/<search>")
@gui.route("/p/<search>")
def profile(search):
	# TODO: paginate query result

	user = User.query.filter_by(username=search).first()
	return render_template("main/user/userProfile.html", searchUser=user)


@gui.route("/profileSearch", methods=["GET"])
def profileSearch():
	search = request.args.get('username')
	query = User.query.filter(User.username.like(f"%{search}%"))

	return render_template("main/user/profileSearch.html", users=query.all())


##### Kanäle #####
@gui.route("/channel/<search>")
@gui.route("/c/<search>")
def channelView(search):
	channel = Channel.query.filter_by(name=search).first()
	return render_template("main/channel/channelView.html", channel=channel)


@gui.route("/channels", methods=["GET"])
def channelSearch():
	#TODO: paginate query result

	name, category = request.args.get('channelname'), request.args.get('category')
	channels = []
	if name:
		channels = Channel.query.filter(Channel.name.like(f"%{name}%")).all()
	elif category:
		channels = Category.query.filter_by(name=category).first()
		if channels:
			channels = channels.channels

	print(channels)
	return render_template("main/channel/channelSearch.html", channels=channels, categories=Category.query.all())

#TODO: remove
@gui.route("/test")
def test():
	return render_template("main/LoginLogoutTest.html", user=User.getCurrentUser())

##### Access Points #####
@ap.route("/user/login", methods = ["POST"])
def login():
	"""login access point"""
	if User.isLoggedIn():
		return redirect(request.form.get("redirect") or url_for("home"))

	if request.method == "POST":
		if "username" and "password" in request.form:
			if User.logIn(request.form["username"], request.form["password"]):
				#success
				return redirect(request.form.get("redirect") or url_for("home"))
			else:
				#failed login
				return redirect(request.form.get("returnTo") or url_for("start"))
		else:
			#form nicht ausgefüllt
			return redirect(request.form.get("returnTo") or url_for("start"))

@ap.route("/user/logout", methods = ["POST"])
def logout():
	"""logout access point"""
	User.logOut()
	return redirect(url_for("gui.start"))

#Import Admin Interface
import Intectainment.webpages.admin
import Intectainment.webpages.RestInterface

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