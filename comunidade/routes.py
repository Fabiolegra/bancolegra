from flask import render_template,flash,redirect,url_for,request,abort
from comunidade import app,database,bcrypt
from comunidade.forms import * 
from comunidade.models import *
from flask_login import login_user,logout_user,current_user,login_required
import secrets
import os 
from comunidade.funcoes import *
from PIL import Image,ImageOps

create_tables()#cria tabelas

# --------------------- Area Publica ----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/sobre") 
def sobre():
    return render_template("sobre.html")

@app.route("/contato") 
def contato():
    return render_template("contato.html")

# --------------------- Area login ----------------------
@app.route("/login",methods=["GET","POST"])
def login():
    form = Forms_login_conta()
    codigo = Codigo.query.filter_by(email=form.email.data).first()
    match funcaoLogin(form,codigo):
        case 1:
            par_next = request.args.get("next")
            return redirect(par_next)
        case 2:
            return redirect(url_for("carteira"))
        case 3:
            return redirect(url_for("criaconta"))
        case 4:
            return redirect(url_for("codigo",email=form.email.data))
    return render_template("login.html",form=form)
    
@app.route("/criaconta",methods=["GET","POST"])
def criaconta():
    form = Forms_cria_conta()
    if funcaoCriarconta(form)==1:
        return redirect(url_for("codigo",email=form.email.data))
    return render_template("criaconta.html",form=form)
    
@app.route("/criaconta/codigo_confirmação/<email>",methods=["GET","POST"])
def codigo(email):
    form = Forms_codigo_so()
    codigo = Codigo.query.filter_by(email=email).first()
    if form.validate_on_submit():
        if int(codigo.codigo) == int(form.codigo.data):
            codigo_dado.situacao = 1
            database.session.commit()
            flash(f"A conta foi criada no email {email}",'alert-success')
            return redirect(url_for("login"))
        else:
            flash(f"Codigo Invalido",'alert-danger')
    return render_template("codigo_confirmação.html",form=form)
    
@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash("logout feito com sucesso",'alert-success')
    return redirect(url_for("home"))


#--------------------- Area perfil ----------------------
@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")
    
@app.route("/perfil/editar",methods=["GET","POST"])
@login_required
def editar_perfil():
    form = Forms_editar_perfil()
    if funcaoEditarPerfil(form):
        return redirect(url_for("perfil"))
    return render_template("editar_perfil.html",form=form)

@app.route("/trocar_senha/<email>",methods=["GET","POST"])
def alterar_senha_codigo(email):
    form = Forms_codigo()
    if funcaoTrocarSenha(email,form)==1:
        return redirect(url_for("login"))
    return render_template("trocar_senha_codigo.html",form=form)

@app.route("/alterar_senha",methods=["GET","POST"])
def alterar_senha():
    form = Forms_codigo_email()#reaproveitando
    if form.validate_on_submit():
        if funcaoTrocarsenhaEmail(form.email.data) == 1:
            return redirect(url_for("alterar_senha_codigo",email=form_trocar_senha.email.data))
        else:
            return redirect(url_for("criaconta"))
    return render_template("alterar_senha.html",form=form)


# ------------------ Area usuario ----------------------

@app.route("/usuarios")
@login_required
def usuarios():
    lista_Usuarios = Usuario.query.all()
    return render_template("usuarios.html",lista_Usuarios = lista_Usuarios)


# ---------------------- Area Feedback ----------------------

@app.route("/post/criar",methods=["GET","POST"])
@login_required
def criar_feedback():
    form = Forms_cria_post()
    if funcaoCriarFeedback(form):
        return redirect(url_for('lista_feedback'))
    return render_template("criar_post.html",form=form)

@app.route("/feedback")
@login_required
def lista_feedback():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("lista_feedback.html",posts=posts)

@app.route("/feedback/<post_id>",methods=["GET","POST"])
@login_required
def exibir_feedback(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = Forms_cria_post()#reaproveitando 
        if funcaoEditarFeedback(form,post):
            return redirect(url_for("lista_feedback"))
    else:
        feedback_editar = None
    return render_template("post.html",post=post,form=form)


@app.route("/feedback/<post_id>/excluir",methods=["GET","POST"])
@login_required
def excluir_feedback(post_id):
    post = Post.query.get(post_id)
    if funcaoExcluirFeedback(post):
        return redirect(url_for('lista_feedback'))
        


# ---------------------- Area Loja ----------------------
@app.route("/produtos/lista",methods=["GET","POST"])
@login_required
def lista_produto():
    produtos = Produtos.query.order_by(Produtos.id.desc())
    lista = ["Roupas e acessórios","Eletrônicos","Produtos para casa","Produtos para casa","Cosméticos e produtos de beleza","Alimentos e bebidas","Livros e mídia","Artigos esportivos","Brinquedos e jogos"]
    return render_template("lista_produto.html",produtos=produtos,lista=lista)
    
@app.route("/vendedor/addproduto",methods=["GET","POST"])
@login_required
def add_produto():
    form = Forms_add_produto()
    if adicionarProduto(form):
        return redirect(url_for('lista_produto'))
    return render_template("add_produto.html",form=form)
    
@app.route("/vendedor/<produto_id>",methods=["GET","POST"])
@login_required    
def produto(produto_id):
    produto = Produtos.query.get(produto_id)
    form = Forms_comprar()
    if funcaoComprar(produto,form):
        return redirect(url_for("carteira"))
    if current_user.email == produto.vendedor:
        produto_editar = Forms_add_produto()#reaproveintando 
        if funcaoEditarProduto(produto_editar,produto):
            return redirect(url_for("lista_produto"))
    else:
        produto_editar = None
    return render_template("produto.html",produto=produto,form=form,produto_editar=produto_editar)

@app.route("/produtos/<pt>",methods=["GET","POST"])
@login_required  
def produto_tipo(pt):
    tipo = pt 
    produtos = Produtos.query.filter_by(tipo=pt)
    return render_template("produto_tipo.html",produtos=produtos,tipo=tipo)
    
@app.route("/produto/<produto_id>/excluir",methods=["GET","POST"])
@login_required
def excluir_produto(produto_id):
    produto = Produtos.query.get(produto_id)
    if funcaoExcluirProduto(produto):
        return redirect(url_for('lista_produto'))
         
#-------------------- Area Transação ---------------------

@app.route("/carteira",methods=["GET","POST"])
@login_required
def carteira():
    return render_template("carteira.html")

@app.route("/carteira/emprestimo",methods=["GET","POST"])
@login_required
def emprestimo():
    form = Forms_emprestimo()
    if funcaoEmprestimo(form):
        return redirect(url_for("carteira"))
    return render_template("emprestimo.html",form=form)

@app.route("/carteira/transcacao",methods=["GET","POST"])
@login_required
def transcacao():
    form = Forms_transferir()
    if transferencia(form):
        return redirect(url_for("carteira"))
    return render_template("transcacao.html",form=form)

@app.route("/extrato")
@login_required
def extrato():
    lista_Usuarios = Usuario()
    extratos = Extrato.query.order_by(Extrato.id.desc())
    extratos_env = Extrato.query.filter_by(env_email=current_user.email).order_by(Extrato.id.desc())
    extratos_rec = Extrato.query.filter_by(rec_email=current_user.email).order_by(Extrato.id.desc())
    return render_template("extrato.html",extratos_rec=extratos_rec,extratos_env=extratos_env,lista_Usuarios=lista_Usuarios)
