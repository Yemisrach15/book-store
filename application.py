import os

from flask import Flask, session, render_template, redirect, request, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from models import *
from forms import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# from wtform_fields import *

app = Flask(__name__)

# Apply static file changes without clearing cache
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "secret key"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# Session = scoped_session(sessionmaker(bind=engine))
# db = Session()
db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        pwd = form.password.data
        confirmPwd = form.confirmPassword.data
        
        usr = User(name, generate_password_hash(pwd))

        # Session class at line 23 {=scoped_session(sessionmaker(bind=engine))}
        # db = Session()
        if User.query.filter_by(username=name).first() == None:
            db.session.add(usr)
            db.session.commit()

            flash("Registration was successful.", "info")
            return redirect(url_for("login"))
        else:
            flash("Username already exists.", "error")

        # from flask_session
        # session["user"] = username

    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    # if "user" in session:
    #     return redirect(url_for("dashboard"))
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        name = form.name.data
        pwd = form.password.data
        user = User.query.filter_by(username=name).first()
        if user:
            if check_password_hash(user.password, pwd):
                login_user(user)
                return redirect(url_for('dashboard'))
        flash("Incorrect username or password", "error")

        # from flask_session  
        # session["user"] = request.form.get("name")
        # return redirect(url_for("dashboard"))
        
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    # session.clear()
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user.username)

@app.route("/search")
def search():
    query = request.args.get("q")
    if query == None:
        return redirect(url_for("dashboard"))

    query.strip().replace("'", "")
    # result = Book.query.filter_by(title=query).all()
    statement = text("""select * from books where lower(title) like '%""" + query + """%' or lower(isbn) like '%""" + query + """%' or lower(author) like '%""" + query + """%'""")
    result = db.session.execute(statement).fetchall()
    isEmpty = False
    if len(result) == 0:
        isEmpty = True
    return render_template("search_result.html", query=query, result=result, isEmpty=isEmpty)

@app.route("/books/<string:isbn>")
def book(isbn):
    isbn = str(isbn)
    statement = text("""select * from books where books.isbn = :isbn limit 1""")
    result = db.session.execute(statement, {'isbn': isbn}).fetchone()

    return render_template("book.html", result=result)
    


if __name__ == "__main__":
    app.run(debug=True)