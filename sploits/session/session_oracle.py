from flask import Flask, request
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY'] = 'y0u-w1ll-n3v3r-gu355'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login = LoginManager(app)
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return '<form action="/" method="POST"><input name="username"></input><input name="id" type="number"></input><input type="submit"></input></form>'
    user = User(username=request.form["username"], id=int(request.form["id"]))
    login_user(user)
    return request.cookies.get('session')


app.run(host='0.0.0.0', port='31337', debug=True)
