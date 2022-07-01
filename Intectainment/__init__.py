from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import dotenv, os, sys

dotenv.load_dotenv()

app = Flask(
    __name__, template_folder="./webpages/templates", static_folder="./webpages/static"
)

app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(__file__), app.static_folder, "img"
)
app.config["SECRET_KEY"] = os.getenv("INTECTAINMENT_SECRET")


## init database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("INTECTAINMENT_DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.before_first_request
def db_test():
    try:
        db.engine.execute("SELECT 1")
    except OperationalError:
        print(
            "Could not connect to database!\nPlease make sure you entered the correct database-URI"
        )
        exit()


# load webpages
import Intectainment.webpages

if __name__ == "__main__":
    app.run()
