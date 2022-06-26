import feedparser, threading, time

from flask import render_template, request, redirect, url_for

from Intectainment import db
import Intectainment.datamodels as dbm
from Intectainment.webpages import gui
from Intectainment.util import moderator_required


@gui.route("/rss/new", methods=["GET", "POST"])
@moderator_required
def newRss():
    if request.method == "POST":
        name, rss_url = request.form.get("name"), request.form.get("rss-url")

        if name:
            if not dbm.Channel.query.filter_by(name=name).first():
                channel = dbm.Channel(
                    name=name,
                    owner="RSS-Feed",
                )
                db.session.add(channel)
                db.session.commit()
            else:
                return render_template(
                    "main/channel/channelCreation.html", error="Kanal existiert schon"
                )

        if rss_url:
            if dbm.Rss_link.query.filter_by(url=rss_url).first():
                dbm.Rss_link.query.filter_by(url=rss_url).channel.append(
                    dbm.Channel.query.filter_by(name=name).first()
                )
            else:
                # last three entries will be shown
                parsedFeed = feedparser.parse(rss_url)
                lastGuid = parsedFeed["entries"][3]["guid"]

                feed = dbm.Rss_link(url=rss_url, guid=lastGuid)
                feed.channel.append(dbm.Channel.query.filter_by(name=name).first())

                db.session.add(feed)
                db.session.commit()
            return redirect(url_for("gui.channelView", channel=name))
            update_rss()

    return render_template("main/channel/rssCreation.html")


def update_rss():
    for feed in dbm.Rss_link.query.all():
        url = feed.url

        parsedFeed = feedparser.parse(url)

        readFeed = 0
        for entry in parsedFeed["entries"]:
            if str(entry["guid"]) == str(feed.guid):
                break
            readFeed += 1

        if readFeed == 0:
            continue
        feed.guid = parsedFeed["entries"][0]["guid"]
        for i in range(readFeed, 0, -1):
            entry = parsedFeed["entries"].get(i)

            if entry == None:
                break

            pubDate = "Veröffentlichung: " + entry.published + "  \n"

            title = f'# {entry.get("title", "")}\n'
            author = f'_von {entry.get("author", "")}_\n'
            link = f'[Link zum Artikel]({entry.get("link","")})\n\n'
            description = entry.get("description", "")
            summary = entry.get("summary", "")

            for channel in feed.getChannel():
                # adding post
                post = dbm.Post(channel_id=channel.id, owner=entry["author"])
                db.session.add(post)
                db.session.commit()

                post.createFile()
                post.setContent(title + link + description + summary)


def timed_rss_update():
    update_rss()
    time.sleep(60 * 60 * 12)


rssThread = threading.Thread(name="rssQuery", target=timed_rss_update)
rssThread.daemon = True
rssThread.start()
