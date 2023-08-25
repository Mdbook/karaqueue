from flask import session
from flask_socketio import SocketIO, send, emit, disconnect
import json, functools
# from main import authenticated_only
from app import app
socketapp = SocketIO(app)
from users import User, db

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session['logged_in']:
            pass
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def admin_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session['logged_in'] and session['admin']:
            pass
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketapp.on('init')
@authenticated_only
def init(username):
    print('User "' + username + '" connected.')
    data = get_usernames()
    print(data)
    emit('User Init', data, json=True, broadcast=False)


@socketapp.on('message')
def handle_message(data):
    print('received message: ' + data)

def delete_user(uname):
    User.query.filter_by(username=uname).delete()
    print("Deleted user " + uname)
    db.session.commit()
    update_users()

def get_users():
    return User.query.all()

def get_usernames():
    data = get_users()
    newArr = []
    for item in data:
        newArr.append(item.username)
    return json.dumps(newArr)

def update_users():
    socketapp.emit("User Update", get_usernames())

def create_user(uname, pwd):
    new_user = User(
        username=uname,
        password=pwd)
    db.session.add(new_user)
    db.session.commit()
    update_users()

def reset_password_for_user(uname, password):
    print("Resetting password")
    data = User.query.filter_by(username=uname).first()
    data.password = password
    db.session.commit()
    print("Password reset")