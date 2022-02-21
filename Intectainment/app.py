from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser, os

# init config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.conf'))
for section in ["Server", "Database", "Development"]:
	if section not in config:
		config.add_section(section)

app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

# server configs
app.config["SERVER_NAME"] = f"{(config['Server'].get('server', fallback='localhost'))}:{(config['Server'].get('port', fallback='3000'))}"
app.config["SECRET_KEY"] = config['Server'].get("secretKey", fallback="replaceWhenDeployToDoThings")

## init database
app.config["SQLALCHEMY_DATABASE_URI"] = config['Database'].get("URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = (config['Development'].get("deyMode")) == "yes" #dev state
db = SQLAlchemy(app)
# load tables

#TODO only for dev
if config['Development'].get("devMode"):
	db.create_all()

# load webpages
