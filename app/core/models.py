from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from app.core.db import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, index=True, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)


class Poll(Base):
    __tablename__ = "polls"  # Fixed double underscores
    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, ForeignKey("users.peer_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    is_single_use = Column(Boolean, default=False)
    first_question_id = Column(Integer, nullable=True)
    def __str__(self):
        return (
            f"Poll(id={self.id}, "
            f"peer_id={self.peer_id}, "
            f"title='{self.title}', "
            f"description={'None' if self.description is None else f'\"{self.description}\"'}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, "
            f"is_single_use={self.is_single_use}, "
            f"first_question_id={self.first_question_id})"
        )

class Question(Base):
    __tablename__ = "questions"  # Fixed double underscores
    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    text = Column(String, nullable=False)
    with_options = Column(Boolean, default=False, nullable=False)
    with_multipy_options = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    next_question_id = Column(Integer, nullable=True)
    prev_question_id = Column(Integer, nullable=True)

    def __str__(self):
        return (f"Question(id={self.id}, poll_id={self.poll_id}, text={self.text}, with_options={self.with_options},\
                with_multipy_options={self.with_multipy_options}, created_at={self.created_at}, updated_at={self.updated_at},\
                next_question_id={self.next_question_id}, prev_question_id={self.prev_question_id})")


'''class Option(Base):
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    question_id = Column(Integer, index=True, nullable=False)'''


class Reply(Base):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, index=True, nullable=False)
    peer_id = Column(Integer, index=True,  nullable=False)
    reply = Column(String, default="")