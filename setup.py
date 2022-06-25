import os
import Intectainment.datamodels as dbm
from Intectainment import db


# create content subdirectories
for dir in ["Intectainment/content/posts", "Intectainment/content/img"]:
    path = os.path.join(os.path.dirname(__file__), dir)
    if not os.path.exists(path):
        os.makedirs(path)

db.create_all()
