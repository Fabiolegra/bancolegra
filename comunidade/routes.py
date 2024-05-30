
"""
Este módulo contém as definições de rotas para o aplicativo comunidade.
"""
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import logout_user, current_user, login_required
from comunidade import app, database
from comunidade.forms import (FormsLoginConta,
    FormsCriaConta, FormsCodigoSO, FormsEditarPerfil, 
    FormsCodigo, FormsCodigoEmail, FormsCriaPost, FormsAddProduto, FormsComprar, 
    FormsEmprestimo, FormsTransferir
)
from comunidade.models import Codigo, Usuario, Post, Produtos, Extrato
from comunidade.funcoes import (create_tables,
    funcao_login, funcao_criar_conta, funcao_editar_perfil, funcao_trocar_senha, 
    funcao_trocar_senha_email, funcao_criar_feedback, funcao_editar_feedback, funcao_excluir_feedback, 
    adicionar_produto, funcao_comprar, funcao_editar_produto, funcao_excluir_produto, funcao_transferencia
)

create_tables()  # Cria tabelas

# --------------------- Área Pública ----------------------

@app.route("/")
def home():
    """Rota para a página inicial."""
    return render_template("home.html")

@app.route("/sobre")
def sobre():
    """Rota para a página sobre."""
    return render_template("sobre.html")

@app.route("/contato")
def contato():
    """Rota para a página de contato."""
    return render_template("contato.html")

# --------------------- Área de Login ----------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota para a página de login."""
    form = FormsLoginConta()
    codigo_ = Codigo.query.filter_by(email=form.email.data).first()
    match funcao_login(form, codigo_):
        case 1:
            par_next = request.args.get("next")
            return redirect(par_next)
        case 2:
            return redirect(url_for("carteira"))
        case 3:
            return redirect(url_for("criaconta"))
        case 4:
            return redirect(url_for("codigo", email=form.email.data))
    return render_template("login.html", form=form)

@app.route("/criaconta", methods=["GET", "POST"])
def criaconta():
    """Rota para a página de criação de conta."""
    form = FormsCriaConta()
    if funcao_criar_conta(form):
        return redirect(url_for("codigo", email=form.email.data))
    return render_template("criaconta.html", form=form)

@app.route("/criaconta/codigo_confirmação/<email>", methods=["GET", "POST"])
def codigo(email):
    """Rota para a página de confirmação de código."""
    form = FormsCodigoSO()
    codigo_ = Codigo.query.filter_by(email=email).first()
    if form.validate_on_submit():
        if int(codigo_.codigo) == int(form.codigo.data):
            codigo_.situacao = 1
            database.session.commit()
            flash(f"A conta foi criada no email {email}", 'alert-success')
            return redirect(url_for("login"))
        flash("Código Inválido", 'alert-danger')
    return render_template("codigo_confirmação.html", form=form)

@app.route("/sair")
@login_required
def sair():
    """Rota para fazer logout."""
    logout_user()
    flash("Logout feito com sucesso", 'alert-success')
    return redirect(url_for("home"))

# --------------------- Área de Perfil ----------------------

@app.route("/perfil")
@login_required
def perfil():
    """Rota para a página de perfil."""
    return render_template("perfil.html")

@app.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    """Rota para a página de edição de perfil."""
    form = FormsEditarPerfil()
    if funcao_editar_perfil(form):
        return redirect(url_for("perfil"))
    return render_template("editar_perfil.html", form=form)

@app.route("/trocar_senha/<email>", methods=["GET", "POST"])
def alterar_senha_codigo(email):
    """Rota para a página de alteração de senha com código."""
    form = FormsCodigo()
    if funcao_trocar_senhar(email, form) == 1:
        return redirect(url_for("login"))
    return render_template("trocar_senha_codigo.html", form=form)

@app.route("/alterar_senha", methods=["GET", "POST"])
def alterar_senha():
    """Rota para a página de alteração de senha."""
    form = FormsCodigoEmail()
    if form.validate_on_submit():
        if funcao_trocar_senha_email(form.email.data) == 1:
            return redirect(url_for("alterar_senha_codigo", email=form.email.data))
        return redirect(url_for("criaconta"))
    return render_template("alterar_senha.html", form=form)

# ------------------ Área de Usuário ----------------------

@app.route("/usuarios")
@login_required
def usuarios():
    """Rota para a lista de usuários."""
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios=lista_usuarios)

# ---------------------- Área de Feedback ----------------------

