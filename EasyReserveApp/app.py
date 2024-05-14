# Flask
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Criação da instância da aplicação Flask
app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta'  # Chave secreta para uso das sessões

# Inicialização do SQLAlchemy com a aplicação Flask
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definição do modelo Quarto
class Quarto(db.Model):
    __tablename__ = 'quartos'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    tipo = db.Column(db.String)
    preco = db.Column(db.Float)
    banheiros = db.Column(db.Integer)
    disponivel = db.Column(db.Boolean)

    def __init__(self, numero, tipo, preco, banheiros, disponivel=True):
        self.numero = numero
        self.tipo = tipo
        self.preco = preco
        self.banheiros = banheiros
        self.disponivel = disponivel

# Definição do modelo Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)  # Adicionando a coluna username
    senha_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, senha):
        self.username = username
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


# Criação das tabelas no banco de dados com base nas definições de classe
with app.app_context():
    db.create_all()

# Rota para a página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para cadastro de quartos
@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == "POST":
        numero = request.form.get("numero")
        tipo = request.form.get("tipo")
        preco = request.form.get("preco")
        banheiros = request.form.get("banheiros")

        if numero and tipo and preco and banheiros:
            quarto = Quarto(numero, tipo, preco, banheiros)
            db.session.add(quarto)
            db.session.commit()
            return redirect(url_for("index"))  # Redireciona para a página inicial após o cadastro

    return render_template("cadastro.html")

# Rota para listar quartos
@app.route("/lista")
def lista():
    quartos = Quarto.query.all()
    return render_template("lista.html", quartos=quartos)

# Rota para excluir quartos
@app.route("/excluir/<int:id>")
def excluir(id):
    quarto = Quarto.query.get(id)
    db.session.delete(quarto)
    db.session.commit()
    return redirect(url_for("lista"))

# Rota para atualizar quartos
@app.route("/atualizar/<int:id>", methods=['GET', 'POST'])
def atualizar(id):
    quarto = Quarto.query.get(id)

    if request.method == "POST":
        numero = request.form.get("numero")
        tipo = request.form.get("tipo")
        preco = request.form.get("preco")
        banheiros = request.form.get("banheiros")

        if numero and tipo and preco and banheiros:
            quarto.numero = numero
            quarto.tipo = tipo
            quarto.preco = preco
            quarto.banheiros = banheiros
            db.session.commit()
            return redirect(url_for("lista"))

    return render_template("atualizar.html", quarto=quarto)

# Rota para login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.verificar_senha(senha):
            session['usuario_id'] = usuario.id  # Armazena o ID do usuário na sessão
            return redirect(url_for('index'))  # Redireciona para a página inicial após o login

    return render_template('login.html')

# Rota para logout
@app.route("/logout")
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
