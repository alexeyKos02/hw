from . import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

class BusinessData(db.Model):
    __tablename__ = 'business_data'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
