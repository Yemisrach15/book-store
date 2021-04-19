from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

login_manager = LoginManager()
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))