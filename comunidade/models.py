from comunidade import database,login_manager
from datetime import datetime
from flask_login import UserMixin
import pytz

brasilia_tz = pytz.timezone('America/Sao_Paulo')


@login_manager.user_loader
def loader_user(id_usuario):
    return Usuario.query.get(int(id_usuario))
    
class Usuario(database.Model,UserMixin):
    __tablename__ = 'usuario'
    id = database.Column(database.Integer,primary_key=True)
    username = database.Column(database.String,nullable=False)
    email = database.Column(database.String,nullable=False,unique=True)
    senha = database.Column(database.TEXT,nullable=False)
    foto = database.Column(database.String,default="https://dl.dropboxusercontent.com/scl/fi/8b52av0u6mvviq2wxutch/x?rlkey=dhd0nodb11kwuadrzvnzab3j8&dl=0")
    post = database.relationship('Post',backref="autor",lazy=True)
    tagpagador = database.Column(database.String,nullable=False,default="Não informado")
    saldo = database.Column(database.FLOAT,nullable=False,default=0)
    
    
class Post(database.Model):
    __tablename__ = 'Feedback'
    id = database.Column(database.Integer,primary_key=True)
    titulo = database.Column(database.String,nullable=False)
    corpo = database.Column(database.Text,nullable=False)
    data_criacao = database.Column(database.String,nullable=False,default=datetime.now(brasilia_tz).strftime('%d-%m-%Y %H:%M:%S'))
    id_usuario = database.Column(database.Integer,database.ForeignKey('usuario.id'),nullable=False)

class Extrato(database.Model):
    __tablename__ = 'Extrato'
    id = database.Column(database.Integer,primary_key=True)
    env_email = database.Column(database.String,nullable=False)
    env_valor = database.Column(database.FLOAT,nullable=False,default=0)
    env_data = database.Column(database.String,nullable=False,default=datetime.now(brasilia_tz).strftime('%d-%m-%Y %H:%M:%S'))
    rec_email = database.Column(database.String,nullable=False)

class Produtos(database.Model):
    __tablename__ = 'Produto'
    id = database.Column(database.Integer,primary_key=True)
    vendedor = database.Column(database.String,nullable=False)
    nome = database.Column(database.String,nullable=False)
    preco = database.Column(database.FLOAT,nullable=False,default=0)
    foto = database.Column(database.String,nullable=False)
    descricao = database.Column(database.Text,nullable=False)
    data_produto = database.Column(database.String,nullable=False,default=datetime.now(brasilia_tz).strftime('%d-%m-%Y %H:%M:%S'))
    tipo = database.Column(database.String,nullable=False)
    
class Comprar(database.Model):
    __tablename__ = 'Comprar'
    id = database.Column(database.Integer,primary_key=True)
    data_venda = database.Column(database.String,nullable=False,default=datetime.now(brasilia_tz).strftime('%d-%m-%Y %H:%M:%S'))
    comprador = database.Column(database.String,nullable=False)
    
class Codigo(database.Model):
    __tablename__ = "Codigo"
    id = database.Column(database.Integer,primary_key=True)
    email = database.Column(database.String,nullable=False,unique=True)
    codigo = database.Column(database.Integer,nullable=False)
    situacao = database.Column(database.Integer,nullable=False,default=0)
