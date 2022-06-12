from Intectainment import db, app
from Intectainment.ldapAuthentication import User

import os.path, datetime
from flask import session, url_for

ChannelCategory = db.Table(
    "channelCategories",
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
    db.Column("channel_id", db.Integer, db.ForeignKey("channel.id"), primary_key=True),
)

Subscription = db.Table(
    "subscribedChannels",
    db.Column("channel_id", db.Integer, db.ForeignKey("channel.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

Favorites = db.Table(
    "favoritePost",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)


class OldUser:
    subscriptions = db.relationship(
        "Channel", secondary=Subscription, backref="subscibers"
    )
    favoritePosts = db.relationship("Post", secondary=Favorites, backref="favUsers")

    channels = db.relationship("Channel", backref="owner")
    posts = db.relationship("Post", backref="owner")

    def getFavoritePosts(self):
        return self.favoritePosts

    def getSubscriptions(self):
        return self.subscriptions


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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

    def addFav(self, user=None, commit=True):

        if not user:
            if currentUser := User.getCurrentUser():
                user = User.query.filter_by(id=currentUser.id).first()
            else:
                return False
        if not self in user.favoritePosts:
            user.favoritePosts.append(self)
            if commit:
                db.session.commit()
            return True
        return False

    def remFav(self, user=None, commit=True):
        if not user:
            if currentUser := User.getCurrentUser():
                user = User.query.filter_by(id=currentUser.id).first()
            else:
                return False
        if self in user.favoritePosts:
            user.favoritePosts.remove(self)
            if commit:
                db.session.commit()
            return True
        return False

    @staticmethod
    def new(channel_id, content, user=None):
        """To create a basic Post"""

        if not user:
            user = User.getCurrentUser()

        post = Post(channel_id=channel_id, owner=user)
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
