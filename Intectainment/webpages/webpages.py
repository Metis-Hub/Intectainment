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
@gui.route("/channels", methods=["GET"])
def channelSearch():
	name = request.args.get('channelname')

	page_num = 1
	try:
		page_num = int(request.args.get("page"))
	except (ValueError, TypeError):
		pass

	channels = Channel.query.filter(Channel.name.like(f"%{name}%")).paginate(per_page=20, page=page_num, error_out=False)
	return render_template("main/channel/channelSearch.html", channels=channels)

@gui.route("/c/<channel>")
@gui.route("/channel/<channel>")
def channelView(channel):
	channel = Channel.query.filter_by(name=channel).first()
	return render_template("main/channel/channelView.html", channel=channel)

@gui.route("/c/<channel>/settings")
@gui.route("/channel/<channel>/settings", methods=["GET", "POST"])
def channelSettings(channel):
	channel = Channel.query.filter_by(name=channel).first()

	return render_template("main/channel/channelSettings.html", channel=channel, categories=Category.query.all())



##### Kategorien #####
@gui.route("/categories", methods=["GET"])
def viewCategories():
	page_num = 1
	try:
		page_num = int(request.args.get("page"))
	except (ValueError, TypeError):
		pass

	categories = Category.query.paginate(per_page=20, page=page_num, error_out=False)
	return render_template("main/category/categoryList.html", categories = categories)

@gui.route("/categories/new", methods=["GET", "POST"])
def createCategory():
	if request.method == "GET":
		return render_template("main/category/categoryCreation.html")
	elif request.method == "POST":
		name = request.form.get("name")
		if name:
			if Category.query.filter_by(name=name).count() > 0:
				#exists allready
				return render_template("main/category/categoryCreation.html", error="exists", message="Die Kategorie existiert bereits")
				pass
			else:
				category = Category(name=name)
				db.session.add(category)
				db.session.commit()

				return render_template("main/category/categoryCreation.html", message="Kategorie erfolgreich erstellt")
				pass
		else:
			return render_template("main/category/categoryCreation.html", error="noargument", message="Name als Argument benötigt")


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