import os
from random import randint

import re
import smtplib
import secrets
import dropbox
from dotenv import load_dotenv
from PIL import Image,ImageOps
from flask import flash,request,abort,render_template_string
from flask_login import login_user,logout_user,current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from comunidade import app,database,bcrypt
from comunidade.models import *


load_dotenv()
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD_EMAIL = os.getenv('PASSWORD_EMAIL')
API_KEY_DROPBOX = os.getenv('API_KEY_DROPBOX')

#-------------------cria tabelas -------------------
def create_tables():
    with app.app_context():
        database.create_all()

# -----------------login e cadastro --------------------
def funcaoLogin(form,codigo):
    """
    o que ele faz:
        Realiza o login do usuário, verificando a existência do usuário, a situação do email por meio de um código de verificação, e a senha do usuário.
    argumentos:
        login_conta: O resultado do formulário de login.
        codigo: A situação do código de verificação do email.
    
    """
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario:
            senha = usuario.senha
            senha_agora = form.senha.data
            senha_certa = bcrypt.check_password_hash(senha,senha_agora)
            if codigo.situacao ==1:
                if senha_certa:
                    login_user(usuario,remember=form.lembra_dados.data)
                    flash(f"O login foi feito no email {form.email.data}","alert-success")
                    par_next = request.args.get("next")
                    if par_next:
                        return 1#se fez login -> ele volta para a página que eles estava visualizando antes de ser direcionados para a página de login
                    else:
                        return 2#se fez login redirect carteira
                else:
                    flash(f"Senha incorreta","alert-danger")
            else:
                return 4
                flash(f"Email não confirmado","alert-danger")
        else:
            flash(f"email não existente. Crie uma Conta","alert-danger")
            return 3 # se não existe conta com o email redirect criar conta

def funcaoCriarconta(form):
    """
    O que faz: 
        Cria uma conta de usuário, gerando um hash com a senha, adicionando um novo usuário ao banco de dados, gerando e enviando um código de verificação por email.
    Argumentos:
        form: O formulário de criação de conta.
    """
    if form.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form.senha.data).decode('utf8')
        with app.app_context():
            usuario = Usuario(email=form.email.data,senha=senha_crypt,username=form.username.data)
            database.session.add(usuario)
            codigo = randint(1000,9999)
            codigo_user = Codigo(email=form.email.data,codigo=codigo)
            database.session.add(codigo_user)
            enviar_email(form.email.data,codigo)
            database.session.commit()
        flash(f"Conta Criada! mas antes cofirme o seu email {form.email.data}",'alert-info')
        return 1
        

# -------------------- email -----------------

def enviar_email(destino,codigo):
    """
    O que faz: 
        Envia um email com um código de verificação.
    Argumentos:
        destino: O email de destino.
        codigo: O código de verificação.
    """
    # Configurações do servidor SMTP do Gmail
    smtp_server = 'smtp.gmail.com'
    port = 587  # Porta TLS para o Gmail
    # Seu email e senha do Gmail
    sender_email = SENDER_EMAIL
    password = PASSWORD_EMAIL
    # Criar uma mensagem
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = destino
    msg['Subject'] = 'Código BankLegra'
    # Ler o conteúdo do arquivo HTML
    with open('comunidade/templates/enviar_email.html', 'r') as file:
        html = file.read()
    html = render_template_string(html,codigo=codigo) 
    msg.attach(MIMEText(html, 'html'))
    # Conectar ao servidor SMTP do Gmail
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    # Enviar email
    text = msg.as_string()
    server.sendmail(sender_email, destino, text)
    # Fechar conexão
    server.quit()


