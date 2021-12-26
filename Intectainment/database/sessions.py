from Intectaiment.app import User

# Hier ist der Angemeldete Benutzer auffindbar
class ActualUser(User):
	
	def __init__():
		if session["ActualUser"] != None:
			self = session["ActualUser"]
		else:
			self.id = None
			self.username = "Visitor"
			self.password = None
			self.email = None
			self.privilege = 0

	def __init__(db_user):
		self.id = db_user.id
		self.username = db_user.username
		self.password = db_user.password
		self.email = db_user.email
		self.privilege = db_user.privilege

	def __del__(self):
		session["ActualUser"] = self

	@staticmethod
	def LogIn(password):
		# TODO varification
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