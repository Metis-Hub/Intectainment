from Intectainment.app import db

class User(db.Model):

	id = db.Column(db.Integer, primary_key=True)

	username	=	db.Column( db.String(80)	, unique=True	, nullable=False )
	password	=	db.Column( db.String(80)	, unique=False	, nullable=False )
	email		=	db.Column( db.String(120)	, unique=True	, nullable=False )
	privilege	=	db.Column( db.Integer		, unique=False	, nullable=True	 )

	def __repr__(self):
		return '<User %r>' % self.username

	@staticmethod
	def LogIn(password):
		# TODO: varification
		if True:
			session["IsLogedIn"] = True

	@staticmethod
	def LogOut():
		if session["IsLogedIn"] != None:
			session.pop("IsLogedIn", None)

	@staticmethod
	def IsLogedIn():
		if session["IsLogedIn"] != None & session["IsLogedIn"] == True:
			return True
		return False

	@staticmethod
	def ChangePW():
		# TODO
		pass

	@staticmethod
	def ChangeAttribute(attr, value):
		# TODO
		pass

	@staticmethod
	def HasAccess(level):
		return level >= self.privilege


class UserInfo(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	def __repr__(self):
		return '<UserInfo %r>' % self.id
	