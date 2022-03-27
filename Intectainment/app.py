from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import configparser, os, sys


if "--init" in sys.argv[1:] or "-i" in sys.argv[1:]:
	if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'config.conf')):
		with open(os.path.join(os.path.dirname(__file__), 'config.conf'), "x") as file:
			file.writelines(["[Server]\n",
							 "server = localhost\n"
							 "port = 3000\n"
							 "secretKey = replaceWhenDeployToDoThings\n"
							 "\n"
							 "\n"
							 "[Database]\n",
							 "URI = YOURDATABASEURI"])
		print("The File config.conf has been created in the directory Intectainment/\nPlease edit the config to your fitting and press any key to continue")
		input()

# init config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.conf'))
for section in ["Server", "Database"]:
	if section not in config:
		config.add_section(section)

app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

# server configs
app.config["SERVER_NAME"] = f"{(config['Server'].get('server', fallback='localhost'))}:{(config['Server'].get('port', fallback='3000'))}"
app.config["SECRET_KEY"] = config['Server'].get("secretKey", fallback="replaceWhenDeployToDoThings")

app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), app.static_folder, "img")

## init database
app.config["SQLALCHEMY_DATABASE_URI"] = config['Database'].get("URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


try:
	db.engine.execute("SELECT 1")
except OperationalError:
	print("Could not connect to database!\nPlease make sure you entered the correct database-URI")
	exit()


# load tables
import Intectainment.datamodels

#first initialisation
from Intectainment.datamodels import User
if "--init" in sys.argv[1:] or "-i" in sys.argv[1:]:
	db.create_all()

	# create default super user
	if not User.query.filter_by(username = "Admin").first():
		user = User()
		user.permission = User.PERMISSION.ADMIN
		user.username = "Admin"
		user.changePassword("intectainment")
		db.session.add(user)
		db.session.commit()

	for dir in ["content/posts"]:
		path = os.path.join(os.path.dirname(__file__), dir)
		if not os.path.exists(path):
			os.makedirs(path)


	print("Initialisation finished")

# load webpages
from Intectainment.webpages import webpages
