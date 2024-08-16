import pytest
from fastapi.testclient import TestClient
from app import models
from app.main import app, get_db
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from argon2 import PasswordHasher
# from app import schema
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status



# Using in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///"

engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False}, 
                       poolclass=StaticPool,)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    
    yield
    Base.metadata.drop_all(bind=engine)


# Test successful signup
def test_signup(setup_db):
    response = client.post("/signup", json={
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

# Test successful login
def test_login(setup_db): 
     
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


# @pytest.fixture
def test_create_movie(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]

    movie_response = client.post("/movies/", json={
        "title": "Test Movie",
        "genre": "A test movie description",
        "publisher": "Test Publisher",
        "year_published": "2024"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    print(movie_response.json())  # Debugging line to print the error response
    assert movie_response.status_code == 201
    # assert response.json()["title"] == "Test Movie"
    movie_data = movie_response.json()
    
    return movie_data, token


def test_get_movies(setup_db):
    response = client.get("/movies/")
    assert response.status_code == 200
    assert response.json()

def test_get_movie_by_id(setup_db):
    response = client.get("/movies/1")
    
    assert response.status_code == 200
    assert response.json()['id'] == 1
    
    
    # Test getting a movie that does not exist
    response = client.get("/movies/9999")  # Using a very high ID that doesn't exist
    assert response.status_code == 404  # Expecting a 404 Not Found error
    assert response.json()["detail"] == "movie not found"  # Check the error message
    
    
def test_update_movie_by_id(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]

    movie_id = 1
    response = client.put(f"/movies/{movie_id}", json={
        "title": "Updated Movie Title",
        "genre": "Updated genre",
        "publisher": "Updated Publisher",
        "year_published": "2025"
    }, headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 201
    assert response.json()["title"] == "Updated Movie Title"  # Confirm the title is updated
    
    wrong_movie_id = 9999
        # Test getting a movie that does not exist
    response = client.get(f"/movies/{wrong_movie_id}")  # Using a very high ID that doesn't exist
    assert response.status_code == 404  # Expecting a 404 Not Found error
    assert response.json()["detail"] == "movie not found"  # Check the error message
    
    
def test_delete_movie(setup_db):
        login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
        })
        token = login_response.json()["access_token"]

        movie_id = 1
        # to delete movie by id 1
        response = client.delete(f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}" })
        
        assert response.status_code == 200
        # assert response.json()["id"] == '1'
        assert response.json()['message'] == f'movie {movie_id} deleted successfully'

  
  
  
    # rating test......
    
    # create rating
def test_create_rating(setup_db):
    login_response = client.post("/login", data={
    "username": "testuser",
    "password": "testpassword"
    })
    token = login_response.json()["access_token"]
     
    # Create a movie before creating the rating
    # suppose be fixture oo, movie data
    movie_response = client.post("/movies", json={
            "title": "Test Movie",
            "genre": "A test movie description",
            "publisher": "Test Publisher",
            "year_published": "2024"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    # Ensure the movie was created 
    assert movie_response.status_code == 201
    movie_id = movie_response.json()['id']
    
    response = client.post(f'/ratings/{movie_id}', json={"rating": "4.0"}, headers={
        "Authorization": f"Bearer {token}"
    })
    # assert it rating created successfully
    assert response.status_code == 200
    assert response.json()['rating'] == 4.0


# def test_create_rating(setup_db, create_movie):
#     movie_data, token = create_movie
    
#     response = client.post(f'/ratings/{movie_data["id"]}', json={"rating": "4.0"})

#     # Retrieve ratings for the movie
#     response = client.get(f"/ratings/{movie_data['id']}")


#     assert response.status_code == 200
#     assert len(response.json()) == 0
#     assert response.json()[0]['movie_id'] == movie_data['id']


    # create rating for movie not found
def test_create_rating_wrond_movie_id(setup_db):
    login_response = client.post("/login", data={
    "username": "testuser",
    "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    wrong_movie_id = 4444
    
    response = client.post('/ratings/{wrong_movie_id}', json={"rating": "4.0"}, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()['detail'] == 'movie not found'
    
    
# # ratings for a movie
# def test_get_rating_by_movie(setup_db):
#     movie_id = client.post(f"/movies{movie_id}", json={
#             "title": "Test Movie",
#             "genre": "A test movie description",
#             "publisher": "Test Publisher",
#             "year_published": "2024"
#     })
#     assert movie_id.status_code == 201
#     movie_id = movie_id.json()['id']
    
#     response = client.get(f"/ratings/{movie_id}/rate")
    
#     assert response.status_code == 200
#     assert response.json()['id'] == movie_id
    

    

# create rating
# def test_create_rating(setup_db):
#     login_response = client.post("/login", data={
#     "username": "testuser",
#     "password": "testpassword"
#     })
#     token = login_response.json()["access_token"]
     
#     # Create a movie before creating the rating
#     # suppose be fixture oo, movie data
   
    
#     # Ensure the movie was created 
    
    
#     response = client.post(f'/ratings/{movie_id}', json={"rating": "4.0"}, headers={
#         "Authorization": f"Bearer {token}"
#     })
#     # assert it rating created successfully
#     assert response.status_code == 200
#     assert response.json()['rating'] == 4.0


