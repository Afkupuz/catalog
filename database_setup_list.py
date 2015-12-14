import sys
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

def _today():
    now = datetime.datetime.now()
    return now


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name= Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    creation_date = Column(Date, default= _today)


class Subjects(Base):

    __tablename__ = 'subjects'
    
    title = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    body = Column(String(999), nullable = False)
    creation_date = Column(Date, default= _today)
    update_date = Column(Date, onupdate= _today)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    response1 = relationship("Response", cascade = "all, delete-orphan")

    @property
    def serialize(self):
        # Return object data in easily serializeable format
        return {
            'title': self.title,
            'id': self.id,
            'body': self.body,
            'user_id': self.user_id,
        }


class Response(Base):

    __tablename__ = 'response'
    
    id = Column(Integer, primary_key = True)
    text = Column(String(999))
    subjects_id = Column(Integer, ForeignKey('subjects.id'))
    subjects  = relationship(Subjects)
    creation_date = Column(Date, default= _today)
    update_date = Column(Date, onupdate= _today)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return object data in easily serializeable format
        return {
            'id': self.id,
            'text': self.text,
            'subjects_id': self.subjects_id,
            'user_id': self.user_id
    }


engine = create_engine('sqlite:///subjecsandrespnse.db')

Base.metadata.create_all(engine)
