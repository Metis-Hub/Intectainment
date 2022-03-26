import os.path, datetime, pathlib

from Intectainment.app import db
from flask import session, url_for
import bcrypt, threading, time, string, random


ChannelCategory = db.Table('channelCategories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id'), primary_key=True)
)

Subscription = db.Table('subscribedChannels',
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

Favorites = db.Table('favoritePost',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class User(db.Model):
	class PERMISSION:
		GUEST = 0
		USER = 10
		MODERATOR = 100
		ADMIN = 255


	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	username	  = db.Column(db.String(80), unique=True, nullable=False)
	displayname   = db.Column(db.String(80), unique=True)
	password	  = db.Column(db.String(80), nullable=False)
	permission	  = db.Column(db.Integer, default=PERMISSION.USER)
	icon_extension = db.Column(db.String(4))


	subscriptions = db.relationship("Channel", secondary=Subscription, backref="subscibers")
	favoritePosts = db.relationship("Post", secondary=Favorites, backref="favUsers")

	channels = db.relationship("Channel", backref="owner")
	posts    = db.relationship("Post", backref="owner")

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.lastActive = time.time()

	def __repr__(self):
		return '<User %r>' % self.username

	def reload(self):
		if "User" in session and session["User"] in User.activeUsers.keys():
			User.activeUsers[session["User"]] = User.query.filter_by(id=self.id).first()


	# Timeout management
	TIMEOUT_TIME: int = 60 * 30
	activeUsers: dict = dict()
	@staticmethod
	def resetTimeout():
		if "User" in session:
			if session["User"] in User.activeUsers:
				user = User.activeUsers[session["User"]]
				user.lastActive = time.time()

	# login/logout utility
	@staticmethod
	def logIn(username: str, password: str) -> bool:
		if "User" in session and session["User"] in User.activeUsers.keys():
			#already logged in
			return True
		else:
			user: User = User.query.filter_by(username=username).first()
			if not user:
				return False

			if user.validatePassword(password):
				if not user in User.activeUsers.values():
					key: str = None
					while not key or key in User.activeUsers:
						key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=40))

					User.activeUsers[key] = user
					session["User"] = key
					return True
				else:
					return True
		return False

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
			
	def validatePassword(self, password: str) -> bool:
		return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

	def changePassword(self, newPassword: str) -> None:
		self.password = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt())

	def getName(self) -> str:
		return self.displayname or self.username

	def getFavoritePosts(self):
		return self.favoritePosts

	def getSubscriptions(self):
		return self.subscriptions

	def getProfileImagePath(self):
		if self.icon_extension:
			return url_for("display_image_", type="usr", filename=str(self.id) + "." + self.icon_extension)
		return url_for("static", filename="default_usrimg.png")

class Channel(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	name			= db.Column( db.String(80), unique=True, nullable=False )
	description		= db.Column( db.String(80), nullable=True )
	icon_extension	= db.Column(db.String(4))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	categories	= db.relationship("Category", secondary=ChannelCategory, backref="channels")
	posts		= db.relationship("Post", backref="channel")

	canModify = lambda self, user: user and (user.permission >= User.PERMISSION.MODERATOR or user.id == self.owner.id)
	


class Post(db.Model):
	CONTENTDIRECTORY = "content/posts"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	creationDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
	modDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

	channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


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
		with open(self.getFilePath(), "w", newline='\n') as file:
			file.write(content)

	def getFilePath(self):
		"""returns the path to the related post file"""
		return os.path.join(os.path.dirname(__file__), self.CONTENTDIRECTORY, f"{self.channel_id}-{self.id}.md")

	def createFile(self):
		if not os.path.isfile(self.getFilePath()):
			with open(self.getFilePath(), "x") as f:
				pass

	canModify = lambda self, user: user and (user.permission >= User.PERMISSION.MODERATOR or user.id == self.owner.id)

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
		os.remove(self.getFilePath())
		db.session.delete(self)



class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column( db.String(80), unique=True, nullable=False )

	def __repr__(self):
		return self.name

# init timeout check
def checkUsers():
	for key in User.activeUsers.keys():
		user = User.activeUsers[key]
		if time.time() - user.lastActive >= User.TIMEOUT_TIME and User.activeUsers[key].TIMEOUT_TIME != -1:
			User.activeUsers.pop(key)
		
	time.sleep(User.TIMEOUT_TIME)
afkCheckThread = threading.Thread(name="afkChecker", target=checkUsers)
afkCheckThread.daemon = True
afkCheckThread.start()
