from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from app.core.db import Base
import datetime


class User(Base):
    tablename = "users_test"
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)


class Poll(Base):
    tablename = "polls"
    # Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, ForeignKey("users_test.peer_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    
class Question(Base):
    tablename = "questions"
    # Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)