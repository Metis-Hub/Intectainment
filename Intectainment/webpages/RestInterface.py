from Intectainment.app import db
from Intectainment.database.models import Category, Channel
from Intectainment.webpages.webpages import ap

from flask import request, jsonify

##### Category Accesspoint ######
#TODO: remove?
@ap.route("/category", methods=["PUT", "GET", "DELETE"])
def categoryREST():
	if request.method == "GET":
		"""returns a list of categories"""
		return jsonify([c.name for c in Category.query.all()])

	elif request.method == "PUT":
		"""inserts a category into the database"""
		value = request.form.get("name")
		if not value:
			return "Argument required", 403
		if not Category.query.filter_by(name=value).first():
			category = Category(name=value)
			db.session.add(category)
			db.session.commit()
			return "", 201
		return "already in database", 403

	elif request.method == "DELETE":
		"""removes a category from the database"""
		value = request.form.get("name")
		if not value:
			return "Argument required", 403
		Category.query.filter_by(name=value).delete()
		db.session.commit()
		return "", 202
	pass


@ap.route("/channel", methods=["PUT", "GET", "DELETE"])
def channelREST():
	if request.method == "GET":
		"""returns a list of categories"""
		return jsonify([c.name for c in Channel.query.all()])

	elif request.method == "PUT":
		"""inserts a category into the database"""
		value = request.form.get("name")
		if not value:
			return "Argument required", 403
		if not Category.query.filter_by(name=value).first():
			channel = Channel(name=value)
			db.session.add(channel)
			db.session.commit()
			return "", 201
		return "already in database", 403

	elif request.method == "DELETE":
		"""removes a category from the database"""
		value = request.form.get("name")
		if not value:
			return "Argument required", 403
		Channel.query.filter_by(name=value).delete()
		db.session.commit()
		return "", 202
	pass