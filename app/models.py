from app import db
import datetime


class BuildsModel(db.Model):
    __tablename__ = "builds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    totalValue = db.Column(db.Float, nullable=True)
    dateCreated = db.Column(db.DateTime, default=datetime.datetime.now)
    items = db.relationship("ItemsModel", backref=db.backref("build", uselist=False))



class ItemsModel(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String(1000), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    buildId = db.Column(db.Integer, db.ForeignKey("builds.id"))



