from Intectainment import db
import Intectainment.datamodels as dbm

from flask import session

from ldap3 import Connection, Server, SUBTREE
from ldap3.core.exceptions import LDAPBindError

import random, os, threading, time, ast, string

# loads a dict of (groupName -> permission) mappings and sorts them descendingly
roles = os.getenv("INTECTAINMENT_LDAP_PERMISSIONS")
if roles:
    roles = {
        k: v
        for k, v in sorted(
            ast.literal_eval(roles).items(), key=lambda item: item[1], reverse=True
        )
    }
else:
    roles = {}


# class OldUser:
#    subscriptions = db.relationship(
#        "Channel", secondary=Subscription, backref="subscibers"
#    )
#    favoritePosts = db.relationship("Post", secondary=Favorites, backref="favUsers")
#
#    channels = db.relationship("Channel", backref="owner")
#    posts = db.relationship("Post", backref="owner")
#
#    def getFavoritePosts(self):
#        return self.favoritePosts
#
#    def getSubscriptions(self):
#        return self.subscriptions


class User:
    activeUsers: dict = dict()
    TIMEOUT_TIME: int = 60 * 30

    class PERMISSION:
        GUEST = 0
        USER = 10
        MODERATOR = 100
        ADMIN = 255

    def __init__(self, username: str, permission: int = None):
        self.username = username

        if permission:
            self.permission = permission
        else:
            self.permission = User.loadPermission(username)

        self.lastActive = time.time()

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def logIn(username: str, password: str):
        if User.isLoggedIn():
            return True
        try:
            conn = Connection(
                os.getenv("INTECTAINMENT_LDAP_SERVER"),
                getUserDN(username),
                password,
                auto_bind=True,
            )
        except LDAPBindError:
            return False

        user = User(username)

        key: str = None
        while not key or key in User.activeUsers:
            key = "".join(
                random.choices(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits,
                    k=80,
                )
            )

        User.activeUsers[key] = user
        session["User"] = key

        print(f"User {username} was successfully logged in")

        return True

    @staticmethod
    def loadPermission(uid: str):
        # TODO
        return User.PERMISSION.ADMIN

    @staticmethod
    def getCurrentUser():
        if "User" in session:
            if session["User"] in User.activeUsers:
                return User.activeUsers[session["User"]]
        return None

    @staticmethod
    def resetTimeout():
        if "User" in session:
            if session["User"] in User.activeUsers:
                user = User.activeUsers[session["User"]]
                user.lastActive = time.time()

    @staticmethod
    def logOut() -> None:
        if "User" in session:
            User.activeUsers.pop(session["User"], None)
            session.pop("User", None)

    @staticmethod
    def isLoggedIn() -> bool:
        return "User" in session and session["User"] in User.activeUsers.keys()

    @staticmethod
    def getCurrentUser():
        if "User" in session:
            if session["User"] in User.activeUsers:
                return User.activeUsers[session["User"]]
        return None

    def getSubscriptions(self):
        """
        returns a query object to retrieve the subscriptions of the user
        """
        return dbm.Subscription.query.filter(
            dbm.Subscription.user == self.username
        ).join(dbm.Channel, dbm.Subscription.channel_id == dbm.Channel.id)

    def addSubscriptions(self, channel_id):
        if not dbm.Subscription.query.filter_by(
            user=self.username, channel_id=channel_id
        ).first():
            db.session.add(dbm.Subscription(user=self.username, channel_id=channel_id))

    def removeSubscriptions(self, channel_id):
        if subscription := dbm.Subscription.query.filter_by(
            user=self.username, channel_id=channel_id
        ).first():
            db.session.delete(subscription)

    def getFavoritePosts(self):
        """
        returns a query object to retrieve the favorite posts of the user
        """

        return dbm.Favorites.query.filter(dbm.Favorites.user == self.username).join(
            dbm.Post, dbm.Favorites.post_id == dbm.Post.id
        )

    def addFavorite(self, post_id):
        if not dbm.Favorites.query.filter_by(
            user=self.username, post_id=post_id
        ).first():
            db.session.add(dbm.Favorites(user=self.username, post_id=post_id))

    def removeFavorite(self, post_id):
        if fav := dbm.Favorites.query.filter_by(
            user=self.username, post_id=post_id
        ).first():
            db.session.delete(fav)


def getUserDN(user: str):
    return f"{os.getenv('INTECTAINMENT_LDAP_USER_ID')}={user},{os.getenv('INTECTAINMENT_LDAP_USER_DN')},{os.getenv('INTECTAINMENT_LDAP_ROOT')}"


def getGroupDN(group: str):
    return f"{os.getenv('INTECTAINMENT_LDAP_GROUP_ID')}={group},{os.getenv('INTECTAINMENT_LDAP_GROUP_DN')},{os.getenv('INTECTAINMENT_LDAP_ROOT')}"


# init timeout check
def checkUsers():
    for key in User.activeUsers.keys():
        user = User.activeUsers[key]
        if time.time() - user.lastActive >= 60 * 20:
            User.activeUsers.pop(key)

    time.sleep(60 * 1)


afkCheckThread = threading.Thread(name="afkChecker", target=checkUsers)
afkCheckThread.daemon = True
afkCheckThread.start()
