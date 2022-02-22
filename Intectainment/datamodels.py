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

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	username	=	db.Column( db.String(80)	, unique=True	, nullable=False )
	displayname =   db.Column( db.String(80)	, unique=True	, nullable=True )
	password	=	db.Column( db.String(80)	, unique=False	, nullable=False )
	email		=	db.Column( db.String(320)	, unique=True	, nullable=False )

	subscriptions = db.relationship("Channel", secondary=Subscription, backref="subscibers")
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
		if "User" in session:
			#already logged in
			return True
		else:
			user: User = User.query.filter_by(username=username).first()
			if not user:
				return False

			if user.validatePassword(password):
				#cant save object in session

				key: str = None
				while not key or key in User.activeUsers:
					key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=40))

				User.activeUsers[key] = user
				session["User"] = key
				return True
		return False

	@staticmethod
	def logOut() -> None:
		if "User" in session:
			User.activeUsers.pop(session["User"], None)
			session.pop("User", None)

	@staticmethod
	def isLoggedIn() -> bool:
		return "User" in session

	@staticmethod
	def getCurrentUser():
		if "User" in session:
			if session["User"] in User.activeUsers:
				return User.activeUsers[session["User"]]
		return None
			
	def validatePassword(self, password: str) -> bool:
		return bcrypt.checkpw(password.encode("utf-8"), self.password)

	def changePassword(self, newPassword: str) -> None:
		self.password = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt())

	#
	def getName(self) -> str:
		return self.displayname or self.username

	#TODO
	def getContent(self):
		content = []
		for sub in self.subscriptions:
			content.append(sub.entries)
   
		return content

	#TODO test
	def getFavoritePosits(self):
		return self.favoritePosts


class Channel(db.Model):
	__tablename__ = "channels"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name	=	db.Column( db.String(80), unique=True, nullable=False )
	description =   db.Column( db.String(80), unique=True, nullable=True )

	categories = db.relationship("Category", secondary=ChannelCategory, backref="channels")
	post = db.relationship("Post", backref="channel")

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
		with open(self.getFilePath(), "r") as file:
			pass

	def setContent(self, content):
		"""sets the content of the post"""
		with open(self.getFilePath(), "w") as file:
			file.write(content)

	def getFilePath(self):
		"""returns the path to the related post file"""
		return os.path.join(os.path.dirname(__file__), self.CONTENTDIRECTORY, f"{self.channel_id}-{self.id}.md")

@db.event.listens_for(Post, 'after_insert')
def createPostFile(mapper, connection, target):
	"""creates post file in content directory"""
	if not os.path.isfile(target.getFilePath()):
		with open(target.getFilePath(), "x") as f:
			f.write("# Hallo")

#TODO only triggers if directly deleted from session, not via query -> fix
@db.event.listens_for(Post, 'before_delete')
def deletePostFile(mapper, connection, target):
	"""removes post file from content directory"""

	os.remove(target.getFilePath())

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