@app.route("/post/criar", methods=["GET", "POST"])
@login_required
def criar_feedback():
    """Rota para a criação de feedback."""
    form = FormsCriaPost()
    if funcao_criar_feedback(form):
        return redirect(url_for('lista_feedback'))
    return render_template("criar_post.html", form=form)

@app.route("/feedback")
@login_required
def lista_feedback():
    """Rota para a lista de feedbacks."""
    posts = Post.query.order_by(Post.id.desc())
    return render_template("lista_feedback.html", posts=posts)

@app.route("/feedback/<post_id>", methods=["GET", "POST"])
@login_required
def exibir_feedback(post_id):
    """Rota para exibir feedback."""
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormsCriaPost()
        if funcao_editar_feedback(form, post):
            return redirect(url_for("lista_feedback"))
    else:
        form = None
    return render_template("post.html", post=post, form=form)

@app.route("/feedback/<post_id>/excluir", methods=["GET", "POST"])
@login_required
def excluir_feedback(post_id):
    """Rota para excluir feedback."""
    post = Post.query.get(post_id)
    if funcao_excluir_feedback(post):
        return redirect(url_for('lista_feedback'))
    abort(403)
    return None
# ---------------------- Área de Loja ----------------------

@app.route("/produtos/lista", methods=["GET", "POST"])
@login_required
def lista_produto():
    """Rota para a lista de produtos."""
    produtos = Produtos.query.order_by(Produtos.id.desc())
    categorias = [
        "Roupas e acessórios", "Eletrônicos", "Produtos para casa", 
        "Cosméticos e produtos de beleza", "Alimentos e bebidas", 
        "Livros e mídia", "Artigos esportivos", "Brinquedos e jogos"
    ]
    return render_template("lista_produto.html", produtos=produtos, categorias=categorias)

@app.route("/vendedor/addproduto", methods=["GET", "POST"])
@login_required
def add_produto():
    """Rota para adicionar produto."""
    form = FormsAddProduto()
    if adicionar_produto(form):
        return redirect(url_for('lista_produto'))
    return render_template("add_produto.html", form=form)

@app.route("/vendedor/<produto_id>", methods=["GET", "POST"])
@login_required
def produto(produto_id):
    """Rota para exibir produto."""
    produto_ = Produtos.query.get(produto_id)
    form = FormsComprar()
    if funcao_comprar(produto_, form):
        return redirect(url_for("carteira"))
    if current_user.email == produto_.vendedor:
        produto_editar = FormsAddProduto()
        if funcao_editar_produto(produto_editar, produto_):
            return redirect(url_for("lista_produto"))
    else:
        produto_editar = None
    return render_template("produto.html",
                            produto=produto_, form=form, produto_editar=produto_editar
                            )

@app.route("/produtos/<pt>", methods=["GET", "POST"])
@login_required
def produto_tipo(pt):
    """Rota para exibir produtos por tipo."""
    produtos = Produtos.query.filter_by(tipo=pt)
    return render_template("produto_tipo.html", produtos=produtos, tipo=pt)

@app.route("/produto/<produto_id>/excluir", methods=["GET", "POST"])
@login_required
def excluir_produto(produto_id):
    """Rota para excluir produto."""
    produto_ = Produtos.query.get(produto_id)
    if funcao_excluir_produto(produto_):
        return redirect(url_for('lista_produto'))
    abort(403)
    return None

# --------------------- Carteira ----------------------

@app.route("/carteira", methods=["GET", "POST"])
@login_required
def carteira():
    """Rota para a carteira do usuário."""
    return render_template("carteira.html")

@app.route("/emprestimo", methods=["GET", "POST"])
@login_required
def emprestimo():
    """Rota para solicitação de empréstimo."""
    form = FormsEmprestimo()
    if funcaoEmprestimo(form):
        return redirect(url_for("carteira"))
    return render_template("emprestimo.html",form=form)

@app.route("/carteira/transcacao",methods=["GET","POST"])
@login_required
def transcacao():
    """Rota para transferencia de dinheiro"""
    form = FormsTransferir()
    if funcao_transferencia(form):
        return redirect(url_for("carteira"))
    return render_template("transcacao.html",form=form)

@app.route("/extrato")
@login_required
def extrato():
    """Rota para o extrato bancario"""
    lista_usuarios = Usuario()
    extratos_env = (
        Extrato.query.filter_by(env_email=current_user.email).order_by(Extrato.id.desc())
        )
    extratos_rec = (
        Extrato.query.filter_by(rec_email=current_user.email).order_by(Extrato.id.desc())
        )
    return render_template("extrato.html",
                            extratos_rec=extratos_rec,
                            extratos_env=extratos_env,
                            lista_usuarios=lista_usuarios
                            )
