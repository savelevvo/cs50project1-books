import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import Flask, session, render_template, request, redirect, url_for


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, email, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.email = email
        self.password = self.set_password(password)

    def __repr__(self):
        return self.email

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class Book(db.Model):
    __tablename__ = 'book'
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return '[{}] {}'.format(self.isbn, self.title)


@app.route("/")
def index():
    return render_template('index.html', email=session.get('email'), is_logged=session.get('is_logged'))


@app.route("/reg_form")
def reg_form():
    return render_template('register.html')


@app.route("/search", methods=['GET'])
def search():
    if request.method == 'GET':
        isbn = request.args.get('isbn')
        title = request.args.get('title')
        author = request.args.get('author')

        result = Book.query.filter_by(isbn=isbn).all()

        return render_template('search.html', email=session.get('email'), is_logged=session.get('is_logged'), search_results=result)


@app.route("/login_form")
def login_form():
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')

    db.session.add(User(email=email, password=password))
    db.session.commit()

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = email
            session['is_logged'] = True
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session['is_logged'] = False
    return redirect(url_for('index'))
