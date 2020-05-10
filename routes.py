from flask import render_template, redirect, request, session, flash
from flask_login import current_user, login_required
from forms import RegistrForm, LoginForm, Msg
from app import app, db
from models import User, Message, Dialog


@app.route('/logout')
def logout():
    session['user_id'] = None
    return redirect('/login')


@app.route("/users", methods=['POST', 'GET'])
def users():
    user = User.query
    print(list(user))
    return render_template('users.html', title='Страница', users=list(user))


@app.route("/", methods=['GET', 'POST'])
def profile():
    if session['user_id']:
        return redirect('/index/{}'.format(session['user_id']))
    else:
        return redirect('/login')


@app.route("/index/<int:id>", methods=['POST', 'GET'])
def index(id):
    user = User.query.filter_by(id=id).first()
    me = User.query.filter_by(id=session['user_id']).first()
    if session['user_id'] == id:
        return render_template('index.html', title='Страница', user=user, me=0)
    else:
        return render_template('index.html', title='Страница', user=user, me=me)


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
            session['user_id'] = user.id
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


@app.route('/follow/<int:userid>', methods=['GET', 'POST'])
def follow(userid):
    user = User.query.filter_by(id=userid).first()
    me = User.query.filter_by(id=session['user_id']).first()
    if user is None:
        return redirect('/login')
    if user.id == session['user_id']:
        return redirect('/index/{}'.format(userid))
    if me.is_following(user):
        return redirect('/index/{}'.format(userid))
    me.follow(user)
    db.session.commit()
    return redirect('/index/{}'.format(userid))


@app.route('/unfollow/<int:userid>', methods=['GET', 'POST'])
def unfollow(userid):
    user = User.query.filter_by(id=userid).first()
    me = User.query.filter_by(id=session['user_id']).first()
    if user is None:
        return redirect('/login')
    if user == me:
        return redirect('/index/{}'.format(userid))
    me.unfollow(user)
    db.session.commit()
    return redirect('/index/{}'.format(userid))


@app.route('/followers', methods=['GET', 'POST'])
def followers():
    me = User.query.filter_by(id=session['user_id']).first()
    users = list(me.followers)
    return render_template('users.html', title='Подписчики', users=users)


@app.route('/followed', methods=['GET', 'POST'])
def followed():
    me = User.query.filter_by(id=session['user_id']).first()
    users = list(me.followed)
    return render_template('users.html', title='Подписчики', users=users)


@app.route('/to_dialog/<int:userid>', methods=['GET', 'POST'])
def to_dialog(userid):
    user = User.query.filter_by(id=userid).first()
    me = User.query.filter_by(id=session['user_id']).first()
    if user is None:
        return redirect('/login')
    if user.id == session['user_id']:
        return redirect('/index/{}'.format(userid))
    if me.is_dialogging(user) and user.is_dialogging(me):
        print('-')
        dial = Dialog.query.filter_by(user_f=me.id, user_s=user.id).first()
        if dial:
            return redirect('/dialog/{}'.format(dial.id))
        else:
            dial = Dialog.query.filter_by(user_f=user.id, user_s=me.id).first()
            return redirect('/dialog/{}'.format(dial.id))
    me.start_dialog(user)
    user.start_dialog(me)
    dial = Dialog(user_f=me.id, user_s=user.id)
    db.session.add(dial)
    db.session.commit()
    return redirect('/dialog/{}'.format(dial.id))


@app.route('/dialog/<int:di_id>', methods=['GET', 'POST'])
def dialog(di_id):
    form = Msg()
    letters = Message.query.filter_by(dialog_id=di_id)
    print(list(letters))
    dial = Dialog.query.filter_by(id=di_id).first()
    if form.validate_on_submit():
        content = form.body.data
        if dial.user_f == session['user_id']:
            other = dial.user_s
        else:
            other = dial.user_f
        let = Message(recipient_id=session['user_id'], sender_id=other, body=content, dialog_id=di_id)
        db.session.add(let)
        db.session.commit()
        return redirect('/dialog/{}#end'.format(di_id))
    return render_template('message.html', title='Диалог', form=form, letters=list(letters), user=session['user_id'])