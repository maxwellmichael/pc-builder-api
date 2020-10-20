from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from app.build_api import Build, Item

api = Api(app)
api.add_resource(Build, "/build/")
api.add_resource(Item, "/item/<int:buildID>")

CORS(app)
