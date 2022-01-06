from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser, os


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
print(config.sections())


app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

# server configs
app.config["SERVER_NAME"] = f"{(config.get('Server').get('server', 'localhost'))}:{(config['Server'].get('port') or '3000')}"
app.config["SECRET_KEY"] = config.get('Server').get("secretKey", "replaceWhenDeployToDoThings")

## init database
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("Database").get("URI") or "mysql+pymysql://root:@localhost/intectainment"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = (config.get("Development").get("deyMode")) == "yes" #dev state
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
