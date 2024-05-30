"""Modulo que reune todas as funções"""
import os
import smtplib
import secrets
from random import randint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dropbox
from dotenv import load_dotenv
from PIL import Image, ImageOps
from flask import flash, request, abort, render_template_string
from flask_login import login_user, current_user

from comunidade import app, database, bcrypt
from comunidade.models import Usuario, Post, Extrato, Produtos, Comprar, Codigo

load_dotenv()
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD_EMAIL = os.getenv('PASSWORD_EMAIL')
API_KEY_DROPBOX = os.getenv('API_KEY_DROPBOX')

#-------------------cria tabelas -------------------
def create_tables():
    """funcão que cria tabelas"""
    with app.app_context():
        database.create_all()

# -----------------login e cadastro --------------------
def funcao_login(form, codigo):
    """
    Realiza o login do usuário, verificando a existência do usuário,
    a situação do email por meio de um código de verificação e a senha do usuário.
    """
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario:
            senha = usuario.senha
            senha_agora = form.senha.data
            senha_certa = bcrypt.check_password_hash(senha, senha_agora)
            if codigo.situacao == 1:
                if senha_certa:
                    login_user(usuario, remember=form.lembra_dados.data)
                    flash(f"O login foi feito no email {form.email.data}","alert-success")
                    par_next = request.args.get("next")
                    if par_next:
                        return 1  # se fez login -> volta para a página anterior
                    return 2  # se fez login redirect carteira
                flash("Senha incorreta", "alert-danger")
            else:
                flash("Email não confirmado", "alert-danger")
                return 4
        else:
            flash("Email não existente. Crie uma Conta", "alert-danger")
            return 3  # se não existe conta com o email redirect criar conta
    return False

def funcao_criar_conta(form):
    """
    Cria uma conta de usuário, gerando um hash com a senha,
    adicionando um novo usuário ao banco de dados e
    gerando e enviando um código de verificação por email.
    """
    if form.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form.senha.data).decode('utf8')
        with app.app_context():
            usuario = Usuario(
              email=form.email.data,
              senha=senha_crypt,
              username=form.username.data
            )
            database.session.add(usuario)
            codigo = randint(1000, 9999)
            codigo_user = Codigo(email=form.email.data, codigo=codigo)
            database.session.add(codigo_user)
            enviar_email(form.email.data, codigo)
            database.session.commit()
        flash(f"Conta Criada! Mas antes confirme o seu email {form.email.data}", 'alert-info')
        return 1
    return False

# -------------------- email -----------------

def enviar_email(destino, codigo):
    """
    Envia um email com um código de verificação.
    """
    smtp_server = 'smtp.gmail.com'
    port = 587  # Porta TLS para o Gmail
    sender_email = SENDER_EMAIL
    password = PASSWORD_EMAIL
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = destino
    msg['Subject'] = 'Código BankLegra'
    with open('comunidade/templates/enviar_email.html', 'r',encoding="utf-8") as file:
        html = file.read()
    html = render_template_string(html, codigo=codigo)
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, destino, msg.as_string())
    server.quit()

def salvar_imagem(imagem, pasta):
    """
    Salva uma imagem na nuvem (Dropbox) e retorna o link da imagem.
    """
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome = nome.replace(" ", "")
    nome_do_arquivo = nome + codigo + extensao
    caminho_da_imagem = os.path.join(app.root_path, f'static/{pasta}/', nome_do_arquivo)
    tamanho = (300, 300)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida = ImageOps.exif_transpose(imagem_reduzida)
    imagem_reduzida.thumbnail(tamanho)
    imagem_final = Image.new("RGB", tamanho, (255, 255, 255))
    imagem_final.paste(
      imagem_reduzida,
      ((tamanho[0] - imagem_reduzida.size[0]) // 2,
      (tamanho[1] - imagem_reduzida.size[1]) // 2)
    )
    imagem_final.save(caminho_da_imagem)
    dbx = dropbox.Dropbox(API_KEY_DROPBOX)
    with open(caminho_da_imagem, 'rb') as f:
        dbx.files_upload(f.read(), f"/banco/{pasta}/{nome_do_arquivo}")
    shared_link = dbx.sharing_create_shared_link(f"/banco/{pasta}/{nome_do_arquivo}")
    return shared_link.url.replace(
        'www.dropbox.com',
        'dl.dropboxusercontent.com'
        ).replace('?dl=0', '')

# ----------------- Perfil --------------------

def funcao_editar_perfil(form):
    """
    Edita o perfil do usuário, atualizando o nome de usuário, tags e foto de perfil e senha.
    """
    if request.method == "GET":
        form.username.data = current_user.username
    elif form.validate_on_submit() and 'botao_alterar' in request.form:
        current_user.username = form.username.data
        current_user.tagpagador = form.tags.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data, 'foto_perfil')
            current_user.foto = nome_imagem
        database.session.commit()
        flash("Perfil atualizado", "alert-success")
        return True
    return False

