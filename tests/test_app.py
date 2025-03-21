import sys
import os
from flask_jwt_extended import jwt_required, create_access_token

# Добавляем родительскую директорию в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.app_context():
        db.create_all()
    
    yield app.test_client()
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_register(client):
    # Тест регистрации пользователя
    response = client.post('/register', json={'username': 'test_user', 'password': 'test_password'})
    assert response.status_code == 201
    assert response.json['msg'] == 'User created successfully'

def test_register_existing_user(client):
    # Тест регистрации существующего пользователя
    client.post('/register', json={'username': 'test_user', 'password': 'test_password'})
    response = client.post('/register', json={'username': 'test_user', 'password': 'test_password'})
    assert response.status_code == 400
    assert response.json['msg'] == 'Username already exists'

def test_register_missing_credentials(client):
    # Тест регистрации без указания логина или пароля
    response = client.post('/register', json={'username': 'test_user'})
    assert response.status_code == 400
    assert response.json['msg'] == 'Missing username or password'

def test_login(client):
    # Тест аутентификации пользователя
    client.post('/register', json={'username': 'test_user', 'password': 'test_password'})
    response = client.post('/login', json={'username': 'test_user', 'password': 'test_password'})
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_bad_credentials(client):
    # Тест аутентификации с неверными данными
    client.post('/register', json={'username': 'test_user', 'password': 'test_password'})
    response = client.post('/login', json={'username': 'test_user', 'password': 'wrong_password'})
    assert response.status_code == 401
    assert response.json['msg'] == 'Bad username or password'

def test_login_missing_credentials(client):
    # Тест аутентификации без указания логина или пароля
    response = client.post('/login', json={'username': 'test_user'})
    assert response.status_code == 401
    assert response.json['msg'] == 'Bad username or password'

def test_create(client):
    app = client.application
    with app.app_context():
        access_token = create_access_token(identity='test_user')
    
    response = client.post('/create', json={'data': 'Test data'}, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201

def test_get(client):
    app = client.application
    with app.app_context():
        access_token = create_access_token(identity='test_user')
    
    response = client.get('/get', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

def test_update(client):
    app = client.application
    with app.app_context():
        access_token = create_access_token(identity='test_user')
    
    # Сначала создайте данные для обновления
    client.post('/create', json={'data': 'Test data'}, headers={'Authorization': f'Bearer {access_token}'})
    
    response = client.put('/update/1', json={'data': 'New data'}, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

def test_delete(client):
    app = client.application
    with app.app_context():
        access_token = create_access_token(identity='test_user')
    
    # Сначала создайте данные для удаления
    client.post('/create', json={'data': 'Test data'}, headers={'Authorization': f'Bearer {access_token}'})
    
    response = client.delete('/delete/1', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
