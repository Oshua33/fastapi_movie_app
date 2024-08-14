from psycopg2 import Timestamp
from sqlalchemy import Column, DateTime, String, Integer,Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    # relationship  movie-user
    # movies = relationship("Movie", back_populates="user")
    
    # # relationshp user-comments
    # comments = relationship("Comment", back_populates="owner")
    
    # # relationship user-rating
    # ratings = relationship("Rating", back_populates="user")
    
    
class Movie(Base):
    __tablename__ = "movies"
    
    # what to make title unquie
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    
    # this is the average rating of all ratings
    rating = Column(Float, nullable=True)
    
    year_published = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    
    # user-movie
    # user = relationship("User", back_populates="movies")
    user = relationship("User")
    
    # movie-rating
    ratings = relationship("Rating", cascade='all, delete-orphan', back_populates="movie")
    
    # movie-comments
    comments = relationship("Comment", cascade='all, delete-orphan', back_populates="movie")


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True )
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    user = relationship("User")
    movie = relationship("Movie", back_populates="ratings")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    comment = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    
    user = relationship("User")
    movie = relationship("Movie", back_populates="comments")
    replies = relationship("Reply", back_populates="comment")
    

class Reply(Base):
    __tablename__ = "replies"
    
    id = Column(Integer, primary_key=True)
    reply = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    
    comment = relationship("Comment", back_populates="replies")
    user = relationship("User")
    
    
    
    
    
    
    
