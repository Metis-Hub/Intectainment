from Intectainment.app import db
from flask import session
import bcrypt

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
	def LogIn(username: str, password: str) -> bool:
		if "User" in session:
			#already logged in
			return True
		else:
			user: User = User.query.filter_by(username=username).first()

			if user.validatePassword(password):
				session["User"] = user
				return True
			else:
				return False

	@staticmethod
	def logOut() -> None:
		if "User" in session:
			session.pop("User", None)

	@staticmethod
	def isLogedIn() -> bool:
		return "User" in session

	def validatePassword(self, password: str) -> bool:
		return bcrypt.checkpw(password, self.password)

	def changePW(self, newPassword: str) -> None:
		self.password = bcrypt.hashpw(newPassword, bcrypt.getsalt())

	def changeAttribute(self, attr, value) -> None:
		# TODO
		pass

	def hasAccess(self, level: int) -> bool:
		return level >= self.privilege
	
	def getAccessLevel(self) -> int:
		return self.privilege
	
	
