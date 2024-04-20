'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()
onlineUsr = set()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    # receiver = request.cookies.get("receiver")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))

    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
    

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


# send message event handler
@socketio.on("send")
def send(sender_name, receiver_name,key, message, room_id):
    emit("incoming", (f"{onlineUsr} is online", "green"), to=int(room_id))
    if receiver_name in onlineUsr:

        # send to db
        msg = db.send_msg(key,message,sender_name,receiver_name)
        emit("incoming", (f"{msg}"), to=room_id)

        # emit("incoming", (f"{sender_name}: {message}"), to=room_id)
    else:
        emit("incoming", (f"{receiver_name} not online"), to=room_id)
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):

    friList = db.get_allfri(sender_name)
    friList = friList if friList is not None else []    
    # emit("incoming", (f"{friList} are fri. Type: {type(friList[0])}", "red"))

    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    # not friend
    # if receiver not in friList:
    #     return f"{receiver} not in fri list"

    # Convert receiver_name to string // as type not the same
    receiver_name_str = str(receiver_name)
    found = False
    for friend in friList:
        if str(friend.username) == receiver_name_str:
            found = True
            break

    if not found:
        return f"{receiver} not in fri list"

    room_id = room.get_room_id(receiver_name)
    #is online
    onlineUsr.add(sender_name)
    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
            # display message_history
        all_msg = db.display_msg(sender_name,receiver_name)
        all_msg = all_msg if all_msg is not None else []
        for msg in all_msg:
            emit("incoming", (msg, "blue")) 
        return room_id
        

    else:
        # if the user isn't inside of any room, 
        # perhaps this user has recently left a room
        # or is simply a new user looking to chat with someone
        room_id = room.create_room(sender_name, receiver_name)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)

        all_msg = db.display_msg(sender_name,receiver_name)
        all_msg = all_msg if all_msg is not None else []
        for msg in all_msg:
            emit("incoming", (msg, "blue"), to=int(room_id)) 




    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    onlineUsr.remove(username)
    room.leave_room(username)
###########################################chatroom######################################



###########################################friendlist####################################
#sendrequest
@socketio.on('send_request')
def send_request(sender, receiver):
    user1 =  db.get_user(sender)
    user2 = db.get_user(receiver)
 
    if user1 is None or user2 is None:
        return "Error: User does not exist!"
    
    db.send_request(sender, receiver)

#accept
@socketio.on('approve')
def approve(sender, receiver):
    user1 =  db.get_user(sender)
    user2 = db.get_user(receiver)
 
    if user1 is None or user2 is None:
        return "Error: User does not exist!"
    
    db.approve(sender, receiver)

#disapprove
@socketio.on('disapprove')
def disapprove(sender, receiver):
    user1 =  db.get_user(sender)
    user2 = db.get_user(receiver)
 
    if user1 is None or user2 is None:
        return "Error: User does not exist!"
    
    db.disapprove(sender, receiver)