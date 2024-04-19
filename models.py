'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, LargeBinary,Table,Column, ForeignKey,Integer,DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,Relationship,joinedload,backref,relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from typing import Dict

# data models
class Base(DeclarativeBase):
    pass

# model to store user information

#https://gist.github.com/absent1706/8b6d9bca6434502989c9c1495f35d8b4
#https://stackoverflow.com/questions/37972778/sqlalchemy-symmetric-many-to-one-friendship
#https://youtu.be/vKuKp10LQEM

#many to many
class Friendship(Base):
    __tablename__ = 'friendship'
    username_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'), primary_key=True)
    friname_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'), primary_key=True)

class FriendshipRequest(Base):
    __tablename__ = "friendship_request"
    # id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'), primary_key=True)
    receiver_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'), primary_key=True)

class User(Base):
    __tablename__ = "user"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 
    username: Mapped[str] = mapped_column(String, primary_key=True)
    # password: Mapped[bytes] = mapped_column(LargeBinary)
    # salt: Mapped[bytes] = mapped_column(LargeBinary)

    password: Mapped[int] = mapped_column()
    
    #reference to classname, linkingtable name, table_name
    friends = relationship("User",
                           secondary=Friendship.__tablename__,
                           primaryjoin=(Friendship.username_id == username),
                           secondaryjoin=(Friendship.friname_id == username),
                           backref='friendswith')
    
    senders = relationship(
        'FriendshipRequest',
        foreign_keys='FriendshipRequest.sender_id',
        backref = 'sender'
    )

    receivers = relationship(
        'FriendshipRequest',
        foreign_keys='FriendshipRequest.receiver_id',
        backref = 'recevier'
    )

    sent_messages = relationship("Message", 
                                 foreign_keys="[Message.sender_id]", 
                                 back_populates="sender")
    received_messages = relationship("Message", 
                                     foreign_keys="[Message.receiver_id]", 
                                     back_populates="receiver")

    def __repr__(self):
        return f"{self.username}"


#one_to_many , one usr to many message
class Message(Base):
    __tablename__ = "message"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    #from sender key
    public_key : Mapped[str] = mapped_column(String)
    message : Mapped[str] = mapped_column(String)
    
    sender_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'))
    receiver_id : Mapped[str] = mapped_column(String, ForeignKey('user.username'))
    
    # encrypted_message = Column(LargeBinary, nullable=False)


    # many to one
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

    


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
    