from flask import render_template, redirect, request, session, flash, url_for
from forms import RegistrForm, LoginForm, Msg_, Pst, Edit
from app import app, db, send_email
from models import User, Msg, Dialog, Post
from sqlalchemy import or_
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'])


def follower_notification(email, username):
    send_email("{} is now following you!".format(username),
               'nast-pota@ya.ru',
               [email],
               render_template("follower.txt", user=username),
               render_template("follower.html", user=username))


def forget_password(email, user):
    send_email("{} forget password!".format(session['username']),
               'nast-pota@ya.ru',
               email,
               render_template("forget_password.txt", user=user),
               render_template("forget_password.html", user=user))


@app.route('/logout')
def logout():
    session['user_id'] = None
    session["error"] = 0
    return redirect('/login')


@app.route("/users", methods=['POST', 'GET'])
def users():
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        user = User.query
        print(list(user))
    except Exception as e:
        session["error"] = str(e)
    return render_template('users.html', title='Страница', users=list(user))


@app.route("/", methods=['GET', 'POST'])
def profile():
    session['error'] = 0
    if 'user_id' in session and session['user_id'] != None:
        return redirect('/index/{}'.format(session['user_id']))
    else:
        return redirect('/login')


@app.route("/index/<int:id>", methods=['POST', 'GET'])
def index(id):
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        user = User.query.filter_by(id=id).first()
        me = User.query.filter_by(id=session['user_id']).first()
        posts = list(Post.query.filter_by(user_id=id))
        posts.reverse()
    except Exception as e:
        session["error"] = str(e)
    if session['user_id'] == id:
        try:
            form = Pst()
            if form.validate_on_submit():
                body = form.body.data
                post = Post(user_id=id, body=body)
                db.session.add(post)
                db.session.commit()
                return redirect('/index/{}'.format(id))
        except Exception as e:
            session["error"] = str(e)
        return render_template('index.html', title='Страница', user=user, me=0, form=form, posts=posts)
    else:
        return render_template('index.html', title='Страница', user=user, me=me, posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    session['error'] = 0
    try:
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                session['error'] = "error password"
            else:
                session['user_id'] = user.id
                return redirect('/index/{}'.format(user.id))
    except Exception as e:
        session["error"] = str(e)
    return render_template('login.html', title='Вход', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    session['error'] = 0
    try:
        form = RegistrForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            user = User(username=username, email=email, about_me='good luck', avatar='1.jpg')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            follower_notification(email, username)
            return redirect('/login')
    except Exception as e:
        session["error"] = str(e)
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/follow/<int:userid>', methods=['GET', 'POST'])
def follow(userid):
    session['error'] = 0
    if not 'user_id' in session or session['user_id'] == None:
        return redirect('/login')
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
    session['error'] = 0
    if not 'user_id' in session or session['user_id'] == None:
        return redirect('/login')
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
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        me = User.query.filter_by(id=session['user_id']).first()
        users = list(me.followers)
    except Exception as e:
        session["error"] = str(e)
    return render_template('users.html', title='Подписчики', users=users)


@app.route('/followed', methods=['GET', 'POST'])
def followed():
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        me = User.query.filter_by(id=session['user_id']).first()
        users = list(me.followed)
    except Exception as e:
        session["error"] = str(e)
    return render_template('users.html', title='Подписчики', users=users)


@app.route('/to_dialog/<int:userid>', methods=['GET', 'POST'])
def to_dialog(userid):
    if not 'user_id' in session or session['user_id'] == None:
        return redirect('/login')
    session['error'] = 0
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
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        form = Msg_()
        letters = Msg.query.filter_by(dialog_id=di_id)
        print(list(letters))
        dial = Dialog.query.filter_by(id=di_id).first()
        if form.validate_on_submit():
            content = form.body.data
            if dial.user_f == session['user_id']:
                other = dial.user_s
            else:
                other = dial.user_f
            let = Msg(recipient_id=session['user_id'], sender_id=other, body=content, dialog_id=di_id)
            db.session.add(let)
            db.session.commit()
            return redirect('/dialog/{}#end'.format(di_id))
    except Exception as e:
        session["error"] = str(e)
    return render_template('message.html', title='Диалог', form=form, letters=list(letters), user=session['user_id'])


@app.route('/dialogs', methods=['GET', 'POST'])
def dialogs():
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        dial = Dialog.query.filter(or_(Dialog.user_f == session['user_id'], Dialog.user_s == session['user_id']))
    except Exception as e:
        session["error"] = str(e)
    return render_template('dialog.html', title='Диалоги', dialogs=dial, user=session['user_id'])


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    session['error'] = 0
    try:
        if not 'user_id' in session or session['user_id'] == None:
            return redirect('/login')
        me = User.query.filter_by(id=session['user_id']).first()
        form = Edit()
        if form.validate_on_submit():
            if form.username.data != '':
                me.username = form.username.data
            if form.about.data != '':
                me.about_me = form.about.data
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                me.avatar = filename
                file.save('static/{}'.format(filename))
            db.session.commit()
            return redirect('/index/{}'.format(me.id))
    except Exception as e:
        session["error"] = str(e)
    return render_template('edit.html', form=form)
