from sqlalchemy import create_engine

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://your_db_user:your_db_password@db:5432/your_db_name'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://aleksej:mypassword@localhost/mydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret'

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
