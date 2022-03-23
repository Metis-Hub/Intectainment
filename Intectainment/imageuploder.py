import os, urllib.request, shutil
from Intectainment.app import app
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif", "bmp", "svg", "ico"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def create_subfolder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def move_images(userid, postid):
    source_path = os.path.join(app.config["UPLOAD_FOLDER"], "usr/tmp", str(userid))
    destination_path = app.config["UPLOAD_FOLDER"]
    shutil.move(source_path, destination_path)
    os.rename(os.path.join(app.config["UPLOAD_FOLDER"], str(userid)), os.path.join(app.config["UPLOAD_FOLDER"], str(postid)))
    source_path = os.path.join(app.config["UPLOAD_FOLDER"], str(postid))
    destination_path = os.path.join(app.config["UPLOAD_FOLDER"], "p", str(postid))
    shutil.move(source_path, destination_path)

def upload_image(name="", folder="c", subfolder="", type=""):
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("No Image is selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if name != "":
            filename = name + "." + get_extension(file.filename)
        create_subfolder(os.path.join(app.config["UPLOAD_FOLDER"], folder, subfolder))
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], folder, subfolder, filename))
        if type != "":
            return render_template("img/upload.html", path="http://" + app.config["SERVER_NAME"] + "/img/" + type + "/" + subfolder + "/" + filename)
        else:
            return render_template("img/upload.html")
    else:
        flash("Allowed image types are -> png, jpg, jpeg, gif, bmp, svg, ico")
        return redirect(request.url)

def display_image(folder, filename):
    return redirect(url_for("static", filename="img/" + folder + "/" + filename), code=301)