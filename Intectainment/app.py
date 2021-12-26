from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

# server configs
app.config["SERVER_NAME"] = "localhost:3000"
app.config["SECRET_KEY"] = "replaceWhenDeployToDoThings"

## init database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/intectainment"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #dev state
db = SQLAlchemy(app)
# load tables
import Intectainment.database.models
#TODO only for dev
try:
	db.create_all()
except:
	print("Database not connected")

# load webpages
from Intectainment.webpages import webpages
