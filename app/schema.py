from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# user schema
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    full_name: str
    email: str
    password: str
    
class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
    
class UserResponseModel(BaseModel):
    id: int
    username: str
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)



# movie
class MovieBase(BaseModel):
    title: str
    genre: str
    publisher: str
    year_published: int
    
    model_config = ConfigDict(from_attributes=True)
    
class MovieCreate(MovieBase):
    pass
 
class MovieUpdate(MovieBase):
    title: Optional[str] = None
    genre: Optional[str] = None
    publisher: Optional[str] = None
    year_published: Optional[int] = None

class Movie(MovieBase):
    id: int
    user_id: int
    # average_rating
    rating: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)
     
class MovieResponseModel(BaseModel):
    id: int 
    title: str
    genre: str
    publisher: str
    year_published: int
    
    # average_rating
    rating: Optional[float] = None
    user: UserResponseModel

    model_config = ConfigDict(from_attributes=True)
    
    
    
 
# rating
class RatingBase(BaseModel):
    rating: float
        
    model_config = ConfigDict(from_attributes=True)

class RatingCreate(RatingBase):
    pass

# class Rating(RatingBase):
#     id: int
#     user_id: int
#     Movie_id: int
    
class RatingResponseModel(BaseModel):
    id: int
    rating: float
    movie: MovieBase
    user: UserResponseModel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

        

# Comment schemas
class CommentBase(BaseModel):
    comment: str
    
    model_config = ConfigDict(from_attributes=True)
    
class CommentCreate(CommentBase):
    pass



# reply
class ReplyCreate(BaseModel):
    reply: str

class ReplyResponse(BaseModel):
    id: int
    reply: str
    user_id: int
    comment_id: int

class CommentResponse(BaseModel):
    id: int
    comment: str 
    movie: MovieBase
    created_at: datetime
    replies: List[ReplyResponse]

    model_config = ConfigDict(from_attributes=True)


class MovieCommentResponseModel(BaseModel):
    id: int 
    comments: List[CommentResponse] = []

    model_config = ConfigDict(from_attributes=True)
   