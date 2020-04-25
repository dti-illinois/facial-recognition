from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import *

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[required()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
    