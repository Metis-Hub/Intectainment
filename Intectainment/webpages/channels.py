from Intectainment import app, db
from Intectainment.datamodels import Channel, Post, User, RssLink
from Intectainment.webpages import gui
from Intectainment.util import login_required
from Intectainment.images import move_images
from Intectainment.webpages.rss_feeds import createRssLink

from flask import request, render_template, redirect, url_for
from sqlalchemy import desc

import datetime

##### Kanäle #####
@gui.route("/home/subscriptions", methods=["POST", "GET"])
@login_required
def handle_subscriptions():
    return render_template(
        "main/home/subscriptions.html",
        channels=User.getCurrentUser().getSubscriptions().all(),
        user=User.getCurrentUser(),
    )


@gui.route("/discover/new", methods=["GET", "POST"])
@login_required
def channelCreation():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            if not Channel.query.filter_by(name=name).first():
                channel = Channel(name=name, owner=User.getCurrentUser().username)
                db.session.add(channel)
                db.session.commit()

                return redirect(url_for("gui.channelView", channel=name))
            else:
                return render_template(
                    "main/channel/channelCreation.html",
                    error="Kanal existiert schon",
                    isMod=User.getCurrentUser().permission >= User.PERMISSION.MODERATOR,
                )
    return render_template(
        "main/channel/channelCreation.html",
        isMod=User.getCurrentUser().permission >= User.PERMISSION.MODERATOR,
    )


@gui.route("/c/<channel>", methods=["POST", "GET"])
@gui.route("/channel/<channel>", methods=["POST", "GET"])
def channelView(channel):
    page_num = 1
    try:
        page_num = int(request.args.get("page"))
    except (ValueError, TypeError):
        pass

    channel = Channel.query.filter_by(name=channel).first_or_404()

    if request.method == "POST" and User.isLoggedIn():
        if "subscr" in request.form:
            User.getCurrentUser().addSubscriptions(channel.id)
            db.session.commit()
        elif "desubscr" in request.form:
            User.getCurrentUser().removeSubscriptions(channel.id)
            db.session.commit()

    posts = (
        Post.query.filter_by(channel_id=channel.id)
        .order_by(desc(Post.creationDate))
        .paginate(per_page=20, page=page_num, error_out=False)
    )

    return render_template(
        "main/channel/channelView.html",
        channel=channel,
        posts=posts,
        canModify=channel.canModify(User.getCurrentUser()),
        user=User.getCurrentUser(),
        subscribed=User.isLoggedIn()
        and (channel in User.getCurrentUser().getSubscriptions().all()),
    )


@gui.route("/c/<channel>/settings", methods=["GET", "POST"])
@gui.route("/channel/<channel>/settings", methods=["GET", "POST"])
@login_required
def channelSettings(channel):
    channel = Channel.query.filter_by(name=channel).first_or_404()

    if not channel.canModify(User.getCurrentUser()):
        return redirect(url_for("gui.channelView", channel=channel.name))

    if request.method == "POST":
        if request.form.get("addRss") and request.form.get("rssLink"):
            createRssLink(request.form.get("rssLink"), channel)
        elif request.form.get("remRss") and request.form.get("rssLink"):
            channel.feeds.remove(
                RssLink.query.filter_by(url=request.form.get("rssLink")).first()
            )
            db.session.commit()

        elif request.form.get("changeDescription"):
            channel.description = request.form.get("description", "")
            db.session.commit()

    return render_template(
        "main/channel/channelSettings.html", channel=channel, user=User.getCurrentUser()
    )


##### Posts #####
@gui.route("/post/<postid>", methods=["GET", "POST"])
def postView(postid):
    post = Post.query.filter_by(id=postid).first_or_404()

    if request.method == "POST" and User.isLoggedIn():
        if "delete" in request.form:
            channel = ""
            if post.canModify(User.getCurrentUser()):
                channel = post.channel.name
                post.delete()
                db.session.commit()
            return redirect(url_for("gui.channelView", channel=channel))
        elif "fav" in request.form:
            User.getCurrentUser().addFavorite(post.id)
            db.session.commit()
        elif "defav" in request.form:
            User.getCurrentUser().removeFavorite(post.id)
            db.session.commit()

    timeMessage = f"Erstellt am {post.creationDate.strftime('%d.%m.%Y %H:%M')}"
    if post.creationDate != post.modDate:
        timeMessage = f"Modifiziert am {post.modDate.strftime('%d.%m.%Y %H:%M')}"

    return render_template(
        "main/post/showPost.html",
        post=post,
        user=User.getCurrentUser(),
        timeMessage=timeMessage,
        faved=User.isLoggedIn()
        and (post in User.getCurrentUser().getFavoritePosts().all()),
        canModify=post.canModify(User.getCurrentUser()),
    )


@gui.route("/c/<channel>/new", methods=["GET", "POST"])
@gui.route("/channel/<channel>/new", methods=["GET", "POST"])
@login_required
def createPost(channel):
    channel = Channel.query.filter_by(name=channel).first_or_404()

    if request.method == "POST":
        if "create" in request.form:
            post = Post.new(channel.id, request.form.get("content") or "")
            content = post.getContent().replace(
                "tmp/" + str(User.getCurrentUser().username), "p/" + str(post.id)
            )
            post.setContent(content)
            move_images(User.getCurrentUser().username, post.id)
            return redirect(url_for("gui.postView", postid=post.id))
        elif "exit" in request.form:
            return redirect(url_for("gui.channelView", channel=channel.name))
    return render_template(
        "main/post/newPost.html",
        server=app.config["SERVER_NAME"],
        usrid=User.getCurrentUser().username,
    )


@gui.route("/post/<postid>/edit", methods=["GET", "POST"])
@login_required
def postEdit(postid):
    post = Post.query.filter_by(id=postid).first_or_404()
    if not post.canModify(User.getCurrentUser()):
        return redirect(url_for("gui.postView", postid=postid))

    if request.method == "POST":
        if request.form.get("update"):
            post.setContent(request.form.get("content") or "")
            post.modDate = datetime.datetime.now()
            db.session.commit()
        return redirect(url_for("gui.postView", postid=post.id))

    return render_template(
        "main/post/editPost.html",
        server=app.config["SERVER_NAME"],
        post=post,
        canModify=post.canModify(User.getCurrentUser()),
    )
