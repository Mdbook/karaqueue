"""Flask Login Example and instagram fallowing find"""
from flask import Flask
from flask_mobility import Mobility

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///karaqueue.db'
Mobility(app)