def salvar_imagem(imagem, pasta):
    """
    O que faz: 
        Salva uma imagem na nuvem (dropbox) e retorna o link da imagem.
    Argumentos:
        imagem: A imagem a ser salva.
        pasta: A pasta onde a imagem deve ser armazenada.
    """
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome = nome.replace(" ", "")
    nome_do_arquivo = nome + codigo + extensao
    caminho_da_imagem = os.path.join(app.root_path, f'static/{pasta}/', nome_do_arquivo)
    tamanho = (300, 300)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida = ImageOps.exif_transpose(imagem_reduzida)
    # Redimensiona a imagem para exatamente 300x300, cortando se necessário
    imagem_reduzida.thumbnail(tamanho)
    # Cria uma imagem em branco de 300x300 para garantir o tamanho final
    imagem_final = Image.new("RGB", tamanho, (255, 255, 255))
    imagem_final.paste(imagem_reduzida, ((
        tamanho[0] - imagem_reduzida.size[0]) // 2,
        (tamanho[1] - imagem_reduzida.size[1]) // 2))
    imagem_final.save(caminho_da_imagem)
    # Configuração da autenticação
    dbx = dropbox.Dropbox(API_KEY_DROPBOX)
    # Caminho local do arquivo a ser enviado
    local_path = caminho_da_imagem
    # Caminho remoto no Dropbox
    remote_path = f"/banco/{pasta}/{nome_do_arquivo}"
    # Upload do arquivo
    with open(local_path, 'rb') as f:
        dbx.files_upload(f.read(), remote_path)
    # Pegar o link compartilhável
    shared_link = dbx.sharing_create_shared_link(remote_path)
    # Modificar o link para o formato direto de visualização da imagem 
    direct_link = shared_link.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '')
    return direct_link



# ----------------- Perfil --------------------

def funcaoEditarPerfil(form):
    """
    O que faz: 
        Edita o perfil do usuário, atualizando o nome de usuário, tags e foto de perfil e senha.
    Argumentos:
        form: O formulário de edição de perfil.
    """
    if request.method == "GET":
        form.username.data = current_user.username
    elif form.validate_on_submit() and 'botao_alterar' in request.form:
        current_user.username = form.username.data
        current_user.tagpagador = form.tags.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data,'foto_perfil')
            current_user.foto = nome_imagem
        database.session.commit()
        flash(f"Perfil atualizado","alert-success")
        return True
    else:
        flash(f"Perfil Inalterado","alert-danger")
        return True
        
def funcaoTrocarsenhaEmail(email):
    """
    O que faz: 
        Inicia o processo de troca de senha via email, enviando um código de verificação por email.
    Argumentos:
        email: O email do usuário.
    """
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        codigo = randint(1000,9999)
        codigo_banco = Codigo.query.filter_by(email=email).first()
        codigo_banco.codigo = codigo
        database.session.commit()
        enviar_email(email,codigo)
        flash(f"codigo enviado para seu email {email}","alert-success")
        return 1
    else:
        flash(f"Email não existente! Crie uma conta","alert-danger")
        return 2
    
    
def funcaoTrocarSenha(email,form):
    """
    O que faz: 
        Finaliza o processo de troca de senha, verificando o código de verificação e alterando a senha do usuário.
    Argumentos:
        email: O email do usuário.
        form: O formulário com o código de verificação.
    """
    codigo_banco = Codigo.query.filter_by(email=email).first()
    usuario = Usuario.query.filter_by(email=email).first()
    if form.validate_on_submit():
        if int(form.codigo.data) == int(codigo_banco.codigo):
            senha_crypt = bcrypt.generate_password_hash(form.senha.data).decode('utf8')
            usuario.senha = senha_crypt
            database.session.commit()
            flash(f"Codigo Cofirmado",'alert-success')
            return 1
        else:
            flash(f"Codigo Invalido",'alert-danger')

# -------------------- Loja -----------------
def adicionarProduto(form):
    """
    O que faz: 
        Adiciona um novo produto à loja.
    Argumentos:
        form: O formulário para adicionar um produto.
    """
    if form.validate_on_submit() and 'botao_add_prod' in request.form:
        if form.foto_produto.data:
            nome_imagem = salvar_imagem(form.foto_produto.data,'produto_foto')
            produto = Produtos(nome=form.nome.data,vendedor=current_user.email,preco=form.preco.data,foto=nome_imagem,tipo=form.tipo.data,descricao=form.descricao.data)
            database.session.add(produto)
            database.session.commit()
            flash('Produto Adicionado com Sucesso','alert-success')
            return True

def funcaoComprar(produto,form):
    """
    O que faz: 
        Realiza a compra de um produto na loja, atualizando os saldos do comprador e do vendedor.
    Argumentos:
        produto: O produto a ser comprado.
        form: O formulário de compra.
    """
    if form.validate_on_submit():
        if produto.preco<= current_user.saldo:
            if produto.vendedor != current_user.email:
                usuario = Usuario.query.filter_by(email=produto.vendedor).first()
                if usuario:
                    saldo_agora = float(f"{(float(current_user.saldo) - float(produto.preco)):.2f}")
                    current_user.saldo = saldo_agora
                    usuario.saldo = float(f"{(float(produto.preco) + float(usuario.saldo)):.2f}")
                    extrato = Extrato(env_email=current_user.email,env_valor=produto.preco,rec_email=produto.vendedor)
                    compra = Comprar(comprador=produto.vendedor)
                    database.session.add(compra)
                    database.session.add(extrato)
                    database.session.commit()
                    return True
                    
