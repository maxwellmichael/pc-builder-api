from app import db, bcrypt, app
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)


class UsersModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    isOnline = db.Column(db.Boolean, default=False, nullable=True)
    isAdmin = db.Column(db.Boolean, default=False, nullable=False)
    lastOnline = db.Column(db.DateTime, default=datetime.datetime.now)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    modifiedOn = db.Column(db.DateTime, nullable=True)
    builds = db.relationship("BuildsModel", backref=db.backref("user", uselist=False))
    publicId = db.Column(db.String(256), nullable=False, unique=True)  # ID used to encode the JWT Token

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password, method="sha256")
        self.isAdmin = False
        self.isOnline = False
        self.createdOn = datetime.datetime.now()
        self.modifiedOn = datetime.datetime.now()
        self.lastOnline = datetime.datetime.now()
        self.publicId = str(uuid.uuid4())

    # Creates aand Saves User Query in the Database
    @staticmethod
    def userRegister(name, email, password):
        user = UsersModel.query.filter_by(email=email).first()
        if user:
            return {"status": None, "message": "Email Already Exists!"}
        user = UsersModel(name, email, password)
        db.session.add(user)
        db.session.commit()
        return {"status": "ok"}

    # When User Login is Successful returns access token and refresh token
    @staticmethod
    def userLogin(email, password):
        user = UsersModel.query.filter_by(email=email).first()
        if not user:
            return {"status": None, "message": "Invalid Email Specified", "status_code": 404}

        hash_result = check_password_hash(user.password, password)
        if hash_result:
            user.lastOnline = datetime.datetime.now()
            user.isOnline = True
            db.session.add(user)
            db.session.commit()
            tokens = {
                'access_token': create_access_token(identity=user.publicId),
                'refresh_token': create_refresh_token(identity=user.publicId)
            }
            # token = jwt.encode({"public_id": user.publicId, "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=1)},app.config["SECRET_KEY"])
            return {"status": "ok", "tokens": tokens, "status_code": 200}
        else:
            return {"status": None, "message": "Invalid Password", "status_code": 404}


class BuildsModel(db.Model):
    __tablename__ = "builds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(400), nullable=True)
    totalValue = db.Column(db.Float, nullable=True)
    dateCreated = db.Column(db.DateTime, default=datetime.datetime.now)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))
    items = db.relationship("ItemsModel", backref=db.backref("build", uselist=False))


class ItemsModel(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String(1000), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    totalRating = db.Column(db.Integer, nullable=True)
    starRating = db.Column(db.Float, nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))
    buildId = db.Column(db.Integer, db.ForeignKey("builds.id"))
