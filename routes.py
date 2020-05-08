from flask import render_template, redirect, request, session, flash
from forms import RegistrForm, LoginForm
from app import app, db
from models import User


@app.route("/index/<int:id>", methods=['POST', 'GET'])
def index(id):
    user = User.query.filter_by(id=id).first()
    return render_template('index.html', title='Страница', user=user)


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
        else:
            return redirect('/index/{}'.format(user.id))
    return render_template('login.html', title='Вход', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)