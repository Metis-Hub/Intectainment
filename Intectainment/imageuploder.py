import os, urllib.request
from Intectainment.app import app
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif", "bmp", "svg", "ico"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(folder="c", subfolder=""):
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("No Image is selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #os.path.join(os.path.dirname(__file__), self.CONTENTDIRECTORY, f"{self.channel_id}-{self.id}.md")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], folder, subfolder, filename))
        return render_template("img/upload.html", path=os.path.join(app.config["UPLOAD_FOLDER"], filename))
    else:
        flash("Allowed image types are -> png, jpg, jpeg, gif, bmp, svg, ico")
        return redirect(request.url)

def diplay_image(folder, filename):
    return redirect(url_for("static", filename="img/" + folder + "/" + filename), code=301)