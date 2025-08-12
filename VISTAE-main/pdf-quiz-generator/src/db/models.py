from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("student", "admin"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    quiz_results = relationship("QuizResult", back_populates="user")

class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    options = Column(String, nullable=False)  # comma-separated options
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    user_answers = relationship("UserAnswer", back_populates="question")

    def get_options_list(self):
        return self.options.split(',')

class UserAnswer(Base):
    __tablename__ = 'user_answers'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('quiz_questions.id'), nullable=False)
    user_answer = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)  # optional link to user

    question = relationship("QuizQuestion", back_populates="user_answers")
    user = relationship("User")

class QuizResult(Base):
    __tablename__ = 'quiz_results'

    id = Column(Integer, primary_key=True, index=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percentage = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    user = relationship("User", back_populates="quiz_results")