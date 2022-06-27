import os, shutil
from Intectainment import app, db
from Intectainment.datamodels import Channel, User
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif", "bmp", "svg", "ico"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def create_subfolder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def deleteImage(user: User):
    if user.icon_extension:
        source_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "usr/",
            str(user.username) + user.icon_extension,
        )
        user.icon_extension = None
        if os.path.exists(source_path):
            os.remove(source_path)
        user.reload()


def softImageDelete(user: User):
    if user.icon_extension:
        source_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "usr/",
            str(user.username) + "." + user.icon_extension,
        )
        if os.path.exists(source_path):
            os.remove(source_path)


def softImageDelete(channel: Channel):
    if channel.icon_extension:
        source_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "c/",
            str(channel.id) + "." + channel.icon_extension,
        )
        if os.path.exists(source_path):
            os.remove(source_path)


def move_images(userid, postid):
    source_path = os.path.join(app.config["UPLOAD_FOLDER"], "usr/tmp", str(userid))
    if os.path.exists(source_path):
        destination_path = app.config["UPLOAD_FOLDER"]
        shutil.move(source_path, destination_path)
        os.rename(
            os.path.join(app.config["UPLOAD_FOLDER"], str(userid)),
            os.path.join(app.config["UPLOAD_FOLDER"], str(postid)),
        )
        source_path = os.path.join(app.config["UPLOAD_FOLDER"], str(postid))
        destination_path = os.path.join(app.config["UPLOAD_FOLDER"], "p", str(postid))
        shutil.move(source_path, destination_path)


def upload_image(name="", folder="c", subfolder="", type=""):
    if "file" not in request.files:
        if "img_config" not in request.form:
            flash("Es wurde kein Bild zum hochladen ausgewählt!")
            return redirect(request.url)
        else:
            if folder == "c":
                target = Channel.query.filter_by(id=int(name)).first()
            elif folder == "usr":
                target = User.getCurrentUser()
            else:
                flash("Unbekannter Fehler")
                redirect(request.url)

            target.img_xPos = int(float(request.form["range_x"]) * 1000)
            target.img_yPos = int(float(request.form["range_y"]) * 1000)
            target.img_zoom = int(float(request.form["range_size"]) * 1000)

            if folder == "usr":
                target.reload()
            else:
                db.session.add(target)
                db.session.commit()

            flash("Einstellungen wurden übernommen!")
            flash(
                "Hinweis: Du kannst das Pop-up schließen und nachdem du deine Browserseite neu geladen hast, kannst du auch das neue Profilbild sehen."
            )
            return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("Es wurde kein gültiges Bild zum hochladen ausgewählt!")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if name != "":
            filename = name + "." + get_extension(file.filename)

        profile = None
        if folder == "c":
            channel = Channel.query.filter_by(id=int(name)).first()
            softImageDelete(channel)
            channel.icon_extension = get_extension(file.filename)
            db.session.add(channel)
            db.session.commit()
            profile = "c"
        elif folder == "usr":
            user = User.query.filter_by(id=int(name)).first()
            softImageDelete(user)
            user.icon_extension = get_extension(file.filename)
            user.reload()
            profile = "usr"

        create_subfolder(os.path.join(app.config["UPLOAD_FOLDER"], folder, subfolder))
        file.save(
            os.path.join(app.config["UPLOAD_FOLDER"], folder, subfolder, filename)
        )

        path = None
        if type:
            path = url_for(
                "display_image_posts", type=type, post_id=subfolder, filename=filename
            )
        else:
            path = url_for("display_image_", type=folder, filename=filename)

        return render_template("img/upload.html", path=path, type=type, profile=profile)
    else:
        flash("Unzulässige Dateiendung!")
        flash(
            "Hinweis: Zulässige Dateiendungen sind: *.png, *.jpg, *.jpeg, *.gif, *.bmp, *.svg, *.ico"
        )
        return redirect(request.url)


def display_image(folder, filename):
    return redirect(
        url_for("static", filename="img/" + folder + "/" + filename), code=301
    )
