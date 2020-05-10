from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

dialogs = db.Table(
    'dialogs',
    db.Column('sender_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('recipient_id', db.Integer, db.ForeignKey('user.id')),
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    recipient = db.relationship(
        'User', secondary=dialogs,
        primaryjoin=(dialogs.c.sender_id == id),
        secondaryjoin=(dialogs.c.recipient_id == id),
        backref=db.backref('senders', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def start_dialog(self, user):
        if not self.is_dialogging(user):
            self.recipient.append(user)

    def is_dialogging(self, user):
        return self.recipient.filter(
            dialogs.c.recipient_id == user.id).count() > 0


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Dialog(db.Model):
    __tablename__ = 'dial'
    id = db.Column(db.Integer, primary_key=True)
    user_f = db.Column(db.Integer)
    user_s = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Dialog {}>'.format(self.user_f)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dialog_id = db.Column(db.Integer, db.ForeignKey('dial.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

    def size(self):
        return len(self.body)

