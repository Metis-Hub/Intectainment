import feedparser, threading, time

from flask import render_template, request, redirect, url_for

from Intectainment import app, db
from Intectainment.datamodels import Channel, RssLink, Post
from Intectainment.webpages import gui
from Intectainment.util import moderator_required


def createRssLink(rss_url, channel):
    if feed := RssLink.query.filter_by(url=rss_url).first():
        feed.channel.append(channel)
    else:
        # last three entries will be shown
        parsedFeed = feedparser.parse(rss_url)

        index = min(3, len(parsedFeed["entries"]) - 1)
        if index >= 0:
            lastGuid = parsedFeed["entries"][index]["guid"]
        else:
            lastGuid = 0
        feed = RssLink(url=rss_url, guid=lastGuid)
        feed.channel.append(channel)

        db.session.add(feed)
        db.session.commit()

        update_rss()

        return feed
    return None


def update_rss():
    for feed in RssLink.query.all():
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
            if i >= len(parsedFeed["entries"]):
                continue
            entry = parsedFeed["entries"][i]

            pubDate = "Veröffentlichung: " + entry.published + "  \n"

            title = f'# {entry.get("title", "")}\n'
            author = f'_von {entry.get("author", "")}_\n'
            link = f'[Link zum Artikel]({entry.get("link","")})\n\n'
            description = entry.get("description", "")
            summary = entry.get("summary", "")

            for channel in feed.getChannel():
                # adding post
                post = Post(channel_id=channel.id, owner=f'#{entry["author"]}')
                db.session.add(post)
                db.session.commit()

                post.createFile()
                post.setContent(title + link + description + summary)


def timed_rss_update():
    update_rss()
    time.sleep(60 * 60 * 12)


@app.before_first_request
def startup():
    rssThread = threading.Thread(name="rssQuery", target=timed_rss_update)
    rssThread.daemon = True
    rssThread.start()
