from flask import Blueprint, jsonify, request
from . import db
from .models import User, BusinessData
from flask_jwt_extended import jwt_required, create_access_token
from prometheus_client import Counter

requests_total = Counter('requests_total', 'Total number of requests')

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    requests_total.inc()
    return 'OK'

# Регистрация пользователя
@routes.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username and password:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"msg": "Username already exists"}), 400
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    return jsonify({"msg": "Missing username or password"}), 400

# Аутентификация
@routes.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

# CRUD операции
@routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    data = request.json.get('data', None)
    if data:
        new_data = BusinessData(data=data)
        db.session.add(new_data)
        db.session.commit()
        return jsonify({"msg": "Data created successfully"}), 201
    return jsonify({"msg": "Missing data"}), 400

@routes.route('/get', methods=['GET'])
@jwt_required()
def get():
    data = BusinessData.query.all()
    return jsonify([item.data for item in data]), 200

@routes.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update(id):
    data = BusinessData.query.get(id)
    if data:
        new_data = request.json.get('data', None)
        if new_data:
            data.data = new_data
            db.session.commit()
            return jsonify({"msg": "Data updated successfully"}), 200
        return jsonify({"msg": "Missing data"}), 400
    return jsonify({"msg": "Data not found"}), 404

@routes.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    data = BusinessData.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({"msg": "Data deleted successfully"}), 200
    return jsonify({"msg": "Data not found"}), 404
