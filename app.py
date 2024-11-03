from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcriptor.db'
db = SQLAlchemy(app)


if __name__ == "__main__":
    from views import *
    app.run(debug=True) 
