from Intectainment.app import db
from flask import session
import bcrypt, json

class User(db.Model):
	class PrivilegeLevel:
		GUEST = 0
		USER = 1
		MODERATOR = 10
		ADMIN = 255


	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	username	=	db.Column( db.String(80)	, unique=True	, nullable=False )
	displayname =   db.Column( db.String(80)	, unique=True	, nullable=True )
	password	=	db.Column( db.String(80)	, unique=False	, nullable=False )
	email		=	db.Column( db.String(320)	, unique=True	, nullable=False )
	privilege	=	db.Column( db.Integer		, unique=False	, nullable=True	 )

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
				session["User"] = user.id
				return True
		return False
	
	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__)
	
	@staticmethod
	def getCurrentUser():
		#TODO mabe find better way to do this, also see logIn()
		if "User" in session:
			return User.query.filter_by(id=session["User"]).first()
		else:
			return None
	
	@staticmethod
	def logOut() -> None:
		if "User" in session:
			session.pop("User", None)

	@staticmethod
	def isLoggedIn() -> bool:
		return "User" in session

	def validatePassword(self, password: str) -> bool:
		return bcrypt.checkpw(password.encode("utf-8"), self.password)

	def changePassword(self, newPassword: str) -> None:
		self.password = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt())

	def changeAttribute(self, attr, value) -> None:
		# TODO
		pass

	def getName(self) -> str:
		return self.displayname or self.username

	def hasAccess(self, level: int) -> bool:
		return level >= self.privilege
	
	def getAccessLevel(self) -> int:
		return self.privilege
	
	
#
#bruno = User(username="Bruno", password=bcrypt.hashpw(b"1234", bcrypt.gensalt()), email="ja")
#db.session.add(bruno)
#db.session.commit()