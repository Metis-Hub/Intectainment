from Intectainment.app import app, db
from Intectainment.datamodels import Channel, Category, Post, User
from Intectainment.webpages.webpages import gui
from Intectainment.util import login_required
from Intectainment.imageuploder import move_images

from flask import request, render_template, redirect, url_for

import datetime

##### Kanäle #####
@gui.route("/channels", methods=["GET"])
def channelSearch():
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    channels = Channel.query.filter(Channel.name.like(f"%{request.args.get('channelname', '')}%")).paginate(per_page=20, page=page_num, error_out=False)
    return render_template("main/channel/channelSearch.html", channels=channels)


@gui.route("/channels/new", methods=["GET", "POST"])
@login_required
def channelCreation():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            if not Channel.query.filter_by(name=name).first():
                channel = Channel(name=name, owner=User.getCurrentUser())
                db.session.add(channel)
                db.session.commit()

                return redirect(url_for("gui.channelView", channel=name))
            else:
                return render_template("main/channel/channelCreation.html", error="Kanal existiert schon")
    return render_template("main/channel/channelCreation.html")



@gui.route("/c/<channel>")
@gui.route("/channel/<channel>")
def channelView(channel):
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    channel = Channel.query.filter_by(name=channel).first_or_404()
    posts = Post.query.filter_by(channel_id=channel.id).paginate(per_page=20, page=page_num, error_out=False)

    return render_template("main/channel/channelView.html", channel=channel, posts=posts, canModify=channel.canModify(User.getCurrentUser()))


@gui.route("/c/<channel>/settings", methods=["GET", "POST"])
@gui.route("/channel/<channel>/settings", methods=["GET", "POST"])
@login_required
def channelSettings(channel):
    channel = Channel.query.filter_by(name=channel).first_or_404()

    if not channel.canModify(User.getCurrentUser()):
        return redirect(url_for("gui.channelView", channel=channel))

    if request.method == "POST":
        if request.form.get("addCategory") and request.form.get("category"):
            name = request.form.get("category")
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                db.session.add(category)

            if category not in channel.categories:
                channel.categories.append(category)
                db.session.commit()
        elif request.form.get("deleteCategory") and request.form.get("category"):
            channel.categories.remove(Category.query.filter_by(name=request.form.get("category")).first())
            db.session.commit()
        elif request.form.get("changeDescription"):
            channel.description = request.form.get("description", "")
            db.session.commit()

    return render_template("main/channel/channelSettings.html", channel=channel, categories=Category.query.all())

##### Posts #####
@gui.route("/post/<postid>", methods=["GET", "POST"])
def postView(postid):
    post = Post.query.filter_by(id=postid).first_or_404()

    if request.method == "POST":
        if "delete" in request.form:
            channel = ""
            if post.canModify(User.getCurrentUser()):
                channel = post.channel.name
                post.delete()
                db.session.commit()
            return redirect(url_for("gui.channelView", channel=channel))
        elif "fav" in request.form:
            user = User.query.filter_by(id=User.getCurrentUser().id).first()
            if user:
                if not post in user.favoritePosts:
                    user.favoritePosts.append(post)
                    db.session.commit()
        elif "defav" in request.form:
            user = User.query.filter_by(id=User.getCurrentUser().id).first()
            if user:
                if not post in user.favoritePosts:
                    user.favoritePosts.remove(post)
                    db.session.commit()

    timeMessage = f"Erstellt am {post.creationDate.strftime('%d.%m.%Y %H:%M')}"
    if post.creationDate != post.modDate:
        timeMessage = f"Modifiziert am {post.modDate.strftime('%d.%m.%Y %H:%M')}"



    return render_template("main/post/showPost.html",
                           post=post,
                           user=User.getCurrentUser(),
                           timeMessage = timeMessage,
                           faved=User.isLoggedIn() and (post in User.query.filter_by(id=User.getCurrentUser().id).first().getFavoritePosts()),
                           canModify=post.canModify(User.getCurrentUser()))


@gui.route("/c/<channel>/new", methods=["GET", "POST"])
@gui.route("/channel/<channel>/new", methods=["GET", "POST"])
@login_required
def createPost(channel):
    channel = Channel.query.filter_by(name=channel).first_or_404()

    if request.method == "POST":
        post = Post.new(channel.id, request.form.get("content") or "")
        content = post.getContent().replace("tmp/" + str(User.getCurrentUser().id), "p/" + str(post.id))
        post.setContent(content)
        move_images(User.getCurrentUser().id, post.id)
        return redirect(url_for("gui.postView", postid = post.id))

    return render_template("main/post/newPost.html", server=app.config["SERVER_NAME"], usrid=User.getCurrentUser().id)

@gui.route("/post/<postid>/edit", methods=["GET", "POST"])
@login_required
def postEdit(postid):
    post = Post.query.filter_by(id = postid).first_or_404()
    if not post.canModify(User.getCurrentUser()):
        return redirect(url_for("gui.postView", postid=postid))

    if request.method == "POST":
        if request.form.get("update"):
            post.setContent(request.form.get("content") or "")
            post.modDate = datetime.datetime.now()
            db.session.commit()
        return redirect(url_for("gui.postView", postid=post.id))

    return render_template("main/post/editPost.html", server=app.config["SERVER_NAME"], post=post, canModify=post.canModify(User.getCurrentUser()))



##### Kategorien #####
@gui.route("/categories", methods=["GET"])
def viewCategories():
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    categories = Category.query.paginate(per_page=20, page=page_num, error_out=False)
    return render_template("main/category/categoryList.html", categories=categories)


@gui.route("/categories/new", methods=["GET", "POST"])
@login_required
def createCategory():
    if request.method == "GET":
        return render_template("main/category/categoryCreation.html")
    elif request.method == "POST":
        name = request.form.get("name")
        if name:
            if Category.query.filter_by(name=name).count() > 0:
                # exists allready
                return render_template("main/category/categoryCreation.html", error="exists",
                                       message="Die Kategorie existiert bereits")
                pass
            else:
                category = Category(name=name)
                db.session.add(category)
                db.session.commit()

                return render_template("main/category/categoryCreation.html", message="Kategorie erfolgreich erstellt")
                pass
        else:
            return render_template("main/category/categoryCreation.html", error="noargument",
                                   message="Name als Argument benötigt")