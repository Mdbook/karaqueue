import os, json, time
from flask_socketio import send, emit, disconnect
from socket_worker import socketapp, authenticated_only, admin_only, delete_user
from flask import session
from karaqueue import KaraQueue
Queue = KaraQueue()
# DEFAULT_QUEUE = "{\"order\":[],\"list\":{},\"inactive\":[],\"hidden\":[],\"active\":\"None\"}"
if os.path.exists(Queue.path):
    Queue.Load()

    # f = open("data/queue.json", "w")
    # f.write(DEFAULT_QUEUE)
    # f.close()


# def add_to_queue(req:Request):
#     if not req.username in queue['list'].keys():
#         queue['list'][req.username] = []
#     # print(len(queue['list'][req.username]))
#     queue['list'][req.username].append({
#         "id":req.id,
#         "song":req.song,
#         "artist":req.author,
#         "timestamp":req.timestamp,
#         "username":req.username,
#         "iter":len(queue['list'][req.username]),
#         # "active":req.active
#     })
#     if not req.username in queue['order']:
#         if len(getActiveUsers()) == 0:
#             queue['active'] = req.username
#         queue['order'].append(req.username)
#     if req.username in queue['inactive']:
#         queue['inactive'].remove(req.username)
#     print(queue)
#     update_queue()

# def getActiveUsers():
#     allUsers = queue['order']
#     hiddenUsers = queue['hidden']
#     inactiveUsers = queue['inactive']
#     activeUsers = []
#     for user in allUsers:
#         if not (user in hiddenUsers or user in inactiveUsers):
#             activeUsers.append(user)
#     return activeUsers


def update_queue():
    update_order()
    socketapp.emit("Queue Update", Queue.Export())


@socketapp.on('Add Song for User')
@admin_only
def add_for_user(data):
    username = data['username']
    song = data['song']
    artist = data['artist']
    Queue.Request(username, song, artist)
    update_queue()

@socketapp.on('init_queue')
@admin_only
def init(username):
    print('User "' + username + '" connected is viewing queue.')
    emit('Queue Init', Queue.Export(), json=True, broadcast=False)

@socketapp.on('init_user_queue')
@authenticated_only
def init_user():
    print('User "' + session['username'] + '" connected is viewing queue.')
    username = session['username']
    ret = {
        "username":username,
        "songs":Queue.GetSongs(username)
    }
    # print(ret)
    emit('User Update Response', ret, broadcast=False)

@socketapp.on('clear_queue')
@admin_only
def clear_queue():
    print("Clearing the queue")
    Queue.Wipe()
    socketapp.emit("Queue Update", Queue.Export())

@socketapp.on('Change User Order')
@admin_only
def change_order(data):
    print("Received order change")
    new_order = json.loads(data)
    Queue.Rearrange(new_order)
    update_queue()

@socketapp.on('Change Song Order')
@authenticated_only
def change_order(data):
    print("Received user song order change")
    order = json.loads(data)
    user = order['user']
    if session['admin'] or session['username'] == user:
        Queue.ReorderUserSongs(order['user'], order['list'])
        update_queue()
    else:
        print("Auth error")

# def change_order(data):
#     global queue
#     print("Received user song order change")
#     order = json.loads(data)
#     # print(order)
#     user = order['user']
#     if session['admin'] or session['username'] == user:
#         ids = order['list']
#         oldids = queue['list'][user]
#         for oldid in oldids:
#             if oldid['id'] not in ids:
#                 ids.append(oldid)
#         i = 0
#         newUserOrder = []
#         for songid in ids:
#             for song in queue['list'][user]:
#                 if song['id'] == songid:
#                     song['iter'] = i
#                     newUserOrder.append(song)
#                     i += 1
#         # print("new order!")
#         # print(newUserOrder)
#         queue['list'][user] = newUserOrder
#         update_queue()
#     else:
#         print("Auth error")


@socketapp.on('Get User')
@authenticated_only
def get_user(username):
    if session['admin'] or session['username'] == username:
        ret = {
            "username":username,
            "songs":Queue.GetSongs(username)
        }
        # print(ret)
        emit('User Update Response', ret, broadcast=False)

@socketapp.on('Delete Song')
@authenticated_only
def delete_song(data):
    if session['admin'] or session['username'] == data['user']:
        usr = data['user']
        Queue.DeleteSong(data['user'], data['id'])
        if Queue.Active(usr):
            Queue.Next()
            if Queue.Active(usr):
                Queue.ClearActive()
        update_queue()
# def delete_song(data):
#     global queue
#     if session['admin'] or session['username'] == data['user']:
#         song_id = data['id']
#         to_delete = -1
#         for i in range(len(queue['list'][data['user']])):
#             if to_delete is not -1:
#                 queue['list'][data['user']][i]["iter"] = queue['list'][data['user']][i]["iter"] - 1
#             elif queue['list'][data['user']][i]["id"] == song_id:
#                 to_delete = i
#         del queue['list'][data['user']][to_delete]
#         if len(queue['list'][data['user']]) is 0:
#             if queue['active'] == data['user']:
#                 next_singer()
#                 if queue['active'] == data['user']:
#                     queue['active'] = None
#             queue['inactive'].append(data['user'])
#         # TODO: add case for when num songs = 0
#         print("Deleted song " + song_id)
#         update_queue()
        # emit('User Update Response', ret, broadcast=False)

@socketapp.on('Show or Hide User')
@admin_only
def showhide_user(username):
    Queue.ToggleHidden(username)
    update_queue()

@socketapp.on("Singer Update")
@admin_only
def singer_update(code):
    if code == "next":
        Queue.Next()
    elif code == "prev":
        Queue.Prev()
    update_queue()

@socketapp.on("Request Order Status")
@authenticated_only
def requested_order_status(username):
    if session['admin'] or session['username'] == username:
        emit('Order Status', get_order_data(), broadcast=False)


# def next_singer():
#     validSingers = getActiveUsers()
#     # print(getActiveUsers())
#     if len(validSingers) == 0:
#         # print('gotcha')
#         queue['active'] = "None"
#         update_queue()
#         return
#     currentIndex = validSingers.index(queue['active'])
#     currentIndex = currentIndex + 1
#     if currentIndex == len(validSingers):
#         currentIndex = 0
#     queue['active'] = validSingers[currentIndex]
#     update_queue()

# def prev_singer():
#     validSingers = getActiveUsers()
#     currentIndex = validSingers.index(queue['active'])
#     currentIndex = currentIndex - 1
#     if currentIndex == -1:
#         currentIndex = len(validSingers) - 1
#     queue['active'] = validSingers[currentIndex]
#     update_queue()

def update_order():
    socketapp.emit("Order Status", Queue.GetActiveUsers())

def get_order_data():
    order = Queue.GetActiveUsers()
    singer = Queue.get_active()
    data = {
        "singer":singer,
        "order":order
    }
    return data

@socketapp.on('delete')
def delete(uname):
    socketapp.emit("Force Logout", uname)
    delete_user(uname)
    Queue.DeleteUser(uname)
    update_queue()