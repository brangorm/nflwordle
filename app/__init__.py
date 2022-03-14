from flask import Flask, session
from flask_bootstrap import Bootstrap
from flask_session import Session
import os

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)#app.config.from_object(Config)
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

Session(app)
from app import routes