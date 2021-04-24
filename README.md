# Project 1: Books

## Installation steps

On a terminal

1. Set up a virtual environment 

    `python -m venv venv`
    
2. Activate the virtual environment

    `venv\Scripts\activate`
    
3. Install requirements

    `pip install -r requirements.txt`
    
4. Set database url

    `set DATABASE_URL=[your database url]`
    
5. Create users, books and reviews table

    `python create.py`

6. Populate database with books

    `python import.py`

7. Set flask app

    `set FLASK_APP=application.py`
    
8. Finally run the flask app

    `flask run`
