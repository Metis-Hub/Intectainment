from flask import render_template, send_from_directory, request, redirect, url_for, session
import os

from Intectainment.app import app
from Intectainment.database.models import User

@app.route("/")
def mainPage():
	return render_template("main/start.html")

@app.route("/home")
def home():
	if not User.isLoggedIn():
		return redirect(url_for("login"))
	else:
		return render_template("main/home.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
	if User.isLoggedIn():
		return redirect(url_for("home"))

	if request.method == "GET":
		return render_template("main/login.html")
	elif request.method == "POST":
		if "username" and "password" in request.form:
			if User.logIn(request.form["username"], request.form["password"]):
				#success
				return redirect(url_for("home"))
			else:
				#failed login
				return redirect("?badLogin=1")
		else:
			#form nicht ausgefüllt
			pass

@app.route("/logout", methods = ["POST"])
def logout():
	User.logOut()
	pass



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