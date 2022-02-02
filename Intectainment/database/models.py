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

class User(db.Model):
	__tablename__ = "users"
	TIMEOUT_TIME: int = 60*30

	activeUsers:dict = dict()
	lastActive = time.time()
	
	@staticmethod
	def resetTimeout():
		if "User" in session:
			if session["User"] in User.activeUsers:
				user = User.activeUsers[session["User"]]
				user.lastActive = time.time()
	
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	username	=	db.Column( db.String(80)	, unique=True	, nullable=False )
	displayname =   db.Column( db.String(80)	, unique=True	, nullable=True )
	password	=	db.Column( db.String(80)	, unique=False	, nullable=False )
	email		=	db.Column( db.String(320)	, unique=True	, nullable=False )

	subscriptions = db.relationship("Channel", secondary=Subscription)

	def __repr__(self):
		return '<User %r>' % self.username
	
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
					key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
				
				print(f"Added {user} with key {key}")
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

	def getName(self) -> str:
		return self.displayname or self.username



class Channel(db.Model):
	__tablename__ = "channels"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name	=	db.Column( db.String(80), unique=True, nullable=False )
	description =   db.Column( db.String(80), unique=True, nullable=True )

	categories = db.relationship("Category", secondary=ChannelCategory)
	channel = db.relationship("BlogEntry", backref="channels")


class BlogEntry(db.Model):
	__tablename__ = "blogentries"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	contentPath = db.Column(db.String(60), nullable=False)
	modDate = db.Column(db.DateTime, nullable=False)

	channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'),
        nullable=False)



class Category(db.Model):
	__tablename__ = "categories"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name	=	db.Column( db.String(80)	, unique=True	, nullable=False )
	
#
#bruno = User(username="Bruno", password=bcrypt.hashpw(b"1234", bcrypt.gensalt()), email="ja")
#db.session.add(bruno)
#db.session.commit()


# init timeout check
def checkUsers():
	for key in User.activeUsers.keys():
		user = User.activeUsers[key]
		if(time.time() - user.lastActive >= User.TIMEOUT_TIME):
			User.activeUsers.pop(key)
		
	time.sleep(User.TIMEOUT_TIME)
afkCheckThread = threading.Thread(name="afkChecker", target=checkUsers)
afkCheckThread.setDaemon(True)
afkCheckThread.start()	