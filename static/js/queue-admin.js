var socket = io();
var currentUser = null;
var showHidden = true;
document.getElementById('show-hidden').addEventListener('change', function (e) {
    console.warn('buh')
    let items = document.getElementsByClassName('queue-item');
    showHidden = !showHidden;
    for (let i = 0; i < items.length; i++) {
        if (items[i].classList.contains('display-hidden')) {
            items[i].classList.remove('display-hidden');
        } else if (items[i].classList.contains('hidden')) {
            items[i].classList.add('display-hidden');
        }
    }
});

function addSong() {
    let song = prompt("Song name:");
    if (!song) {
        return
    }
    let artist = prompt('Artist:');
    if (!artist) {
        return
    }
    socket.emit("Add Song for User", {
        "username": currentUser,
        "song": song,
        "artist": artist
    })
}

function clear_queue() {
    if (confirm("Are you sure you want to completely clear the queue?")) {
        socket.emit('clear_queue')
    }
}
socket.on('connect', function () {
    socket.emit('init_queue', globalUsername);
});
socket.on('Queue Init', function (data) {
    iterate(data)
    init_sortable()
});

socket.on('Queue Update', function (data) {
    console.log(data);
    iterate(data);
    if (currentUser != null) {
        if (data['order'].indexOf(currentUser) != -1) {
            getUser(currentUser);
        } else {
            clearUserQueue();
            document.getElementById('user-id').innerText = "N/A";
            document.getElementById('user-id').title = "N/A";
        }
    }
});

function next_singer() {
    socket.emit('Singer Update', "next");
}

function prev_singer() {
    socket.emit('Singer Update', "prev");
}

function showHideUser(username) {
    socket.emit('Show or Hide User', username);
}

function init_sortable() {
    var queue_list = document.getElementById('queue_list');
    var sortable = Sortable.create(queue_list, {
        onEnd: function ( /**Event*/ evt) {
            var itemEls = evt.to.getElementsByTagName('div');
            let newOrder = []
            console.log(itemEls)
            for (i in itemEls) {
                if (itemEls[i].innerText) {
                    newOrder.push(itemEls[i].innerText);
                }
            }
            pushNewOrder(newOrder);
        }
    });
    var user_queue_list = document.getElementById('user_queue_list');
    var sortable = Sortable.create(user_queue_list, {
        onEnd: function ( /**Event*/ evt) {
            var itemEls = evt.to.getElementsByTagName('div');
            var newOrder = []
            console.log(itemEls)
            for (i in itemEls) {
                if (itemEls[i].id) {
                    newOrder.push(itemEls[i].id);
                }
            }
            pushNewSongOrder(newOrder);
        }
    });
}

function pushNewOrder(order) {
    socket.emit('Change User Order', JSON.stringify(order));
}

function pushNewSongOrder(order) {
    let newOrder = {
        'user': currentUser,
        'list': order
    }
    socket.emit('Change Song Order', JSON.stringify(newOrder));
}

function iterate(queue) {
    clearQueueList();
    console.log(Object.keys(queue['list']).length)
    // userlist = document.getElementById('user_list')
    if (queue['order'].length >= 1) {
        for (let i in queue['order']) {
            let username = queue['order'][i];
            let isInactive = queue['inactive'].indexOf(username) != -1;
            let isHidden = queue['hidden'].indexOf(username) != -1;
            let isActive = queue['active'] == username;
            addQueueItem(username, isInactive, isHidden, isActive)
        }
        // document.getElementById('queue_list').getElementsByTagName('div')[queue['active']].classList.add('active')
    }
}

socket.on("User Update Response", function (response) {
    // console.warn(response)
    clearUserQueue();
    document.getElementById('user-id').innerText = trimString(response['username'], 16);
    document.getElementById('user-id').title = response['username'];
    if (response['songs'].length >= 1) {
        for (let i in response['songs']) {
            // console.log(response[i])
            addToUserQueue(response['songs'][i].song, response['songs'][i].artist, response['songs']
                [i].id, response['songs'][i].iter);
        }
    }
});

function clearQueueList() {
    let queuelist = document.getElementById('queue_list')
    queuelist.innerHTML = "";
}

function clearUserQueue() {
    let queuelist = document.getElementById('user_queue_list')
    queuelist.innerHTML = "";
}

function getUser(username) {
    // currentUser = username;
    console.log(currentUser)
    socket.emit('Get User', username)
}

function addQueueItem(username, isInactive, isHidden, isActive) {
    let queuelist = document.getElementById('queue_list');
    let label = document.createElement('div');
    let hide = document.createElement('div');
    hide.className = "eye-icon"
    label.className = "queue-item"
    if (isInactive)
        label.classList.add("inactive")
    if (isHidden) {
        label.classList.add("hidden")
        if (!showHidden) {
            label.classList.add('display-hidden');
        }
    }
    if (isActive)
        label.classList.add('active')
    label.innerText = username;
    label.appendChild(hide)
    hide.addEventListener('click', function (e) {
        showHideUser(e.target.parentElement.innerText);
        e.stopPropagation();
    });
    label.addEventListener('click', function (e) {
        currentUser = username;
        getUser(e.target.innerText)
    });
    queuelist.appendChild(label)
    console.log('done');
}

function deleteSong(id) {
    socket.emit("Delete Song", {
        "id": id,
        "user": currentUser
    })
}

function addToUserQueue(song, artist, id, iter) {
    let queuelist = document.getElementById('user_queue_list');
    let itemsIn = queuelist.getElementsByTagName('div');
    let label = document.createElement('div');
    let trash = document.createElement('img');
    trash.src = "/static/assets/trashcan.png";
    trash.className = "trash-icon"
    label.className = "queue-item"
    label.setAttribute('order', iter)
    label.innerText = song + " - " + artist;
    label.id = id;
    label.appendChild(trash)
    trash.addEventListener('click', function (e) {
        if (confirm("Delete Song \"" + e.target.parentElement.innerText + "\"?"))
            deleteSong(e.target.parentElement.id);
        e.stopPropagation();
    });
    if (itemsIn.length == 0) {
        queuelist.appendChild(label)
    } else {
        for (let i = 0; i < itemsIn.length; i++) {
            let ele = itemsIn[i];
            if (ele.getAttribute('order') > iter) {
                queuelist.insertBefore(label, ele);
                return;
            }
        }
        queuelist.appendChild(label)
    }
    document.getElementById('add-song-button').style.display = "block";
    // console.log('done');
}