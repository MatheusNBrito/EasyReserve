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
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



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
    if not is_loged():
        flash("Acesso negado: apenas logado.", "error")
        return redirect(url_for('login'))
    if not is_admin():
        flash("Acesso negado: apenas administradores.", "error")
        return redirect(url_for('index'))
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
    if not is_loged():
        flash("Acesso negado: apenas logado.", "error")
        return redirect(url_for('login'))

    quartos = Quarto.query.all()
    return render_template("lista.html", quartos=quartos)

# Rota para excluir quartos
@app.route("/excluir/<int:id>")
def excluir(id):
    if not is_admin():
        flash("Acesso negado: apenas administradores.", "error")
        return redirect(url_for('lista'))
    quarto = Quarto.query.get(id)
    db.session.delete(quarto)
    db.session.commit()
    return redirect(url_for("lista"))

# Rota para atualizar quartos
@app.route("/atualizar/<int:id>", methods=['GET', 'POST'])
def atualizar(id):
    quarto = Quarto.query.get(id)
    if not is_admin():
        flash("Acesso negado: apenas administradores.", "error")
        return redirect(url_for('lista'))
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

# Rota para Cadastro
@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))  # Redirecionar para a página principal após cadastro
    return render_template('cadastro_usuario.html')


from flask import Flask, render_template, redirect, url_for, request, session, flash

from flask import Flask, render_template, redirect, url_for, request, session, flash


def is_admin():
    return session.get('is_admin', False)

def is_loged():
    if 'usuario_id' in session:
        return True
    return False


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session['usuario_id'] = usuario.id
            session['username'] = usuario.username
            session['is_admin'] = username.startswith('@')  # Verifica se é administrador
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')

    return render_template('login.html')



# Rota para logout
@app.route("/logout")
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
