import os

if not os.path.exists("Intectainment/content/setup.lock"):
    for dir in ["Intectainment/content/posts", "Intectainment/content/img"]:
        path = os.path.join(os.path.dirname(__file__), dir)
        if not os.path.exists(path):
            os.makedirs(path)

    import Intectainment.datamodels as dbm
    from Intectainment import db

    db.create_all()
    open("Intectainment/content/setup.lock", "x").close()
