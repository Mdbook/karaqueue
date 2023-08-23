import os, json, time
from flask_socketio import send, emit, disconnect
from id_gen import generate_id
from socket_worker import socketapp, authenticated_only, admin_only

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

@socketapp.on('change_order')
@admin_only
def change_order(data):
    global queue
    print("Received order change")
    new_order = json.loads(data)
    queue['order'] = new_order
    update_queue()

@socketapp.on('change_user_order')
@admin_only
def change_order(data):
    global queue
    print("Received user song order change")
    order = json.loads(data)
    user = order['user']
    ids = order['list']
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


@socketapp.on('get_user')
@authenticated_only
def change_order(username):
    global queue
    order = queue['list'][username]
    ret = {
        "username":username,
        "songs":order
    }
    print(ret)
    emit('return_user_update', ret, broadcast=False)