'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

import hashlib
import os

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# hash and salt password
def hash_password(password: str, salt: bytes) -> tuple:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        # generate salt
        salt = os.urandom(32)

        # generate hash
        hashed_password = hash_password(password, salt)

        # insert into db
        user = User(username=username, password=hashed_password, salt=salt)
        session.add(user)
        session.commit()

def get_alluser():
    with Session(engine) as session:
        all_users = session.query(User).all()
        return [user.username for user in all_users]


# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    
def get_allfri(usrname: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=usrname).first()
        if user:
            if user.friends:
                return user.friends
        else:
            return None
    
def get_allsend(usrname: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=usrname).first()
        
        if user:
            # senders(obj1.usrname)
            all_send = user.senders
            
            sended_to = [sender.receiver_id for sender in all_send]
            
            return sended_to
        else:
            return None  
    
def get_allrev(usrname: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=usrname).first()
        if user:
            # senders(obj1.usrname)
            all_rev = user.receivers
            
            reveived_from = [receiver.sender_id for receiver in all_rev]
            
            return reveived_from
        else:
            return None  

# add_fri 
def add_fri(usrname: str, friname: str):
    with Session(engine) as session:
        #get usr
        user = session.query(User).filter_by(username=usrname).first()
        friend = session.query(User).filter_by(username=friname).first()

        # Check if both user and friend exist
        if user and friend:
            friendship1 = Friendship(username_id=user.username,friname_id=friend.username)
            friendship2 = Friendship(username_id=friend.username,friname_id=user.username)
            session.add_all([friendship1,friendship2])
        else:
            print("User not found.")
        
        session.commit()

# request_fri   *** sender , 
def send_request(sender: str, receiver : str):
    with Session(engine) as session:
        #get usr
        send = session.query(User).filter_by(username=sender).first()
        rev = session.query(User).filter_by(username=receiver).first()

        # Check if both user and friend exist
        if send and rev:
            request = FriendshipRequest(sender_id=send.username,receiver_id=rev.username)
            session.add(request)
        else:
            print("User not found.")
        
        session.commit()    

# approved, disapproved
def approve(sender: str, receiver:str):
    add_fri(sender,receiver)
    with Session(engine) as session:
        session.query(FriendshipRequest).filter_by(sender_id=sender, receiver_id=receiver).delete()
        session.commit()

def disapprove(sender: str, receiver:str):
    with Session(engine) as session:
        session.query(FriendshipRequest).filter_by(sender_id=sender, receiver_id=receiver).delete()
        session.commit()

def reset_db():
    # Drop all existing tables
    Base.metadata.drop_all(engine)
    # Recreate tables
    Base.metadata.create_all(engine)



# send message
def send_msg(key: str,content : str, sender: str, receiver):
    with Session(engine) as session:
        #get usr
        send = session.query(User).filter_by(username=sender).first()
        rev = session.query(User).filter_by(username=receiver).first()

        # Check if both user and friend exist
        if send and rev:
            message = Message(public_key=key,message=content,sender_id=send.username,receiver_id=rev.username)
            session.add(message)
            formatted_message = f"{send.username}: {content}"
        else:
            print("User not found.")
        
        session.commit() 
        return formatted_message     

def display_msg(sender: str, receiver):
    with Session(engine) as session:
        send = session.query(User).filter_by(username=sender).first()
        rev = session.query(User).filter_by(username=receiver).first()

        if send and rev:
            messages = session.query(Message).filter(
                or_(
                    and_(Message.sender_id == send.username, Message.receiver_id == rev.username),
                    and_(Message.sender_id == rev.username, Message.receiver_id == send.username)
                )
            ).order_by(Message.timestamp).all()

            formatted_messages = []
            for message in messages:
                formatted_messages.append(f"{message.timestamp} - {message.sender.username}: {message.message}")

            return formatted_messages

        else:
            print("User not found.")
        
