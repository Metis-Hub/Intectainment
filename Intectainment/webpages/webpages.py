import os
from flask import render_template, send_from_directory, request, redirect, url_for, Blueprint

from Intectainment.app import app, db
from Intectainment.datamodels import User, Post
from Intectainment.util import login_required
from Intectainment.imageuploder import upload_image, display_image

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
@login_required
def home():
	return render_template("main/home.html")

@gui.route("/dashboard")
def dashboard():
	return render_template("main/dashboard.html")

##### Profile #####
@gui.route("/profile/<search>")
@gui.route("/p/<search>")
def profile(search):
	user = User.query.filter_by(username=search).first()
	return render_template("main/user/userProfile.html", searchUser=user)


@gui.route("/profiles", methods=["GET"])
def profileSearch():
	search = request.args.get('username')
	query = User.query.filter(User.username.like(f"%{search}%"))

	return render_template("main/user/profileSearch.html", users=query.all())


@gui.route("/login", methods=["GET"])
def login():
	return render_template("main/login.html", redirect="gui.home")

#TODO: remove
@gui.route("/test")
def test():
	return render_template("main/LoginLogoutTest.html", user=User.getCurrentUser())

##### Access Points #####
@ap.route("/user/login", methods = ["POST"])
def login():
	"""login access point"""
	if User.isLoggedIn():
		return redirect(request.form.get("redirect") or request.referrer)

	if request.method == "POST":
		if "username" and "password" in request.form:
			if User.logIn(request.form["username"], request.form["password"]):
				#success
				return redirect(request.form.get("redirect") or request.referrer)
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

##### Images #####
@app.route("/upload/<type>/<id>/")
def upload_form(type, id):
	return render_template("img/upload.html")

@app.route("/upload/<type>/<id>/", methods=["POST"])
def upload_image_r(type, id):
	if type == "c" or type == "usr":
		return upload_image(folder=type, name=id)
	elif type == "p":
		return upload_image(folder=type, subfolder=id)
	return

@app.route("/img/<type>/<filename>")
def display_image_(type, filename):
	return display_image(type, filename)

@app.route("/img/p/<post_id>/<filename>")
def display_image_posts(post_id, filename):
	return display_image("p/" + post_id, filename)

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