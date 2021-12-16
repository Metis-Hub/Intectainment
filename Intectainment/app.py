import os
from flask import Flask

app = Flask(__name__, template_folder="./webpages/templates", static_folder="./webpages/static")

# Config
app.config["SERVER_NAME"] = "localhost:80"
app.config["SECRET_KEY"] = "replaceWhenDeployToDoThings"

from Intectainment.webpages import webpages