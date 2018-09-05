from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'e2f6901qf5d4b6587c4ed6d8a'

db = SQLAlchemy(app)

from flaskblog import routes