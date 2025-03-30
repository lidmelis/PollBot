from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, backref
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
    first_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)

    # Explicitly specify foreign key for questions relationship
    questions = relationship(
        "Question",
        back_populates="poll",
        foreign_keys="Question.poll_id"  # Add this line
    )

    # First question relationship
    first_question = relationship(
        "Question",
        foreign_keys=[first_question_id],  # Explicit foreign key
        post_update=True,
        uselist=False,
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
    next_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)

    # Explicit poll relationship
    poll = relationship(
        "Poll",
        back_populates="questions",
        foreign_keys=[poll_id]  # Add this line
    )

    # Linked list relationships
    next_question = relationship(
        "Question",
        foreign_keys=[next_question_id],
        remote_side=[id],
        backref=backref(
            "previous_question",
            remote_side=[id],
            uselist=False
        ),
        post_update=True,
        uselist=False
    )


'''class Option(Base):
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    question_id = Column(Integer, index=True, nullable=False)'''


class Reply(Base):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, index=True, nullable=False)
    peer_id = Column(Integer, index=True,  nullable=False)
    reply = Column(String, default="")