from flask import render_template, send_from_directory
import os

from Intectainment.app import app
from Intectainment.database.models import User

@app.route("/")
def mainPage():
	return render_template("main/start.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
	# TODO
	User.LogIn("günter", "passwort")
	return "Hi"
	pass

@app.route("/logout", methods = ["POST"])
def logout():
	# TODO
	User.LogOut()
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