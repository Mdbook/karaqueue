import threading, json, time
from typing import List
from id_gen import Generate_ID


class Request:
    def __init__(self, uname, sng, ath, req_id=Generate_ID(10), ts=time.time()):
        self.id = req_id
        self.username = uname
        self.song = sng
        self.artist = ath
        self.timestamp = ts

    def export(self):
        return {
            "id": self.id,
            "username": self.username,
            "song": self.song,
            "artist": self.artist,
            "timestamp": self.timestamp,
        }


class User:
    def __init__(self, uname):
        self.username = uname
        self.songs: List[Request] = []
        self.lock = threading.Lock()

    def Lock(self):
        self.lock.acquire()

    def Unlock(self):
        self.lock.release()

    def addReq(self, req: Request):
        self.songs.append(req)

    def add(self, song, artist, req_id=Generate_ID(10), timestamp=time.time()):
        req = Request(self.username, song, artist, req_id, timestamp)
        self.addReq(req)

    def export_songs(self):
        self.Lock()
        try:
            reqs = []
            for req in self.songs:
                reqs.append(req.export())
            return reqs
        finally:
            self.Unlock()

    def rearrange(self, new_order):
        self.Lock()
        try:
            newarr = []
            # TODO not quite sure about this algorithm;
            # if something breaks it's probably this
            while len(new_order) > 0:
                for song in self.songs:
                    if song.id == new_order[0]:
                        newarr.append(song)
                        self.songs.remove(song)
                new_order.pop(0)
            if len(self.songs) > 0:
                for song in self.songs:
                    newarr.append(song)
            self.songs = newarr
        finally:
            self.Unlock()

    def remove_song(self, song_id):
        self.Lock()
        try:
            for song in self.songs:
                if song.id == song_id:
                    self.songs.remove(song)
        finally:
            self.Unlock()


