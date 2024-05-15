from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import DeclarativeBase
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
import sqlalchemy
import psycopg2
import os 
from dotenv import load_dotenv

load_dotenv()
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
URL_DATABASE = os.getenv('URL_DATABASE')

class Base(DeclarativeBase):
  pass 

database = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.config["SECRET_KEY"] = APP_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = URL_DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Necessario login para acessar essa pagina!"
login_manager.login_message_category = "alert-info"
database.init_app(app)
from comunidade import routes
