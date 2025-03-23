import logging
from flask import Blueprint, jsonify, request
from . import db
from .models import User, BusinessData
from flask_jwt_extended import jwt_required, create_access_token
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flasgger import swag_from

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

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
@swag_from({
    'summary': 'Регистрация нового пользователя',
    'description': 'Создает нового пользователя в системе, если имя пользователя не занято.',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'description': 'Объект с данными для регистрации нового пользователя',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'user123'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123'
                    }
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Пользователь успешно создан',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'msg': {
                                'type': 'string',
                                'example': 'User created successfully'
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Неправильные данные (например, если имя пользователя уже существует)',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'msg': {
                                'type': 'string',
                                'example': 'Username already exists'
                            }
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'msg': {
                                'type': 'string',
                                'example': 'Internal Server Error'
                            }
                        }
                    }
                }
            }
        }
    }
})
def register():

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

@routes.route('/login', methods=['POST'])
@swag_from({
    'summary': 'Аутентификация пользователя',
    'description': 'Проверка логина и пароля пользователя. В случае успеха возвращает токен доступа.',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'description': 'Объект с данными для аутентификации пользователя',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'user123'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123'
                    }
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Токен доступа получен',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {
                        'type': 'string',
                        'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6InVzZXIxMjMifQ.Kxu-N2i1qI_wJf1BbdsW0Yf07v0dHwzLNr_mrBYLMJ4'
                    }
                }
            }
        },
        401: {
            'description': 'Неправильные данные (неверный логин или пароль)',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Bad username or password'
                    }
                }
            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
def login():
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

@routes.route('/create', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': 'Создание данных',
    'description': 'Создание новых данных для бизнес-логики. Должен быть передан объект с необходимыми данными.',
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'description': 'Объект с данными для создания',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'string',
                        'example': 'Some important business data'
                    }
                },
                'required': ['data']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Данные успешно созданы',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Data created successfully'
                    }
                }
            }
        },
        400: {
            'description': 'Отсутствуют данные для создания',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Missing data'
                    }
                }
            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
def create():
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
@swag_from({
    'summary': 'Получение данных',
    'description': 'Получение списка всех данных из базы данных. Требуется авторизация.',
    'responses': {
        200: {
            'description': 'Токен доступа получен',
            'schema': {
                'type': 'array',
                    'items': {
        'type': 'string',
        'example': "1" 
    }

            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
@jwt_required()
def get():
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
@swag_from({
    'summary': 'Обновление данных',
    'description': 'Обновление данных для указанного идентификатора. Требуется авторизация.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'Идентификатор данных, которые нужно обновить',
            'required': True,
            'schema': {
                'type': 'integer',
                'example': 1
            }
        },
        {
            'name': 'data',
            'in': 'body',
            'description': 'Новые данные для обновления',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'string',
                        'example': 'Updated business data'
                    }
                },
                'required': ['data']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Данные успешно обновлены',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Data updated successfully'
                    }
                }
            }
        },
        400: {
            'description': 'Отсутствуют новые данные',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Missing data'
                    }
                }
            }
        },
        404: {
            'description': 'Данные с таким идентификатором не найдены',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Data not found'
                    }
                }
            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
@jwt_required()
def update(id):
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
@swag_from({
    'summary': 'Удаление данных',
    'description': 'Удаление данных с указанным идентификатором. Требуется авторизация.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'Идентификатор данных, которые нужно удалить',
            'required': True,
            'schema': {
                'type': 'integer',
                'example': 1
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Данные успешно удалены',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Data deleted successfully'
                    }
                }
            }
        },
        404: {
            'description': 'Данные с таким идентификатором не найдены',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Data not found'
                    }
                }
            }
        },
        500: {
            'description': 'Ошибка на сервере',
            'content': {
                'application/json': {
                    'example': {
                        'msg': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
def delete(id):
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