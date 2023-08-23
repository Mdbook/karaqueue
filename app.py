"""Flask Login Example and instagram fallowing find"""
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///karaqueue.db'
