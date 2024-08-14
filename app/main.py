import app.crud as crud, app.schema as schema
import app.models 
from fastapi import Depends, FastAPI, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import authenticate_user, create_access_token, get_current_user
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from typing import List
# from app.models import Movie, Rating
from app.logger import get_logger

logger = get_logger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# routers
user_router = APIRouter(prefix="", tags=["users"])
movie_router = APIRouter(prefix="/movies", tags=["movies"])
rating_router = APIRouter(prefix="/ratings", tags=["ratings"])
comments_router = APIRouter(prefix="/comments", tags=["comments"])

@app.get('/')
def home():
    return "My Movie Application"

@user_router.post("/signup")
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    logger.info('Creating user...')
    db_user = crud.get_user_by_username(db, username=user.username)
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    db_user_by_fullname = crud.get_user_by_fullname(db, full_name=user.full_name)
    if db_user:
        logger.error(f"user trying to register but username entered already exist: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    if db_user_by_email:
        logger.error(f"User trying to register but email entered already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    if db_user_by_fullname:
        logger.error(f"User trying to register but email entered already exists: {user.full_name}")
        raise HTTPException(status_code=400, detail="Fullname already registered")
    logger.info('User successfully created.')
    return crud.create_user(db=db, user=user)


@user_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info('user access token created')
    return {"access_token": access_token, "token_type": "bearer"}


@movie_router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.MovieResponseModel])
def get_movies(db: Session = Depends(get_db),  offset: int = 0, limit: int = 10):
    movies = crud.get_movies(
        db, 
        offset=offset, 
        limit=limit
    )
    logger.info('lists of all movies')
    return movies


@movie_router.get("/{movie_id}", status_code=status.HTTP_200_OK, response_model=schema.MovieResponseModel)
def get_movie(movie_id: str, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    logger.warning('movie not found')
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found")
    return movie
   


@movie_router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.MovieResponseModel)
def create_movie(payload: schema.MovieCreate, user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = crud.create_movie(
        db, 
        payload,
        user_id=user.id
    )
    logger.info("created a movie")
    return movie


@movie_router.put('/{movie_id}', status_code=status.HTTP_201_CREATED, response_model=schema.MovieResponseModel)
def update_movie(movie_id: int, payload: schema.MovieUpdate, user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = crud.update_movie(db, movie_id, payload, user.id)
    logger.warning('movie not found')
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    logger.info('movie updated')
    return movie



@movie_router.delete('/{movie_id}')
def delete_movie(movie_id: str, user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning('movie not found')
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    if movie.user_id != user.id:
        logger.warning(f'User {user.id} attempted to delete a movie they do not own')
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f'You are not permitted to delete this movie: {movie.title}')
    
    crud.delete_movie(db, movie_id, user.id)
    logger.info(f'movie {movie_id} deleted')
    return {'message': f'movie {movie_id} deleted successfully'}

# rating endpoint
@rating_router.post('/{movie_id}', response_model=schema.RatingResponseModel)
def create_rating(payload: schema.RatingCreate, movie: schema.Movie = Depends(get_movie), user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rating = crud.create_rating(
        db,
        payload,
        movie_id = movie.id,
        user_id= user.id
        )
    logger.info('rated created successfully')
    return rating


@rating_router.get('/{movie_id}/rate', response_model=List[schema.RatingResponseModel])
def get_rating_by_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning('movie not found')
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='movie not found')
    ratings = crud.get__rating_by_movie_id(db,
                                 movie_id
                                  )
    logger.info('list of ratings for a movie')
    return ratings
    

# delete rating
@rating_router.delete('/{rating_id}')
def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user:schema.User = Depends(get_current_user)):
    existing_rating = crud.get_rating_by_id(db, rating_id)
    if not existing_rating:
        logger.error('rating not found')
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='rating not found')
    logger.info('rating deleted')
    crud.delete_rating(db, rating_id, current_user.id)
    return {'message': 'rating deleted successfully'}


# comments, response_model=schema.CommentResponse
@comments_router.post('/', response_model=schema.CommentResponse)
def create_comment(comment: schema.CommentCreate, 
                   movie_id: int = 1, 
                   current_user: schema.User = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning('movie not found')
        raise HTTPException(status_code=404, detail="Movie not found")
    db_comment = crud.create_comment(db, comment, current_user.id, movie_id)
    logger.info('comment created successfully')
    return db_comment


# create reply
@comments_router.post('/{comment_id}/replies', response_model=schema.CommentResponse)
def create_reply(payload: schema.ReplyCreate, comment_id:int, current_user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_comment = crud.get_comment_by_id(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    reply = crud.create_reply(db, payload, comment_id, current_user.id)
    db_comment.replies.append(reply)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


# to get comments for a post, including nested replies
@comments_router.get('/{movie_id}/comments', response_model=schema.MovieCommentResponseModel)
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie = crud.get_comments(db, movie_id)
    return movie

@comments_router.delete('/{comment_id}')
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    comment = crud.get_comment_by_id(db, comment_id)
    logger.warning('comment not found')
    if not comment:
        raise HTTPException(status_code=404, detail="comment not found")
    logger.info('comment deleted')
    crud.delete_comment(db, comment_id, current_user.id)
    return {'message': 'comment deleted successfuly'}

# reply delete
@comments_router.delete('/{reply_id}')
def delete_reply(reply_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    reply = crud.get_reply_by_id(db, reply_id)
    logger.warning('reply not found')
    if not reply:
        raise HTTPException(status_code=404, detail="reply not found")
    logger.info('reply deleted')
    crud.delete_reply(db, reply_id, current_user.id)
    return {'message': 'reply deleted successfuly'}



# Include routers in the main app
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(rating_router)
app.include_router(comments_router)

