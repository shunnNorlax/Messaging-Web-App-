
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, joinedload

class Request(Base):
    __tablename__ = 'request'

    request_id = Column(Integer, primary_key=True)
    text = Column(String(2048))
    created = Column(DateTime)

    def __repr__(self):
        from pprint import pformat; return pformat(vars(self))

class UserRelation(Base):
    __tablename__ = 'user_relation'


    user_id = Column(BigInteger, ForeignKey('user.user_id'), primary_key=True)
    related_user_id = Column(BigInteger, ForeignKey('user.user_id'), primary_key=True)
    request_id = Column(BigInteger, ForeignKey('request.request_id'))

    approved = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[user_id], uselist=False)
    related_user = relationship("User", foreign_keys=[related_user_id],
                                uselist=False)
    request = relationship("Request", uselist=False, cascade="all, delete-orphan", single_parent = True)

    def __repr__(self):
        from pprint import pformat; return pformat(vars(self))

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)

    classmates_from = relationship('User', secondary=UserRelation.__table__,
                               primaryjoin=and_(user_id==UserRelation.__table__.c.user_id, UserRelation.__table__.c.approved==True),
                               secondaryjoin=(user_id==UserRelation.__table__.c.related_user_id))
    classmate_relations_from = relationship('UserRelation',
                               primaryjoin=(user_id==UserRelation.__table__.c.user_id))

    classmates_to = relationship('User', secondary=UserRelation.__table__,
                               primaryjoin=and_(user_id==UserRelation.__table__.c.related_user_id, UserRelation.__table__.c.approved==True),
                               secondaryjoin=(user_id==UserRelation.__table__.c.user_id))
    classmate_relations_to = relationship('UserRelation',
                               primaryjoin=(user_id==UserRelation.__table__.c.related_user_id))

    @property
    def classmates(self):
        return  self.classmates_from + self.classmates_to

    def __repr__(self):
        from pprint import pformat; return pformat(vars(self))

def get_user(db, user_id):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError('User with id {} not found'.format(user_id))
    return user

def remove_classmate_relation(self, user_id, classmate_id):
    user = get_user(db, user_id)
    classmate = get_user(db, classmate_id)
    if classmate in user.classmates_from:
        user.classmates_from.remove(classmate)
        db.commit()

def create_classmate_relation(db, user_id, classmate_id, request_message=''):
    user = get_user(db, user_id)
    classmate = get_user(db, classmate_id)

    relation = UserRelation(related_user=classmate)
    user.classmate_relations_from.append(relation)
    import datetime;
    relation.request = Request(text = request_message, created = datetime.datetime.now())
    db.commit()

def approve_classmate_relation(db, user_id, classmate_id):
    user = get_user(db, user_id)
    classmate = get_user(db, classmate_id)

    relation = db.query(UserRelation)\
            .filter(and_(UserRelation.user==user,
                         UserRelation.related_user==classmate)).first()
    if relation:
        relation.approved = True
        relation.request = None
        db.commit()

def get_unapproved_classmate_relations_from(db, user_id):
    user = get_user(db, user_id)
    return db.query(UserRelation)\
       .filter(and_(UserRelation.user==user, UserRelation.approved==False))\
       .options(joinedload('request'))\
       .all()

def get_unapproved_classmate_relations_to(db, user_id):
    user = get_user(db, user_id)
    return db.query(UserRelation)\
       .filter(and_(UserRelation.related_user==user,
                    UserRelation.approved==False))\
       .options(joinedload('request'))\
       .all()

################## DEMO CODE ##################

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///1.sqlite',echo=True)
Base.metadata.create_all(engine)

con = engine.connect()
trans = con.begin()
for table in reversed(Base.metadata.sorted_tables):
    con.execute(table.delete())
trans.commit()

db = Session(bind=engine)

u1 = User(name='u1')
u2 = User(name='u2')
u3 = User(name='u3')

db.add_all([u1,u2,u3])
db.commit()

create_classmate_relation(db, u1.user_id, u2.user_id, 'Please add me u1')
create_classmate_relation(db, u1.user_id, u3.user_id, 'Please add me u3')
create_classmate_relation(db, u2.user_id, u3.user_id, 'Please add me u3')
get_unapproved_classmate_relations_from(db,u1.user_id)
approve_classmate_relation(db, u1.user_id, u2.user_id)
approve_classmate_relation(db, u1.user_id, u3.user_id)
remove_classmate_relation(db, u1.user_id, u2.user_id)

