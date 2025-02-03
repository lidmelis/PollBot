from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from app.core.db import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, index=True, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)


class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, ForeignKey("users.peer_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    is_single_use = Column(Boolean, default=False)
    
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    text = Column(String, nullable=False)
    with_options = Column(Boolean, default=False, nullable=False)
    with_multipy_options = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

class Reply(Base):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, index=True, nullable=False)
    peer_id = Column(Integer, index=True,  nullable=False)
    reply = Column(String, default="")