import os, json, time
from flask_socketio import send, emit, disconnect
from id_gen import generate_id
from socket_worker import socketapp, authenticated_only, admin_only
from flask import session
DEFAULT_QUEUE = "{\"order\":[],\"list\":{},\"inactive\":[],\"hidden\":[],\"active\":\"None\"}"

if not os.path.exists("data/queue.json"):
    f = open("data/queue.json", "w")
    f.write(DEFAULT_QUEUE)
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
        # self.active = True

def new_request(username, song, author):
    return Request(
        uname=username,
        sng=song,
        ath=author)

def add_to_queue(req:Request):
    if not req.username in queue['list'].keys():
        queue['list'][req.username] = []
    # print(len(queue['list'][req.username]))
    queue['list'][req.username].append({
        "id":req.id,
        "song":req.song,
        "artist":req.author,
        "timestamp":req.timestamp,
        "username":req.username,
        "iter":len(queue['list'][req.username]),
        # "active":req.active
    })
    if not req.username in queue['order']:
        if len(getActiveUsers()) == 0:
            queue['active'] = req.username
        queue['order'].append(req.username)
    if req.username in queue['inactive']:
        queue['inactive'].remove(req.username)
    print(queue)
    update_queue()

def getActiveUsers():
    allUsers = queue['order']
    hiddenUsers = queue['hidden']
    inactiveUsers = queue['inactive']
    activeUsers = []
    for user in allUsers:
        if not (user in hiddenUsers or user in inactiveUsers):
            activeUsers.append(user)
    return activeUsers


def update_queue():
    update_order()
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

@socketapp.on('init_user_queue')
@authenticated_only
def init_user():
    print('User "' + session['username'] + '" connected is viewing queue.')
    username = session['username']
    order = queue['list'][username]
    ret = {
        "username":username,
        "songs":order
    }
    print(ret)
    emit('User Update Response', ret, broadcast=False)

@socketapp.on('clear_queue')
@admin_only
def clear_queue():
    global queue
    print("Clearing the queue")
    f = open("data/queue.json", "w")
    f.write(DEFAULT_QUEUE)
    f.close()
    f = open('data/queue.json', 'r')
    queue = json.loads(f.read())
    socketapp.emit("Queue Update", queue)

@socketapp.on('Change User Order')
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
@authenticated_only
def change_order(data):
    global queue
    print("Received user song order change")
    order = json.loads(data)
    print(order)
    user = order['user']
    if session['admin'] or session['username'] == user:
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
    else:
        print("Auth error")


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
    if session['admin'] or session['username'] == data['user']:
        song_id = data['id']
        to_delete = -1
        for i in range(len(queue['list'][data['user']])):
            if to_delete is not -1:
                queue['list'][data['user']][i]["iter"] = queue['list'][data['user']][i]["iter"] - 1
            elif queue['list'][data['user']][i]["id"] == song_id:
                to_delete = i
        del queue['list'][data['user']][to_delete]
        if len(queue['list'][data['user']]) is 0:
            queue['inactive'].append(data['user'])
        # TODO: add case for when num songs = 0
        print("Deleted song " + song_id)
        update_queue()
        # emit('User Update Response', ret, broadcast=False)

@socketapp.on('Show or Hide User')
@admin_only
def showhide_user(username):
    global queue
    if username in queue['hidden']:
        queue['hidden'].remove(username)
    else:
        queue['hidden'].append(username)
    update_queue()

@socketapp.on("Singer Update")
@admin_only
def singer_update(code):
    if queue['active'] == "None" or len(getActiveUsers()) < 2:
        return
    if code == "next":
        next_singer()
    elif code == "prev":
        prev_singer()

@socketapp.on("Request Order Status")
@authenticated_only
def requested_order_status(username):
    if session['admin'] or session['username'] == username:
        emit('Order Status', get_order_data(), broadcast=False)


def next_singer():
    validSingers = getActiveUsers()
    currentIndex = validSingers.index(queue['active'])
    currentIndex = currentIndex + 1
    if currentIndex == len(validSingers):
        currentIndex = 0
    queue['active'] = validSingers[currentIndex]
    update_queue()

def prev_singer():
    validSingers = getActiveUsers()
    currentIndex = validSingers.index(queue['active'])
    currentIndex = currentIndex - 1
    if currentIndex == -1:
        currentIndex = len(validSingers) - 1
    queue['active'] = validSingers[currentIndex]
    update_queue()

def update_order():
    socketapp.emit("Order Status", get_order_data())

def get_order_data():
    order = getActiveUsers()
    singer = queue['active']
    data = {
        "singer":singer,
        "order":order
    }
    return data