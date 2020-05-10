from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class Post(FlaskForm):
    theme = StringField('Тема поста', validators=[DataRequired()])
    body = StringField('Тело поста', validators=[DataRequired()])

class Msg(FlaskForm):
    body = StringField('Тело письма', validators=[DataRequired()])
    submit = SubmitField('Отправить')