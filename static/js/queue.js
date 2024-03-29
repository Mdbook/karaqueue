var socket = io();

function clear_queue() {
  if (confirm("Are you sure you want to completely clear the queue?")) {
    socket.emit("clear_queue");
  }
}
socket.on("connect", function (response) {
  socket.emit("init_user_queue");
  init_sortable();
});

function init_sortable() {
  var user_queue_list = document.getElementById("user_queue_list");
  var sortable = Sortable.create(user_queue_list, {
    onEnd: function (evt) {
      var itemEls = evt.to.getElementsByTagName("div");
      var newOrder = [];
      console.log(itemEls);
      for (i in itemEls) {
        if (itemEls[i].id) {
          newOrder.push(itemEls[i].id);
        }
      }
      pushNewSongOrder(newOrder);
    },
  });
}

socket.on("Queue Update", function (data) {
  getUser(globalUsername);
});

function pushNewSongOrder(order) {
  let newOrder = {
    user: globalUsername,
    list: order,
  };
  socket.emit("Change Song Order", JSON.stringify(newOrder));
}

socket.on("User Update Response", function (response) {
  clearUserQueue();
  if (response["songs"].length >= 1) {
    for (let i in response["songs"]) {
      // console.log(response[i])
      addToUserQueue(
        response["songs"][i].song,
        response["songs"][i].artist,
        response["songs"][i].id,
        response["songs"][i].iter
      );
    }
  }
});

function clearUserQueue() {
  let queuelist = document.getElementById("user_queue_list");
  queuelist.innerHTML = "";
}

function getUser(username) {
  socket.emit("Get User", username);
}

function deleteSong(id) {
  socket.emit("Delete Song", {
    id: id,
    user: globalUsername,
  });
}

function addToUserQueue(song, artist, id, iter) {
  let queuelist = document.getElementById("user_queue_list");
  let itemsIn = queuelist.getElementsByTagName("div");
  let label = document.createElement("div");
  let trash = document.createElement("img");
  trash.src = "/static/assets/trashcan.png";
  trash.className = "trash-icon";
  label.className = "queue-item";
  trash.classList.add("icon-always-visible");
  label.setAttribute("order", iter);
  label.innerText = song + " - " + artist;
  label.id = id;
  label.appendChild(trash);
  trash.addEventListener("click", function (e) {
    if (confirm('Delete Song "' + e.target.parentElement.innerText + '"?'))
      deleteSong(e.target.parentElement.id);
    e.stopPropagation();
  });
  if (itemsIn.length == 0) {
    queuelist.appendChild(label);
  } else {
    for (let i = 0; i < itemsIn.length; i++) {
      let ele = itemsIn[i];
      if (ele.getAttribute("order") > iter) {
        queuelist.insertBefore(label, ele);
        return;
      }
    }
    queuelist.appendChild(label);
  }
  // console.log('done');
}
