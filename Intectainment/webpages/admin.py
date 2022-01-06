from Intectainment.app import app
from flask import Blueprint

admin: Blueprint = Blueprint("admin", __name__, url_prefix="/admin")








app.register_blueprint(admin)