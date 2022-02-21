import html
import os
from flask import render_template, send_from_directory, request, redirect, url_for, session, Blueprint, Markup

from Intectainment.app import app
from Intectainment.database.models import User

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
	user = User.query.filter_by(username=search).first()
	return render_template("main/user/userProfile.html", searchUser=user)


@gui.route("/profileSearch", methods=["GET"])
def profileSearch():
	search = request.args.get('username')
	query = User.query.filter(User.username.like(f"%{search}%"))

	return render_template("main/user/profileSearch.html", users=query.all())

@gui.route("/showPost/<fileName>")
def md(fileName):
	import markdown
	with open('Intectainment/webpages/posts/'+fileName+".txt", 'r') as f:
		mdIn = f.read()
		html = markdown.markdown(mdIn)
		print(fileName)
	htmlOut = Markup(html)
	return render_template("main/markdownTest.html", post=htmlOut)

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


app.register_blueprint(ap)
app.register_blueprint(gui)

#Import Admin Interface
import Intectainment.webpages.admin



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