from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import datetime


# Fetches the Values From the Environment Variables
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)


app = Flask(__name__)
jwt_ext = JWTManager(app)

bcrypt = Bcrypt(app)

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
JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=5)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(hours=168)


#app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PW}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # silence the deprecation warning
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SECURE'] = False # True if Connection is https
app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = "csrf_access_token"
app.config['JWT_REFRESH_CSRF_HEADER_NAME'] = "csrf_refresh_token"
app.config['DEBUG'] = False
db = SQLAlchemy(app)

from app.build_api import Build, Item, UserLogin, UserLogout, UserRegister, RefreshAccessToken

api = Api(app)
api.add_resource(Build, "/build/")
api.add_resource(Item, "/item/<int:buildID>")
api.add_resource(UserLogin, "/userlogin")
api.add_resource(UserLogout, "/userlogout")
api.add_resource(UserRegister, "/userregister")
api.add_resource(RefreshAccessToken, "/refreshaccesstoken")



CORS(app,resources={r"/*": {"origins": ["http://react.pc-builder-api.herokuapp.com:3000", "http://192.168.1.2:3000", "localhost:3000"]}},
     supports_credentials=True)
