import os.path, datetime, pathlib

from Intectainment.app import db
from flask import session
import bcrypt, threading, time, string, random


ChannelCategory = db.Table('channelCategories',
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True)
)

Subscription = db.Table('subscribedChannels',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

Favorites = db.Table('favoritePost',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
	db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class User(db.Model):
	__tablename__ = "users"

	class PERMISSION:
		GUEST = 0
		USER = 10
		MODERATOR = 100
		ADMIN = 255


	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	username	=	db.Column( db.String(80), unique=True, nullable=False)
	displayname =   db.Column( db.String(80), unique=True)
	password	=	db.Column( db.String(80), nullable=False)
	permission	=	db.Column( db.Integer, default=PERMISSION.USER)

	subscriptions = db.relationship("Channel", secondary=Subscription, backref="subscibers")
	# user = User.query.filter_by(id=User.getCurrentUser().id).first()
	# subscr = 
	# db.session.add()
	# db.session.commit()
	favoritePosts = db.relationship("Post", secondary=Favorites, backref="favUsers")

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.lastActive = time.time()

	def __repr__(self):
		return '<User %r>' % self.username

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
					#cant save object in session

					key: str = None
					while not key or key in User.activeUsers:
						key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=40))

					User.activeUsers[key] = user
					session["User"] = key
					return True
				else:
					#TODO user allready logged in
					pass
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

	#TODO
	def getContent(self):
		content = []
		for sub in self.subscriptions:
			content.append(sub.entries)
   
		return content

	#TODO test
	def getFavoritePosts(self):
		return self.favoritePosts

class Channel(db.Model):
	__tablename__ = "channels"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name	=	db.Column( db.String(80), unique=True, nullable=False )
	description =   db.Column( db.String(80), nullable=True )

	categories = db.relationship("Category", secondary=ChannelCategory, backref="channels")
	posts = db.relationship("Post", backref="channel")

	#TODO add utility
	


class Post(db.Model):
	__tablename__ = "posts"
	CONTENTDIRECTORY = "content/posts"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	creationDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
	modDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
	channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)

	def getContent(self):
		"""returns the content of post"""
		try:
			with open(self.getFilePath(), "r") as file:
				return file.read()
		except FileNotFoundError:
			self.createFile()
			return ""

	def setContent(self, content):
		"""sets the content of the post"""
		with open(self.getFilePath(), "w") as file:
			file.write(content)

	def getFilePath(self):
		"""returns the path to the related post file"""
		return os.path.join(os.path.dirname(__file__), self.CONTENTDIRECTORY, f"{self.channel_id}-{self.id}.md")

	def createFile(self):
		if not os.path.isfile(self.getFilePath()):
			with open(self.getFilePath(), "x") as f:
				pass

	@staticmethod
	def new(channel_id, content):
		"""To create a basic Post"""

		post = Post(channel_id=channel_id)
		db.session.add(post)
		db.session.commit()

		post.createFile()
		post.setContent(content)

		return post

	def delete(self):
		os.remove(self.getFilePath())
		db.session.delete(self)



class Category(db.Model):
	__tablename__ = "categories"
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
