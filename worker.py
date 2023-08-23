import os, json, time
from id_gen import generate_id

if not os.path.exists("data/queue.json"):
    f = open("data/queue.json", "w")
    f.write("{\"order\":[]}")
    f.close()

f = open('data/queue.json', 'r')
queue = json.loads(f.read())

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
    if not req.username in queue.keys():
        queue[req.username] = []
    queue[req.username].append({
        "id":req.id,
        "song":req.song,
        "artist":req.author,
        "timestamp":req.timestamp
    })
    if not req.username in queue['order']:
        queue['order'].append(req.username)
    print(queue)