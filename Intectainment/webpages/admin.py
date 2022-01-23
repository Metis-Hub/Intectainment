from Intectainment.app import app, db
from flask import Blueprint, render_template, request, redirect, url_for

from Intectainment.database.models import User


admin: Blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
def main():
    return render_template("admin/main.html")

@admin.route("/user", methods= ["GET", "POST"])
def userconfig():
    if(request.method == "GET"):
        return render_template("admin/userConfig.html")
    elif(request.method == "POST"):
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
                    db.session.commit()
                    return render_template("admin/userConfig.html", createUser="success", userName=post.get("username"))
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

        return redirect(url_for("admin.userconfig"))
    pass




app.register_blueprint(admin)