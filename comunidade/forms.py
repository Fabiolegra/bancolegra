"""Módulo de formulários para CPF."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    DecimalField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError
)
from comunidade.models import Usuario

class FormsLoginConta(FlaskForm):
    """Formulario de login"""
    email = StringField("Email", validators=[DataRequired(), Email(), Length(10, 30)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    lembra_dados = BooleanField("Lembrar Dados")
    botao_login = SubmitField("Entrar")

class FormsCriaConta(FlaskForm):
    """Formulario de criação de conta"""
    username = StringField("Nome do Usuário", validators=[DataRequired(), Length(2, 10)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(10, 30)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(8, 20)])
    confirmar_senha = PasswordField("Confirme a senha", validators=[EqualTo('senha')])
    botao_cria = SubmitField("Criar Conta")

    def validate_email(self, email):
        """Metodo que checar se o email já existe no banco de dados"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("Email já existente. Cadastre-se com outro email ou faça login")

class FormsCodigoSO(FlaskForm):
    """Formulario do codigo de confirmação"""
    codigo = PasswordField("Código", validators=[DataRequired(), Length(4, 4)])
    botao = SubmitField("Enviar")

class FormsEditarPerfil(FlaskForm):
    """Formulario que altera o perfil do usuario"""
    username = StringField("Novo nome de Usuário", validators=[DataRequired(), Length(2, 10)])
    tags = SelectField("Como você mais se identifica", choices=[
        ("Pagador", "Pagador"),
        ("Anti-Serasa", "Anti-Serasa"),
        ("mediano", "Mediano"),
        ("Enrolado", "Enrolado"),
        ("Caloteiro", "Caloteiro"),
        ("Risco, Cuidado!", "Risco, Cuidado!")
    ])
    foto_perfil = FileField(
        "Alterar foto de Perfil",
        validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Somente imagens são permitidas.')])
    botao_alterar = SubmitField("Confirmar alteração")

class FormsCodigoEmail(FlaskForm):
    """Formulario que obtem o email"""
    email = StringField("Email", validators=[DataRequired(), Email(), Length(10, 30)])
    botao_login = SubmitField("Confirmar")

class FormsCodigo(FlaskForm):
    """Formulario para trocar a senha com confirmação do codigo"""
    codigo = PasswordField("Código", validators=[DataRequired(), Length(4, 4)])
    senha = PasswordField("Nova Senha", validators=[Length(8, 20)])
    botao = SubmitField("Enviar")

class FormsTransferir(FlaskForm):
    """Formulario de transferencia entre contas"""
    valor = DecimalField("Valor", validators=[DataRequired()], places=2)
    conta = StringField(
            "Email destinatário: ",
            validators=[DataRequired(), Email(), Length(10, 30)])
    botao_transferir = SubmitField("Enviar")

class FormsEmprestimo(FlaskForm):
    """Formulario de emprestimo"""
    valor = DecimalField("Valor", validators=[DataRequired()], places=2)
    botao_emprestar = SubmitField("Emprestar")

class FormsCriaPost(FlaskForm):
    """Formulario para criar um feedback"""
    titulo = StringField("Criar Título", validators=[DataRequired(), Length(2, 30)])
    texto = TextAreaField("Criar Texto", validators=[DataRequired()])
    botao_cria_post = SubmitField("Enviar")

class FormsAddProduto(FlaskForm):
    """Formulario para adicionar Produto"""
    nome = StringField("Nome Produto", validators=[DataRequired(), Length(2, 15)])
    preco = DecimalField("Valor", validators=[DataRequired()], places=2)
    foto_produto = FileField(
        "Foto do Produto",
        validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Somente imagens são permitidas.')])
    descricao = TextAreaField("Descrição", validators=[DataRequired(), Length(2, 270)])
    tipo = SelectField("Como você mais se identifica", choices=[
        ("Roupas e acessórios", "Roupas e acessórios"),
        ("Eletrônicos", "Eletrônicos"),
        ("Produtos para casa", "Produtos para casa"),
        ("Cosméticos e produtos de beleza", "Cosméticos e produtos de beleza"),
        ("Alimentos e bebidas", "Alimentos e bebidas"),
        ("Livros e mídia", "Livros e mídia"),
        ("Artigos esportivos", "Artigos esportivos"),
        ("Brinquedos e jogos", "Brinquedos e jogos")
    ])
    botao_add_prod = SubmitField("Confirmar")

class FormsComprar(FlaskForm):
    """ Formulario para Comprar produto"""
    botao_comprar = SubmitField("Comprar")
