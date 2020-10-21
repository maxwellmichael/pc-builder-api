from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv



# Fetches the Values From the Environment Variables
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)


app = Flask(__name__)

# Loads the .env Files
load_dotenv()

# Sets the values of those depend on your setup
POSTGRESQL_URL = get_env_variable("POSTGRESQL_URL")
POSTGRESQL_USER = get_env_variable("POSTGRESQL_USER")
POSTGRESQL_PW = get_env_variable("POSTGRESQL_PW")
POSTGRESQL_DB = get_env_variable("POSTGRESQL_DB")
POSTGRESQL_HOST = get_env_variable("POSTGRESQL_HOST")
POSTGRESQL_PORT = get_env_variable("POSTGRESQL_PORT")
SECRET_KEY = get_env_variable("SECRET_KEY")

# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PW}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # silence the deprecation warning
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)

from app.build_api import Build, Item

api = Api(app)
api.add_resource(Build, "/build/")
api.add_resource(Item, "/item/<int:buildID>")

CORS(app)