def funcao_trocar_senha_email(email):
    """
    Inicia o processo de troca de senha via email, enviando um código de verificação por email.
    """
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        codigo = randint(1000, 9999)
        codigo_banco = Codigo.query.filter_by(email=email).first()
        codigo_banco.codigo = codigo
        database.session.commit()
        enviar_email(email, codigo)
        flash(f"Código enviado para seu email {email}", "alert-success")
        return 1
    flash("Email não existe no Banco Legra!","alert-danger")
    return 2

def funcao_trocar_senha(email, form):
    """
    Finaliza o processo de troca de senha,
    verificando o código de verificação e alterando a senha do usuário.
    """
    codigo_banco = Codigo.query.filter_by(email=email).first()
    usuario = Usuario.query.filter_by(email=email).first()
    if form.validate_on_submit():
        if int(form.codigo.data) == int(codigo_banco.codigo):
            senha_crypt = bcrypt.generate_password_hash(form.senha.data).decode('utf8')
            usuario.senha = senha_crypt
            database.session.commit()
            flash("Código confirmado", 'alert-success')
            return 1
        flash("Código inválido", 'alert-danger')
    return False

# -------------------- Loja -----------------
def adicionar_produto(form):
    """
    Adiciona um novo produto à loja.
    """
    if form.validate_on_submit() and 'botao_add_prod' in request.form:
        if form.foto_produto.data:
            nome_imagem = salvar_imagem(form.foto_produto.data, 'produto_foto')
            produto = Produtos(
                nome=form.nome.data, vendedor=current_user.email,
                preco=form.preco.data, foto=nome_imagem,
                tipo=form.tipo.data, descricao=form.descricao.data
            )
            database.session.add(produto)
            database.session.commit()
            flash('Produto adicionado com sucesso', 'alert-success')
            return True
    return False

def funcao_comprar(produto,form):
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
                    extrato = Extrato(
                      env_email=current_user.email,
                      env_valor=produto.preco,
                      rec_email=produto.vendedor
                      )
                    compra = Comprar(comprador=produto.vendedor)
                    database.session.add(compra)
                    database.session.add(extrato)
                    database.session.commit()
                    return True
    return False

def funcao_editar_produto(form,produto):
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
    return False

def funcao_excluir_produto(produto):
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
    abort(403)
    return False

# ----------------- Banco -----------------

def funcao_transferencia(form):
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
                    saldo_agora = float(f"{(float(current_user.saldo)-float(form.valor.data)):.2f}")
                    current_user.saldo = saldo_agora
                    usuario.saldo = float(f"{(float(form.valor.data)+float(usuario.saldo)):.2f}")
                    extrato = Extrato(
                      env_email=current_user.email,
                      env_valor=form.valor.data,
                      rec_email=form.conta.data
                      )
                    database.session.add(extrato)
                    database.session.commit()
                    flash("Transferência realizada com sucesso","alert-success")
                    return True
                flash("email não existe no legra bank","alert-danger")
            else:
                flash("Ação Negada","alert-danger")
        else:
            flash("Saldo invalido.","alert-danger")
    return False

def funcao_emprestimo(form):
    """
    O que faz: 
        Realiza um empréstimo de saldo para o usuário.
    Argumentos:
        form: O formulário para realizar o empréstimo.
    """
    if form.validate_on_submit():
        extrato = Extrato(
          env_email="Bank Legra",
          env_valor=form.valor.data,
          rec_email=current_user.email
        )
        current_user.saldo = float(form.valor.data)
        database.session.add(extrato)
        database.session.commit()
        flash("Feito","alert-success")
        return True
    return False

#----------------- Feedback --------------------

def funcao_criar_feedback(form):
    """
    O que faz: 
        Cria um novo feedback.
    Argumentos:
        form: O formulário para criar um feedback.
    """
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data,corpo=form.texto.data,
        autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Feedback Criado com Sucesso','alert-success')
        return True
    return False

def funcao_editar_feedback(form,post):
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
    return None

def funcao_excluir_feedback(post):
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
    abort(403)
