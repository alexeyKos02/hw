from . import db

def create_tables():
    with db.app.app_context():
        db.create_all()
