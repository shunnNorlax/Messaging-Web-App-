'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import *
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship,joinedload,backref
from typing import Dict,List

# data models
class Base(DeclarativeBase):
    pass

#friendship table

# friendship = Table(
#     'friendship',
#     Base.metadata,
#     # ForeignKey (tablename.components)
#     Column('user_username', String, ForeignKey('user.username'),primary_key=True),
#     Column('friend_username', String, ForeignKey('user.username'),primary_key=True)
# )



# model to store user information

#https://gist.github.com/absent1706/8b6d9bca6434502989c9c1495f35d8b4
#https://stackoverflow.com/questions/37972778/sqlalchemy-symmetric-many-to-one-friendship

class Request(Base):
    __tablename__ = 'request'

    request_id = Column(Integer, primary_key=True)
    sender_id = Column(String, ForeignKey('user.username'), primary_key=True)
    receiver_id = Column(String, ForeignKey('user.username'), primary_key=True)
    status = Column(String)  # Pending, Accepted, Rejected, etc.

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

class Friendship(Base):
    __tablename__ = 'friendship'

    user_id = Column(String, ForeignKey('user.username'), primary_key=True)
    friend_id = Column(String, ForeignKey('user.username'), primary_key=True)
    approved = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])

class User(Base):
    __tablename__ = "user"

    username = Column(String, primary_key=True)
    password = Column(LargeBinary)
    salt = Column(LargeBinary)

    friendships: List[Friendship] = relationship("Friendship", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}')>"



# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
