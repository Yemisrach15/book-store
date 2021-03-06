import os
from flask import Flask
from models import db
from application import app

# app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db is imported from models
db.init_app(app)

def main():
    db.create_all()

if __name__ =='__main__':
    with app.app_context():
        main()