def funcaoEditarProduto(form,produto):
    """
    O que faz: 
        Edita as informações de um produto na loja.
    Argumentos:
        form: O formulário para editar um produto.
        produto: O produto a ser editado.
    """
    if request.method == "GET":
        form.nome.data = produto.nome
        form.preco.data = produto.preco
        form.tipo.data = produto.tipo
        form.descricao.data = produto.descricao
    elif form.validate_on_submit() and 'botao_add_prod' in request.form:
        if form.foto_produto.data:
            nome_imagem = salvar_imagem(form.foto_produto.data,'produto_foto')
            produto.foto = nome_imagem
        produto.nome = form.nome.data
        produto.preco = form.preco.data
        produto.tipo = form.tipo.data
        produto.descricao = form.descricao.data
        database.session.commit()
        flash("Produto atualizado com sucesso","alert-success")
        return True
    elif form.validate_on_submit():
        flash("Produto inalterado","alert-danger")
        return True
        
def funcaoExcluirProduto(produto):
    """
    O que faz: 
        Exclui um produto da loja.
    Argumentos:
        produto: O produto a ser excluído do banco de dados.
    """
    if current_user.email == produto.vendedor:
        database.session.delete(produto)
        database.session.commit()
        flash("Produto excluido","alert-danger")
        return True
    else:
        abort(403)

# ----------------- Banco -----------------

def transferencia(form):
    """
    O que faz: 
        Realiza uma transferência de saldo entre contas.
    Argumentos:
        form: O formulário de transferência.
    """
    if form.validate_on_submit():
            if form.valor.data<= current_user.saldo:
                if form.conta.data != current_user.email:
                    usuario = Usuario.query.filter_by(email=form.conta.data).first()
                    if usuario:
                        saldo_agora = float(f"{(float(current_user.saldo) - float(form.valor.data)):.2f}")
                        current_user.saldo = saldo_agora
                        usuario.saldo = float(f"{(float(form.valor.data) + float(usuario.saldo)):.2f}")
                        extrato = Extrato(env_email=current_user.email,env_valor=form.valor.data,rec_email=form.conta.data)
                        database.session.add(extrato)
                        database.session.commit()
                        flash("Transferência realizada com sucesso","alert-success")
                        return True
                    else:
                        flash("email não existe no legra bank","alert-danger")
                else:
                    flash("Ação Negada","alert-danger")
            else:
                flash("Saldo invalido.","alert-danger")

def funcaoEmprestimo(form):
    """
    O que faz: 
        Realiza um empréstimo de saldo para o usuário.
    Argumentos:
        form: O formulário para realizar o empréstimo.
    """
    if form.validate_on_submit():
        extrato = Extrato(env_email="Bank Legra",env_valor=form.valor.data,rec_email=current_user.email)
        current_user.saldo = float(form.valor.data)
        database.session.add(extrato)
        database.session.commit()
        flash("Feito","alert-success")
        return True
        
#----------------- Feedback --------------------

def funcaoCriarFeedback(form):
    """
    O que faz: 
        Cria um novo feedback.
    Argumentos:
        form: O formulário para criar um feedback.
    """
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data,corpo=form.texto.data,autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Feedback Criado com Sucesso','alert-success')
        return True
        
        
def funcaoEditarFeedback(form,post):
    """
    O que faz: 
        Edita um feedback existente.
    Argumentos:
        form: O formulário para editar um feedback.
        post: O feedback a ser editado no banco de dados.
    """
    if request.method == "GET":
        form.titulo.data = post.titulo
        form.texto.data = post.corpo
    elif form.validate_on_submit():
        post.titulo = form.titulo.data
        post.corpo = form.texto.data
        database.session.commit()
        flash("Feedback atualizado com sucesso","alert-success")
        return True

def funcaoExcluirFeedback(post):
    """
    O que faz: 
        Exclui um feedback.
    Argumentos:
        post: O feedback a ser excluído no banco de dados.
    """
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash("feedback excluido","alert-danger")
        return True
    else:
        abort(403)
