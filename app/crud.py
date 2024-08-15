# from argon2 import hash_password
import app.models as models, app.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.sql import func
from app.utils import hash_password 
from sqlalchemy.orm import Session, joinedload



# Movie CRUD operations with joinedload
def get_movie(db: Session, id: int):
    return db.query(models.Movie).options(
        joinedload(models.Movie.ratings),
        joinedload(models.Movie.comments).joinedload(models.Comment.replies)
    ).filter(models.Movie.id == id).first()

    
def get_movie_by_publisher(db: Session, publisher: str):
    return db.query(models.Movie).filter(models.Movie.publisher == publisher).first()

def get_movie_by_title(db: Session, title: str):
    return db.query(models.Movie).filter(models.Movie.title == title).first()

def get_movie_by_rating(db: Session, movie_id: int):
    return db.query(models.Rating).filter(models.Rating.movie_id == movie_id)

def get_movies(db: Session, offset: int = 0, limit: int = 10):
    return db.query(models.Movie).options(
        joinedload(models.Movie.ratings),
        joinedload(models.Movie.comments).joinedload(models.Comment.replies)
    ).offset(offset).limit(limit).all()


def create_movie(db: Session, movie: schema.MovieCreate, user_id:int = None):
    db_movie = models.Movie(**movie.model_dump(),
                user_id = user_id)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie_payload: schema.MovieUpdate, user_id:int = None):
    movie = get_movie(db, movie_id)
    if not movie:
        return None
    
    if movie.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this movie")
    
    movie_payload_dict = movie_payload.dict(exclude_unset=True)

    for k, v in movie_payload_dict.items():
        setattr(movie, k, v)

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie_id, user_id: int = None):
    db_delete_movie = get_movie(db, movie_id)
    if not db_delete_movie:
        return None

    
    db.delete(db_delete_movie)
    db.commit()
    return {'message': 'movie deleted successfully'}


# user crud
def get_user_by_username(db: Session,username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_fullname(db: Session, full_name: str):
    return db.query(models.User).filter(models.User.full_name == full_name).first()
    

def create_user(db: Session, user: schema.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username = user.username,
        full_name = user.full_name,
        email = user.email,
        hashed_password = hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# new rating
def create_rating(db: Session, rating: schema.RatingCreate, movie_id: int, user_id: int):
    # Check if the user has already rated this movie
    existing_rating = db.query(models.Rating).filter(models.Rating.movie_id == movie_id, models.Rating.user_id == user_id).first()
    
    if existing_rating:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"You have already rated movie_id {movie_id}")
    
     # Check if the rating is within the acceptable range
    if rating.rating < 0 or rating.rating > 5.0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{rating} is invalid, Rating range should be from 0 to 5")
       
    db_rating = models.Rating(**rating.model_dump(),
                              movie_id=movie_id, 
                              user_id=user_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating) 
    
    update_movie_average_rating(db, movie_id)
    return db_rating


def update_movie_average_rating(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    if ratings:
        average_rating = sum(r.rating for r in ratings) / len(ratings)
        movie.rating = round(average_rating, 2)
        
    else:
        movie.rating = None
    
    movie.rating = average_rating
    db.commit()
    db.refresh(movie)

# average_rating i cannot see the calcs in my db or docs tester

def get__rating_by_movie_id(db: Session, movie_id: int):
    # check if movie exist
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # filter all ratings in a movie
    ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    if ratings:
        average_rating = sum(r.rating for r in ratings) / len(ratings)
        movie.rating = round(average_rating, 2)
    return ratings
        

def get_rating_by_id(db: Session, rating_id: int):
    return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

def delete_rating(db: Session, rating_id: int, current_user: int = None):
    db_rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if db_rating:
        movie_id = db_rating.movie_id
        
        db.delete(db_rating)
        db.commit()
        update_movie_average_rating(db, movie_id)
        
    else:
        raise HTTPException(status_code=404, detail=f"Rating_id {rating_id} does not exist")   
    return {'message': 'successfully'}


# comments --
def create_comment(db:Session, payload:schema.CommentCreate, current_user: int, movie_id):
    db_comment = models.Comment(**payload.model_dump(),
                                user_id=current_user,
                                movie_id=movie_id
                             )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


# reply
def create_reply(db: Session, reply: schema.ReplyCreate, comment_id: int, current_user: int):
    db_reply_comment = models.Reply(**reply.model_dump(),
                                    user_id = current_user,
                                    comment_id=comment_id
                                    )
    db.add(db_reply_comment)
    db.commit()
    db.refresh(db_reply_comment)
    return db_reply_comment

    
# get comments and its replies
def get_comments(db: Session, movie_id: int ):
     # Fetch the movie with its comments and their replies
    movie_with_comments = db.query(models.Movie).options(joinedload(models.Movie.comments).joinedload(models.Comment.replies)
    ).filter(models.Movie.id == movie_id).first()
    return movie_with_comments

# get comment by id
def get_comment_by_id(db:Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_reply_by_id(db: Session, reply_id: int):
    return db.query(models.Reply).filter(models.Reply.id == reply_id).first()


# delete a comment
def delete_comment(db: Session, comment_id: int, current_user: int = None):
    db_delete_comment = get_comment_by_id(db, comment_id=comment_id)
    if not db_delete_comment:
        return None
    
    db.delete(db_delete_comment)
    db.commit()
    return {'message': 'success'}


# delete reply
def delete_reply(db: Session, reply_id: int, current_user: int = None):
    db_delete_reply = get_reply_by_id(db, reply_id=reply_id)
    if not db_delete_reply:
        raise HTTPException(status_code=404, detail="reply not found")
        # return None
    
    db.delete(db_delete_reply)
    db.commit()
    return {'message': 'success'}
