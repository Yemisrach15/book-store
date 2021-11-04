import os
import requests
import json

from flask import Flask, session, render_template, redirect, request, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from models import *
from forms import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Apply static file changes without clearing cache [ONLY FOR DEVELOPMENT]
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
db.init_app(app)

# Set login view
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

        if User.query.filter_by(username=name).first() == None:
            db.session.add(usr)
            db.session.commit()

            flash("Registration was successful.", "info")
            return redirect(url_for("login"))
        else:
            flash("Username already exists.", "error")

    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
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
        
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
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
    statement = text("""select * from books where lower(title) like lower('%""" + query + """%') or lower(isbn) like lower('%""" + query + """%') or lower(author) like lower('%""" + query + """%')""")
    result = db.session.execute(statement).fetchall()
    isEmpty = False
    if len(result) == 0:
        isEmpty = True
    return render_template("search_result.html", query=query, result=result, isEmpty=isEmpty)

@app.route("/books/<string:isbn>", methods=['GET', 'POST'])
def book(isbn):
    isbn = str(isbn)

    statement = text("""select * from books where books.isbn = :isbn limit 1""")
    bookDetail = db.session.execute(statement, {'isbn': isbn}).fetchone()
    
    bookId = bookDetail.id

    
    if request.method == 'POST':
        userId = int(current_user.get_id())
        params = {}
        feedback = request.form.get('feedback')
        rating = int(request.form.get('rating'))
        if feedback and rating:
            params = {'feedback': feedback, 'rating': rating, 'bookId': bookId, 'userId': userId}
            statement = text("""insert into reviews(review, rating, book_id, user_id) values(:feedback, :rating, :bookId, :userId)""")
            db.session.execute(statement, params)
            db.session.commit()
            return redirect(url_for('book', isbn=isbn))


    if current_user.is_authenticated:
        userId = int(current_user.get_id())

        # check if user has written review on current book
        userCanReview = True
        statement = text("""select * from reviews where book_id=:bookId AND user_id=:userId""")
        userReview = db.session.execute(statement, {'bookId': bookId, 'userId': userId}).fetchone()
        if (userReview != None):
            userCanReview = False

        statement = text("""select reviews.review, reviews.rating, reviews.book_id, users.username from reviews, users where book_id=:bookId AND user_id!=:userId AND user_id=users.id""")
        bookReviews = db.session.execute(statement, {'bookId': bookId, 'userId': userId}).fetchall()

        return render_template("book.html", bookDetail=bookDetail, bookReviews=bookReviews, userCanReview=userCanReview, userReview=userReview)
        
    else:
        statement = text("""select reviews.review, reviews.rating, reviews.book_id, users.username from reviews, users where book_id=:bookId AND user_id=users.id""")
        bookReviews = db.session.execute(statement, {'bookId': bookId}).fetchall()
        return render_template("book.html", bookDetail=bookDetail, bookReviews=bookReviews)
    

@app.route("/api/<string:isbn>")
def api(isbn):
    isbn = str(isbn)

    statement = text("""select * from books where books.isbn = :isbn limit 1""")
    bookDetail = db.session.execute(statement, {'isbn': isbn}).fetchone()

    if bookDetail:
        statement = text("""select count(*) as review_count, sum(rating)/count(*) as average_score from reviews where book_id=:bookId""")
        reviewDetail = db.session.execute(statement, {'bookId': bookDetail.id}).fetchone()
        values = {
            "title": bookDetail.title,
            "author": bookDetail.author,
            "year": bookDetail.year,
            "isbn": bookDetail.isbn,
            "review_count": reviewDetail.review_count,
            "average_score": reviewDetail.average_score
        }

        return json.dumps(values)
    
    values = {
        "error": 404,
        "message": "The requested ISBN was not found in database"
    }
    return json.dumps(values)


if __name__ == "__main__":
    app.run(debug=True)