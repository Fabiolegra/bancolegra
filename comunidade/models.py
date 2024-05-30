"""Módulo que reúne todas as tabelas e colunas do banco de dados"""
from datetime import datetime
import pytz
from flask_login import UserMixin
from comunidade import database, login_manager

# Constantes
IMAGEM_BASE_URL = "https://dl.dropboxusercontent.com"
IMAGEM_PATH = "/scl/fi/8b52av0u6mvviq2wxutch/x?rlkey=dhd0nodb11kwuadrzvnzab3j8&dl=0"
brasilia_tz = pytz.timezone('America/Sao_Paulo')

def data_atual_formatada():
    """ Função para obter data atual formatada """
    return datetime.now(brasilia_tz).strftime('%d/%m/%Y %H:%M:%S')

@login_manager.user_loader
def load_user(id_usuario):
    """
    Função de carregamento de usuário para o Flask-Login
    """
    return Usuario.query.get(int(id_usuario))

# Modelo de Usuário
class Usuario(database.Model, UserMixin):
    """ 
    Tabela Usuario:
        colunas:
            id : Integer
            username: String
            email: String
            senha: TEXT
            foto: String
            post: outra Tabela
            tagpagador: String
            saldo: FLOAT
    """
    __tablename__ = 'usuario'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.TEXT, nullable=False)
    foto = database.Column(database.String, default=IMAGEM_BASE_URL + IMAGEM_PATH)
    post = database.relationship('Post', backref="autor", lazy=True)
    tagpagador = database.Column(database.String, nullable=False, default="Não informado")
    saldo = database.Column(database.FLOAT, nullable=False, default=0)

# Modelo de Post (Feedback)
class Post(database.Model):
    """
    Tabela Feedback
        colunas:
        id : Integer
        titulo : String
        corpo : TEXT
        data_criacao : String
        id_usuario : Integer
    """
    __tablename__ = 'Feedback'
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    data_criacao = database.Column(
        database.String,
        nullable=False,
        default=data_atual_formatada
    )
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

# Modelo de Extrato
class Extrato(database.Model):
    """ Tabela Extratos """
    __tablename__ = 'Extrato'
    id = database.Column(database.Integer, primary_key=True)
    env_email = database.Column(database.String, nullable=False)
    env_valor = database.Column(database.FLOAT, nullable=False, default=0)
    env_data = database.Column(
        database.String,
        nullable=False,
        default=data_atual_formatada
    )
    rec_email = database.Column(database.String, nullable=False)

# Modelo de Produtos
class Produtos(database.Model):
    """ Tabela Produtos """
    __tablename__ = 'Produto'
    id = database.Column(database.Integer, primary_key=True)
    vendedor = database.Column(database.String, nullable=False)
    nome = database.Column(database.String, nullable=False)
    preco = database.Column(database.FLOAT, nullable=False, default=0)
    foto = database.Column(database.String, nullable=False)
    descricao = database.Column(database.Text, nullable=False)
    data_produto = database.Column(
        database.String,
        nullable=False,
        default=data_atual_formatada
    )
    tipo = database.Column(database.String, nullable=False)

# Modelo de Compra
class Comprar(database.Model):
    """ Tabela Comprar """
    __tablename__ = 'Comprar'
    id = database.Column(database.Integer, primary_key=True)
    data_venda = database.Column(
        database.String,
        nullable=False,
        default=data_atual_formatada
    )
    comprador = database.Column(database.String, nullable=False)

# Modelo de Código
class Codigo(database.Model):
    """ Tabela Codigo """
    __tablename__ = "Codigo"
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String, nullable=False, unique=True)
    codigo = database.Column(database.Integer, nullable=False)
    situacao = database.Column(database.Integer, nullable=False, default=0)
