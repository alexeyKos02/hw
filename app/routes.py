import logging
from flask import Blueprint, jsonify, request
from . import db
from .models import User, BusinessData
from flask_jwt_extended import jwt_required, create_access_token
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

LOG_LEVEL = logging.DEBUG  # Или logging.DEBUG для более подробных логов
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)  # Создаем логгер

requests_total = Counter('requests_total', 'Total number of requests')
register_requests = Counter('register_requests', 'Number of register requests')
login_requests = Counter('login_requests', 'Number of login requests')
create_requests = Counter('create_requests', 'Number of create requests')
get_requests = Counter('get_requests', 'Number of get requests')
update_requests = Counter('update_requests', 'Number of update requests')
delete_requests = Counter('delete_requests', 'Number of delete requests')
error_counter = Counter('errors_total', 'Total number of errors')

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    """Получение информации о приложении
    
    ---
    get:
      summary: Получение информации о приложении
      description: Возвращает информацию о приложении
      responses:
        200:
          description: Информация получена
          content:
            text/plain:
              schema:
                type: string
    """
    logger.info("GET /")
    logger.info(f"Запрос: {request}")
    requests_total.inc()
    logger.info("Конфигурация тут")
    try:
        return 'OK'
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

# Регистрация пользователя
@routes.route('/register', methods=['POST'])
def register():
    """Регистрация пользователя
    
    ---
    post:
      summary: Регистрация пользователя
      description: Создает нового пользователя
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        201:
          description: Пользователь создан
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
        400:
          description: Недостаточно данных
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
    """
    logger.info("POST /register")
    logger.info(f"Запрос: {request.json}")
    requests_total.inc()
    register_requests.inc()
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if username and password:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({"msg": "Username already exists"}), 400
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"Ответ: {jsonify({'msg': 'User created successfully'})}")
            return jsonify({"msg": "User created successfully"}), 201
        return jsonify({"msg": "Missing username or password"}), 400
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

# Аутентификация
@routes.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя
    
    ---
    post:
      summary: Аутентификация пользователя
      description: Возвращает токен доступа
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: Токен доступа получен
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
        401:
          description: Неправильные данные
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
    """
    logger.info("POST /login")
    logger.info(f"Запрос: {request.json}")
    requests_total.inc()
    login_requests.inc()
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            access_token = create_access_token(identity=username)
            logger.info(f"Ответ: {jsonify(access_token=access_token)}")
            return jsonify(access_token=access_token), 200
        return jsonify({"msg": "Bad username or password"}), 401
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

# CRUD операции
@routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    """Создание данных
    
    ---
    post:
      summary: Создание данных
      description: Создает новые данные
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - data
              properties:
                data:
                  type: string
      responses:
        201:
          description: Данные созданы
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
        400:
          description: Недостаточно данных
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
    """
    logger.info("POST /create")
    logger.info(f"Запрос: {request.json}")
    requests_total.inc()
    create_requests.inc()
    try:
        data = request.json.get('data', None)
        if data:
            new_data = BusinessData(data=data)
            db.session.add(new_data)
            db.session.commit()
            logger.info(f"Ответ: {jsonify({'msg': 'Data created successfully'})}")
            return jsonify({"msg": "Data created successfully"}), 201
        return jsonify({"msg": "Missing data"}), 400
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

@routes.route('/get', methods=['GET'])
@jwt_required()
def get():
    """Получение данных
    
    ---
    get:
      summary: Получение данных
      description: Возвращает все данные
      security:
        - bearerAuth: []
      responses:
        200:
          description: Данные получены
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string
    """
    logger.info("GET /get")
    logger.info(f"Запрос: {request}")
    requests_total.inc()
    get_requests.inc()
    try:
        data = BusinessData.query.all()
        logger.info(f"Ответ: {jsonify([item.data for item in data])}")
        return jsonify([item.data for item in data]), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

@routes.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update(id):
    """Обновление данных
    
    ---
    put:
      summary: Обновление данных
      description: Обновляет данные по ID
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          required: true
          description: ID данных
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - data
              properties:
                data:
                  type: string
      responses:
        200:
          description: Данные обновлены
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
        400:
          description: Недостаточно данных
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
        404:
          description: Данные не найдены
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
    """
    logger.info(f"PUT /update/{id}")
    logger.info(f"Запрос: {request.json}")
    requests_total.inc()
    update_requests.inc()
    try:
        data = BusinessData.query.get(id)
        if data:
            new_data = request.json.get('data', None)
            if new_data:
                data.data = new_data
                db.session.commit()
                logger.info(f"Ответ: {jsonify({'msg': 'Data updated successfully'})}")
                return jsonify({"msg": "Data updated successfully"}), 200
            return jsonify({"msg": "Missing data"}), 400
        return jsonify({"msg": "Data not found"}), 404
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

@routes.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    """Удаление данных
    
    ---
    delete:
      summary: Удаление данных
      description: Удаляет данные по ID
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          required: true
          description: ID данных
      responses:
        200:
          description: Данные удалены
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
        404:
          description: Данные не найдены
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
    """
    logger.info(f"DELETE /delete/{id}")
    logger.info(f"Запрос: {request}")
    requests_total.inc()
    delete_requests.inc()
    try:
        data = BusinessData.query.get(id)
        if data:
            db.session.delete(data)
            db.session.commit()
            logger.info(f"Ответ: {jsonify({'msg': 'Data deleted successfully'})}")
            return jsonify({"msg": "Data deleted successfully"}), 200
        return jsonify({"msg": "Data not found"}), 404
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        error_counter.inc()
        return jsonify({"msg": "Internal Server Error"}), 500

@routes.route('/metrics')
def metrics():
    """ Exposes application metrics in a Prometheus-compatible format. """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}