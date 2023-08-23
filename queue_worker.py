import os, json, time
from flask_socketio import send, emit, disconnect
from id_gen import generate_id
from socket_worker import socketapp, authenticated_only, admin_only
from flask import session

if not os.path.exists("data/queue.json"):
    f = open("data/queue.json", "w")
    f.write("{\"order\":[],\"list\":{}}")
    f.close()

f = open('data/queue.json', 'r')
queue = json.loads(f.read())
print(queue)
class Request():
    id = ""
    username = ""
    song = ""
    author = ""
    timestamp = 0
    def __init__(self, uname, sng, ath):
        self.id = generate_id()
        self.username = uname
        self.song = sng
        self.author = ath
        self.timestamp = time.time()

def new_request(username, song, author):
    return Request(
        uname=username,
        sng=song,
        ath=author)

def add_to_queue(req:Request):
    if not req.username in queue['list'].keys():
        queue['list'][req.username] = []
    print('buh')
    print(len(queue['list'][req.username]))
    queue['list'][req.username].append({
        "id":req.id,
        "song":req.song,
        "artist":req.author,
        "timestamp":req.timestamp,
        "username":req.username,
        "iter":len(queue['list'][req.username])
    })
    if not req.username in queue['order']:
        queue['order'].append(req.username)
    print(queue)
    update_queue()


def update_queue():
    queue_string = json.dumps(queue)
    f = open("data/queue.json", "w")
    f.write(queue_string)
    f.close()
    socketapp.emit("Queue Update", queue)


@socketapp.on('init_queue')
@admin_only
def init(username):
    print('User "' + username + '" connected is viewing queue.')
    emit('Queue Init', queue, json=True, broadcast=False)

@socketapp.on('clear_queue')
@admin_only
def clear_queue():
    global queue
    print("Clearing the queue")
    f = open("data/queue.json", "w")
    f.write("{\"order\":[],\"list\":{}}")
    f.close()
    f = open('data/queue.json', 'r')
    queue = json.loads(f.read())
    socketapp.emit("Queue Update", queue)

@socketapp.on('Change User')
@admin_only
def change_order(data):
    global queue
    print("Received order change")
    new_order = json.loads(data)
    for user in queue['order']:
        if user not in new_order:
            new_order.append(user)
    queue['order'] = new_order
    update_queue()

@socketapp.on('Change Song Order')
@admin_only
def change_order(data):
    global queue
    print("Received user song order change")
    order = json.loads(data)
    user = order['user']
    ids = order['list']
    oldids = queue['list'][user]
    for oldid in oldids:
        if oldid['id'] not in ids:
            ids.append(oldid)
    i = 0
    newUserOrder = []
    for songid in ids:
        for song in queue['list'][user]:
            if song['id'] == songid:
                song['iter'] = i
                newUserOrder.append(song)
                i += 1
    print("new order!")
    print(newUserOrder)
    queue['list'][user] = newUserOrder
    update_queue()


@socketapp.on('Get User')
@authenticated_only
def get_user(username):
    global queue
    if session['admin'] or session['username'] == username:
        order = queue['list'][username]
        ret = {
            "username":username,
            "songs":order
        }
        print(ret)
        emit('User Update Response', ret, broadcast=False)

@socketapp.on('Delete Song')
@authenticated_only
def delete_song(data):
    global queue
    # print(queue['list'][data['user']])
    # print("\n")
    # print(data['user'])
    # data = json.loads(data)
    if session['admin'] or session['username'] == data['user']:
        song_id = data['id']
        # print(queue['list'][data['user']])
        to_delete = -1
        for i in range(len(queue['list'][data['user']])):
            if to_delete is not -1:
                queue['list'][data['user']][i]["iter"] = queue['list'][data['user']][i]["iter"] - 1
            elif queue['list'][data['user']][i]["id"] == song_id:
                to_delete = i
        del queue['list'][data['user']][to_delete]
        # print(queue['list'][data['user']])
        # queue['list'][data['user']][song_id].pop()
        # TODO: add case for when num songs = 0
        print("Deleted song " + song_id)
        update_queue()
        # emit('User Update Response', ret, broadcast=False)

