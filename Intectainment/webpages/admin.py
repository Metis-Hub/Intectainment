import Intectainment.images
from Intectainment.app import db
from Intectainment.webpages.webpages import gui
from Intectainment.datamodels import User, Channel, Post, Category
from Intectainment.util import admin_required

from flask import Blueprint, render_template, request, redirect, url_for, session, flash


admin: Blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@admin.before_request
@admin_required
def before_request():
    pass


@admin.route("/")
def main():
    return render_template("admin/main.html")

@admin.route("/<usrid>/edit", methods=["GET","POST"])
def edit_user(usrid):
    user = User.query.filter_by(id=usrid).first()
    if request.method == "POST":
        if "pw" and "new" and "ver_new" in request.form:
            if request.form["new"] != request.form["ver_new"]:
                flash("Neues Passwort stimmt nicht mit der Bestätigung des Neuens überein!")
            else:
                user.changePassword(request.form["new"])
                db.session.add(user)
                flash("Passwort wurde erfolgreich  geändert!")
        elif "txtname" and "name" in request.form:
            check_usr = User.query.filter_by(username=request.form["txtname"]).first()
            if check_usr and check_usr.name == request.form["txtname"]:
                flash("Benutzername ist bereits schon vergeben, wollen Sie aber dennoch einen anderen Namen angezeigt haben, so ändern Sie bitte Ihren Anzeignamen!")
            else:
                user.username = request.form["txtname"]
                db.session.add(user)
                flash("Benutzername wurde erfolgreich geändert!")
        elif "txtdispl_name" and "displ_name" in request.form:
            if request.form["txtdispl_name"] != user.username:
                user.displayname = request.form["txtdispl_name"]
            else:
                user.displayname = None
            db.session.add(user)
            flash("Anzuzeigender Name wurde erfolgreich geändert!")
        elif "submit_level" and "level" in request.form:
            user.permission = int(request.form["level"])
            db.session.add(user)
            flash("Zugriffslevel wurde erfolgreich geändert!")
        elif "del_image" in request.form:
            Intectainment.images.deleteImage(user)
            flash("Profilbild gelöscht!")

        db.session.commit()
    return render_template("admin/singleUserConfig.html", edit_user=user)

@admin.route("/user", methods=["GET","POST"])
def userconfig():
    if request.method == "GET":
        return render_template("admin/userConfig.html")
    elif request.method == "POST":
        post = request.form

        if post.get("createUser"):
            # all fields are filled
            if post.get("username") and post.get("email") and post.get("password"):

                #if username is not taken
                if User.query.filter_by(username=post.get("username")).first() is None:
                    user = User()
                    user.username = post.get("username")
                    user.email = post.get("email")
                    user.changePassword(post.get("password"))

                    db.session.add(user)
                    fail = False
                    try:
                        db.session.commit()
                    except:
                        fail = True
                    if not fail:
                        return render_template("admin/userConfig.html", createUser="success", userName=post.get("username"))
                    else:
                        return render_template("admin/userConfig.html", createUser="fail", error="SQL Fehler")
                    pass
                else:
                    #username taken
                    return render_template("admin/userConfig.html", createUser="fail", error="Benutzername existiert schon")
                    pass
                pass
            else:
                #nicht ausgefüllt
                pass
            pass
        elif post.get("queryUser"):
            users = User.query

            if post.get("queryname"):
                users = users.filter_by(username=post.get("queryname"))

            return render_template("admin/userConfig.html", users = users.all())
            #continue
            pass

        return redirect(url_for("gui.admin.userconfig"))
    pass

@admin.route("/setuphelp", methods= ["GET", "POST"])
def setup():
    if request.method == "POST":
        if request.form.get("createDefault"):
            user = User.query.one()

            for channelConfig in [("Intectainment", "Intectainment ist ein Infotainmentsystem"), ("SRZ-III", "Algorithmierung"), ("SRZ-IV", "Was weiß denn ich")]:
                channel = Channel(name=channelConfig[0], description=channelConfig[1])
                channel.owner = user
                db.session.add(channel)

            for i in range(100):
                channel = Channel(name=f"Kanal{i}", description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.")
                channel.owner = user
                db.session.add(channel)

            for userConfig in [("Jakob", "1234"), ("Karl", "C++"), ("Tom", "MATERIALUI"), ("Bruno", "adenosintriphosphat")]:
                user = User()
                user.username = userConfig[0]
                user.email = f"{userConfig[0]}@intectainment.de"
                user.changePassword(userConfig[1])
                db.session.add(user)

            for category in ["Python", "Flask", "Java", "Infotainment", "Informationsübertragung", "CSS", "JavaScript", "Markdown"]:
                db.session.add(Category(name=category))

            db.session.commit()


            return render_template("admin/setup.html", success = True)

    return render_template("admin/setup.html")


gui.register_blueprint(admin)