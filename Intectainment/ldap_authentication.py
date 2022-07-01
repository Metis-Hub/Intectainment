from Intectainment import app, db
import Intectainment.datamodels as dbm

from flask import session

from ldap3 import Connection, Server, SUBTREE
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

import random, os, threading, time, ast, string

LDAP_SERVER = Server(os.getenv("INTECTAINMENT_LDAP_SERVER"))


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
            self.permission = loadPermission(username)

        self.lastActive = time.time()

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def logIn(username: str, password: str):
        if User.isLoggedIn():
            return True
        try:
            conn = Connection(
                LDAP_SERVER,
                getUserDN(username),
                password,
                auto_bind=True,
            )
        except LDAPBindError:
            return False
        except LDAPSocketOpenError:
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

        return True

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

        return dbm.Channel.query.filter(
            dbm.Channel.id.in_(
                [
                    result.channel_id
                    for result in dbm.Subscription.query.filter_by(
                        user=self.username
                    ).all()
                ]
            )
        )

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
        return dbm.Post.query.filter(
            dbm.Post.id.in_(
                [
                    result.post_id
                    for result in dbm.Favorites.query.filter_by(
                        user=self.username
                    ).all()
                ]
            )
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


# loads a dict of (groupName -> permission) mappings
roles = ast.literal_eval(os.getenv("INTECTAINMENT_LDAP_PERMISSIONS"))

# creates a ldap filter with all relevant groups
search_filter = f"(&(objectclass={os.getenv('INTECTAINMENT_LDAP_GROUP_OBJ_CLASS')})(|"
for group in roles:
    search_filter = (
        search_filter + f"({os.getenv('INTECTAINMENT_LDAP_GROUP_ID')}={group})"
    )
search_filter = search_filter + ")"


def loadPermission(uid: str) -> int:
    try:
        conn = Connection(
            LDAP_SERVER,
            user=os.getenv("INTECTAINMENT_LDAP_ELEVATED_USER"),
            password=os.getenv("INTECTAINMENT_LDAP_ELEVATED_PWD"),
            auto_bind=True,
            use_referral_cache=True,
        )

        conn.search(
            f"{os.getenv('INTECTAINMENT_LDAP_GROUP_DN')},{os.getenv('INTECTAINMENT_LDAP_ROOT')}",
            search_filter
            + f"({os.getenv('INTECTAINMENT_LDAP_GROUP_MEMBER_ATTR')}={uid}))",
            attributes=[
                os.getenv("INTECTAINMENT_LDAP_GROUP_ID"),
            ],
        )

        permission = 0
        for entry in conn.entries:
            permission = roles[
                str(entry.__getattribute__(os.getenv("INTECTAINMENT_LDAP_GROUP_ID")))
            ]
        return permission
    except LDAPBindError:
        return User.PERMISSION.GUEST
    except LDAPSocketOpenError:
        return User.PERMISSION.GUEST


# init timeout check
def checkUsers():
    for key in User.activeUsers.keys():
        user = User.activeUsers[key]
        if time.time() - user.lastActive >= 60 * 20:
            User.activeUsers.pop(key)

    time.sleep(60 * 1)


@app.before_first_request
def startup():
    afkCheckThread = threading.Thread(name="afkChecker", target=checkUsers)
    afkCheckThread.daemon = True
    afkCheckThread.start()
