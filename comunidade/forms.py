from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,DecimalField,SelectField,RadioField
from wtforms.validators import DataRequired, Length,Email,EqualTo,ValidationError,Optional
from comunidade.models import *
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed

class Forms_cria_conta(FlaskForm):
    username = StringField("Nome do Usuario",validators=[DataRequired(),Length(2,10)])
    email = StringField("Email",validators=[DataRequired(),Email(),Length(10,30)])
    senha = PasswordField("Senha",validators=[DataRequired(),Length(8,20)])
    confirmar_senha = PasswordField("Confirme a senha",validators=[EqualTo('senha')])
    botao_cria = SubmitField("Cria Conta")
    def validate_email(self,email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        codigo = Codigo.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("Email já existente. Cadastre-se com outro email ou faça login")
            
class Forms_codigo_so(FlaskForm):
    codigo = PasswordField("Codigo",validators=[DataRequired(),Length(4,4)])
    botao = SubmitField("Enviar")
    
class Forms_codigo_email(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email(),Length(10,30)])
    botao_login = SubmitField("confirmar")
    
class Forms_codigo(FlaskForm):
    codigo = PasswordField("Codigo",validators=[DataRequired(),Length(4,4)])
    senha = PasswordField("Nova Senha",validators=[Length(8,20)])
    botao = SubmitField("Enviar")
    
    
class Forms_login_conta(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email(),Length(10,30)])
    senha = PasswordField("Senha",validators=[DataRequired(),Length(6,20)])
    lembra_dados = BooleanField("Lembra Dados")
    botao_login = SubmitField("Entrar")

class Forms_transferir(FlaskForm):
    valor = DecimalField("Valor",validators=[DataRequired()],places=2)
    conta = StringField("Para o Email de quem?",validators=[DataRequired(),Email(),Length(10,30)])
    botao_transferir = SubmitField("Enviar")
    
class Forms_emprestimo(FlaskForm):
    valor = DecimalField("Valor",validators=[DataRequired()],places=2)
    botao_emprestar = SubmitField("Emprestar")
    
class Forms_editar_perfil(FlaskForm):
    username = StringField("Novo nome de Usuario",validators=[DataRequired(),Length(2,10)])
    tags = SelectField("Como você mais se indetifica",choices=[("Pagador","Pagador"),("Anti-Serasa","Anti-Serasa"),("mediano","mediano"),("Enrolado","Enrolado"),("Caloteiro","Caloteiro"),("Risco, Cuidado!","Risco, Cuidado!")])
    foto_perfil = FileField("Alterar foto de Perfil",validators=[FileAllowed(['jpeg','jpg','png'],'Somente imagens são permitidas.')])
    botao_alterar = SubmitField("Confirmar alteração")
    
class Forms_cria_post(FlaskForm):
    titulo = StringField("Criar Titulo",validators=[DataRequired(),Length(2,30)])
    texto = TextAreaField("Criar Texto",validators=[DataRequired()])
    botao_cria_post = SubmitField("Enviar")

class Forms_add_produto(FlaskForm):
    nome = StringField("Nome Produto",validators=[DataRequired(),Length(2,15)])
    preco = DecimalField("Valor",validators=[DataRequired()],places=2)
    foto_produto = FileField("Foto do Produto",validators=[FileAllowed(['jpeg','jpg','png'],'Somente imagens são permitidas.')])
    descricao = TextAreaField("Descricao",validators=[DataRequired(),Length(2,270)])
    tipo = SelectField("Como você mais se indetifica",choices=[("Roupas e acessórios","Roupas e acessórios"),("Eletrônicos","Eletrônicos"),("Produtos para casa","Produtos para casa"),("Cosméticos e produtos de beleza","Cosméticos e produtos de beleza"),("Alimentos e bebidas","Alimentos e bebidas"),("Livros e mídia","Livros e mídia"),("Artigos esportivos","Artigos esportivos"),("Brinquedos e jogos","Brinquedos e jogos")])
    botao_add_prod = SubmitField("Cofirmar")

class Forms_comprar(FlaskForm):
    botao_comprar = SubmitField("Comprar")

