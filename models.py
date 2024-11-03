import time
import uuid
import datetime
from app import app, db
from  flask_sqlalchemy import SQLAlchemy 

class Jobs(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        uuid = db.Column(db.String(36), unique=True, default=str(uuid.uuid4()))
        title = db.Column(db.String(100), nullable=False)
        details = db.Column(db.Text, nullable=True)
        audio_path = db.Column(db.String(200), nullable=False)
        status = db.Column(db.String(50), default="Processing")
        phrases = db.Column(db.Text, nullable=True)
        text_raw = db.Column(db.Text, default=str())
        text_formatted = db.Column(db.Text, default=str())
        created_at = db.Column(db.Integer, default=datetime.datetime.now().ctime())

# def add(object):
#         db.session.add(object)
#         db.session.commit()

# def update():
#        db.session.commit()

# def query_all(object):
#        return db.session.execute(db.select(object))

with app.app_context():
    db.create_all()