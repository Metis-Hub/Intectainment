import os
import Intectainment.datamodels as dbm
from Intectainment import db

db.create_all()

# create default super user
if not dbm.User.query.filter_by(username = "Admin").first():
	user = dbm.User()
	user.permission = dbm.User.PERMISSION.ADMIN
	user.username = "Admin"
	user.changePassword("intectainment")
	db.session.add(user)
	db.session.commit()

for dir in ["Intectainment/content/posts", "Intectainment/content/img"]:
	path = os.path.join(os.path.dirname(__file__), dir)
	if not os.path.exists(path):
		os.makedirs(path)