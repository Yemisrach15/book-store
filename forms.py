from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    name = StringField("Name ", validators=[DataRequired()])
    password = PasswordField("Password ", validators=[DataRequired()],)
    confirmPassword = PasswordField("Confirm password ", validators=[DataRequired(), EqualTo('password', message="Password does not match.")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    name = StringField("Name ", validators=[DataRequired()])
    password = PasswordField("Password ", validators=[DataRequired()])
    submit = SubmitField("Login")
    