class KaraQueue:
    def __init__(self):
        self.order = []
        self.list: dict[str, User] = {}
        self.inactive = []
        self.hidden = []
        self.active = "N/A"
        self.songs_played = 0
        self.songs_requested = 0
        self.users_requested = 0
        self.path = "data/queue.json"
        self.lock = threading.Lock()
        self.file_lock = threading.Lock()

    def load(self, data: dict):
        if "order" in data.keys():
            self.order = data["order"]
        else:
            self.order = []
        if "list" in data.keys():
            l = data["list"]
            for name in l.keys():
                user = User(name)
                for req in l[name]:
                    user.add(req["song"], req["artist"], req["id"], req["timestamp"])
                self.list[name] = user
            # self.list = data['list']
        else:
            self.list = {}
        if "inactive" in data.keys():
            self.inactive = data["inactive"]
        else:
            self.inactive = []
        if "hidden" in data.keys():
            self.hidden = data["hidden"]
        else:
            self.hidden = []
        if "active" in data.keys():
            self.active = data["active"]
        else:
            self.active = "N/A"
        if "songs_played" in data.keys():
            self.songs_played = data["songs_played"]
        else:
            self.songs_played = 0
        if "songs_requested" in data.keys():
            self.songs_requested = data["songs_requested"]
        else:
            self.songs_requested = 0
        if "users_requested" in data.keys():
            self.users_requested = data["users_requested"]
        else:
            self.users_requested = 0
        print("Finished importing.")

    def Load(self):
        print("Loading queue from file: " + self.path)
        f = open(self.path, "r")
        data = json.loads(f.read())
        f.close()
        print("Importing data...")
        self.load(data)

    def get_active(self):
        return self.active

    def get_order(self):
        return self.order

    def get_list(self):
        return self.list

    def get_hidden(self):
        return self.hidden

    def get_inactive(self):
        return self.inactive

    def Lock(self):
        self.lock.acquire()

    def Unlock(self):
        self.lock.release()

    def export(self):
        l = {}
        for username in self.list.keys():
            l[username] = self.list[username].export_songs()
        data = {
            "order": self.order,
            "list": l,
            "inactive": self.inactive,
            "hidden": self.hidden,
            "active": self.active,
            "songs_played": self.songs_played,
            "songs_requested": self.songs_requested,
            "users_requested": self.users_requested,
        }
        return data

    def ReorderUserSongs(self, username, list):
        self.Lock()
        try:
            self.list[username].rearrange(list)
            self.save()
        finally:
            self.Unlock()

    def Export(self):
        self.Lock()
        try:
            return self.export()
        finally:
            self.Unlock()

    def Rearrange(self, new_order: List):
        self.Lock()
        try:
            for username in self.order:
                if username not in new_order:
                    new_order.append(username)
            self.order = new_order
            self.save()
        finally:
            self.Unlock()

    def Wipe(self):
        self.Lock()
        try:
            self.order = []
            self.list = {}
            self.inactive = []
            self.hidden = []
            self.active = "N/A"
            self.songs_played = 0
            self.songs_requested = 0
            self.users_requested = 0
            self.save()
        finally:
            self.Unlock()

    def GetSongs(self, username):
        self.Lock()
        try:
            return self.list[username].export_songs()
        finally:
            self.Unlock()

    def save(self):
        data = self.export()
        self.file_lock.acquire()
        try:
            f = open("data/queue.json", "w")
            f.write(json.dumps(data))
            f.close()
        finally:
            self.file_lock.release()

    def get_active_users(self):
        # self.lock()
        allUsers = self.get_order()
        hiddenUsers = self.get_hidden()
        inactiveUsers = self.get_inactive()
        activeUsers = []
        for user in allUsers:
            if not (user in hiddenUsers or user in inactiveUsers):
                activeUsers.append(user)
        # self.Unlock()
        return activeUsers

    def DeleteSong(self, user, id):
        self.Lock()
        try:
            u = self.list[user]
            u.remove_song(id)
            if len(u.export_songs()) == 0 and not user in self.inactive:
                self.inactive.append(user)
            self.save()
        finally:
            self.Unlock()

    def GetActiveUsers(self):
        self.Lock()
        try:
            return self.get_active_users()
        finally:
            self.Unlock()

    def Active(self, username):
        return username == self.active

    def Request(self, username, song, artist):
        self.Lock()
        try:
            if username not in self.list.keys():
                self.list[username] = User(username)
            self.list[username].add(song, artist)
            if username not in self.order:
                self.order.append(username)
            if username in self.inactive:
                self.inactive.remove(username)
            self.save()
        finally:
            self.Unlock()

    def is_valid_singer(self, name: str):
        return name in self.get_active_users()

    def next_valid_after(self, name: str):  # TODO bug:
        uname = name
        index = self.order.index(uname)
        while not self.is_valid_singer(uname):
            index = index + 1
            if index is len(self.order):
                index = 0
            uname = self.order[index]
        return uname

    def Next(self):
        self.Lock()
        # TODO: add case for when currently up user becomes inactive
        try:
            validSingers = self.get_active_users()
            if len(validSingers) == 1:
                return
            elif len(validSingers) == 0:
                self.active = "None"
                self.save()
                return
            currentActive = self.get_active()
            if currentActive in validSingers:
                currentIndex = validSingers.index(currentActive)  # issue thrown here?
                currentIndex = currentIndex + 1
            else:
                currentIndex = validSingers.index(self.next_valid_after(currentActive))
            if currentIndex == len(validSingers):
                currentIndex = 0
            self.active = validSingers[currentIndex]
            self.save()
        finally:
            self.Unlock()

    def Prev(self):
        self.Lock()
        try:
            validSingers = self.get_active_users()
            if len(validSingers) == 1:
                return
            elif len(validSingers) == 0:
                self.active = "None"
                self.save()
                return
            currentIndex = validSingers.index(self.get_active())
            currentIndex = currentIndex - 1
            if currentIndex == -1:
                currentIndex = len(validSingers) - 1
            self.active = validSingers[currentIndex]
        finally:
            self.Unlock()

    def ClearActive(self):
        self.Lock()
        try:
            self.active = "None"
            self.save()
        finally:
            self.Unlock()

    def ToggleHidden(self, username):
        self.Lock()
        try:
            if username in self.hidden:
                self.hidden.remove(username)
            else:
                self.hidden.append(username)
            self.save()
        finally:
            self.Unlock()

    def DeleteUser(self, username):
        if self.Active(username):
            self.Next()
        self.Lock()
        try:
            if self.Active(username):
                self.active = "None"
            if username in self.order:
                self.order.remove(username)
            if username in self.list.keys():
                self.list.pop(username)
            if username in self.inactive:
                self.inactive.remove(username)
            if username in self.hidden:
                self.hidden.remove(username)
        finally:
            self.save()
            self.Unlock()
