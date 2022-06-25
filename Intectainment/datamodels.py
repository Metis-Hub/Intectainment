from Intectainment import db, app
from Intectainment.ldapAuthentication import User

import os.path, datetime
from flask import session, url_for


ChannelCategory = db.Table(
    "ChannelCategory",
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
    db.Column("channel_id", db.Integer, db.ForeignKey("channel.id"), primary_key=True),
)

RssFeeds = db.Table(
    "feed",
    db.Column("channel_id", db.Integer, db.ForeignKey("channel.id")),
    db.Column("rss_id", db.Integer, db.ForeignKey("RSS.id")),
)


class Subscription(db.Model):
    user = db.Column(db.String(80), primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), primary_key=True)


class Favorites(db.Model):
    user = db.Column(db.String(80), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=True)
    owner = db.Column(db.String(80), nullable=False)
    icon_extension = db.Column(db.String(4))
    img_xPos = db.Column(db.Integer, nullable=False, default=0)
    img_yPos = db.Column(db.Integer, nullable=False, default=0)
    img_zoom = db.Column(db.Integer, nullable=False, default=5500)

    categories = db.relationship(
        "Category", secondary=ChannelCategory, backref="channels"
    )
    posts = db.relationship("Post", backref="channel")

    canModify = lambda self, user: user and (
        user.permission >= User.PERMISSION.MODERATOR or user.id == self.owner.id
    )

    def getProfileImagePath(self):
        if self.icon_extension:
            return url_for(
                "display_image_",
                type="c",
                filename=str(self.id) + "." + self.icon_extension,
            )
        return url_for("static", filename="default_chimg.png")


class Post(db.Model):
    CONTENTDIRECTORY = "content/posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creationDate = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    modDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), nullable=False)
    owner = db.Column(db.String(80), nullable=False)

    def getContent(self):
        """returns the content of post"""
        try:
            with open(self.getFilePath(), "r") as file:
                return file.read()
        except FileNotFoundError:
            self.createFile()
            return ""

    def getContentLines(self):
        try:
            with open(self.getFilePath(), "r") as file:
                return file.readlines()
        except FileNotFoundError:
            self.createFile()
            return []

    def setContent(self, content):
        """sets the content of the post"""
        with open(self.getFilePath(), "w", newline="\n") as file:
            file.write(content)

    def getFilePath(self):
        """returns the path to the related post file"""
        return os.path.join(
            os.path.dirname(__file__),
            self.CONTENTDIRECTORY,
            f"{self.channel_id}-{self.id}.md",
        )

    def createFile(self):
        if not os.path.isfile(self.getFilePath()):
            with open(self.getFilePath(), "x") as f:
                pass

    canModify = lambda self, user: user and (
        user.permission >= User.PERMISSION.MODERATOR or user.id == self.owner.id
    )

    @staticmethod
    def new(channel_id, content, user=None):
        """To create a basic Post"""

        if not user:
            user = User.getCurrentUser()

        post = Post(channel_id=channel_id, owner=user.username)
        """post has to be commited befor file can be created since the id isn't yet available"""
        db.session.add(post)
        db.session.commit()

        post.createFile()
        post.setContent(content)

        return post

    def delete(self):
        """removes the db-object and the linked file"""
        source_path = os.path.join(
            app.config["UPLOAD_FOLDER"], "c/", str(self.id) + "/"
        )
        if os.path.exists(source_path):
            os.remove(source_path)
        os.remove(self.getFilePath())
        db.session.delete(self)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class RSS(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rss = db.Column(db.String(64), unique=True, nullable=False)

    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), nullable=False)
    guid = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return self.name


# init timeout check
def checkUsers():
    for key in User.activeUsers.keys():
        user = User.activeUsers[key]
        if (
            time.time() - user.lastActive >= user.timeout
            and User.activeUsers[key].timeout != -1
        ):
            User.activeUsers.pop(key)

    time.sleep(60 * 1)


afkCheckThread = threading.Thread(name="afkChecker", target=checkUsers)
afkCheckThread.daemon = True
afkCheckThread.start()
