from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
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


class Pst(FlaskForm):
    body = StringField('Тело поста', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class Msg(FlaskForm):
    body = StringField('Тело письма', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class Edit(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    file = FileField('Файл', validators=[DataRequired()])
    about = StringField('О себе', validators=[DataRequired()])
    submit = SubmitField('Изменить')
