from flask_socketio import SocketIO, send, emit
import json
from app import app
socketapp = SocketIO(app)
from users import User, db

@socketapp.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketapp.on('init')
def init(username):
    print('User "' + username + '" connected.')
    data = get_usernames()
    print(data)
    emit('User Init', data, json=True, broadcast=False)

@socketapp.on('delete')
def delete(uname):
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
