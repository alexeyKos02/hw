from sqlalchemy import create_engine
from prometheus_client import Counter
import logging

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

requests_counter = Counter('my_app_requests', 'Number of requests')

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://your_db_user:your_db_password@db:5432/your_db_name'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret'

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

logger.info("Конфигурация загружена")
