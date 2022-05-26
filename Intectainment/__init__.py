from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import argparse, os, sys

parser = argparse.ArgumentParser(description="Intectainment is a infotainment-system")
parser.add_argument('--db_uri', type=str, default=os.environ.get("INTECTAINMENT_DB_URI"),
                    help='URI to database')
parser.add_argument('--secret', type=str, default=os.environ.get("INTECTAINMENT_SECRET"),
                    help='Secret do encode flask-sessions')
args = parser.parse_args()

app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), app.static_folder, "img")
app.config["SECRET_KEY"] = os.environ.get("INTECTAINMENT_SECRET", "replaceWhenDeployToDoThings")


## init database
app.config["SQLALCHEMY_DATABASE_URI"] = args.db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


try:
	db.engine.execute("SELECT 1")
except OperationalError:
	print("Could not connect to database!\nPlease make sure you entered the correct database-URI")
	exit()

# load webpages
from Intectainment.webpages import webpages

if __name__ == '__main__':
	app.run()