from flask import render_template
from Intectainment.app import app

@app.route("/")
def mainPage():
    return render_template("main/start.html", argument="Hiiiiiii")








##### Errors #####
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/error_404.html"), 404
    
@app.errorhandler(500)
def server_error(e):
    return render_template("errors/error_500.html"), 500