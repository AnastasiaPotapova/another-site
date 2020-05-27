import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_mail import Message, Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.create_all()
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
mail = Mail(app)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


from routes import *

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
