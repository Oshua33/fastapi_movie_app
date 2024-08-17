import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base



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
    
    # Debug line to print the error response
    print(movie_response.json())  
    assert movie_response.status_code == 201
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
    response = client.get("/movies/9999")  
    assert response.status_code == 404  
    assert response.json()["detail"] == "movie not found"  
    
    
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
    
    
# test to delete a movie
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

  
  
# # test for ratings endpoints
#  # create rating
def test_create_rating(setup_db):
    login_response = client.post("/login", data={
    "username": "testuser",
    "password": "testpassword"
    })
    token = login_response.json()["access_token"]
     
    # Create a movie before creating the rating
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
def test_get_rating_by_movie(setup_db):
    login_response = client.post("/login", data={
    "username": "testuser",
    "password": "testpassword"
    })
    token = login_response.json()["access_token"]
     
    movie_response = client.post("/movies", json={
            "title": "Test Movie",
            "genre": "A test movie description",
            "publisher": "Test Publisher",
            "year_published": "2024"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert movie_response.status_code == 201
    movie_id = movie_response.json()['id']
    
    response = client.get(f"/ratings/{movie_id}/rate")
    
    assert response.status_code == 200

    
    assert len(response.json()) >= 0 
    

# test endpoint for comment section
# test_create comments 
def test_create_comments(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Create a movie before creating the comment
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
    
    # Use the correct key in the request payload (assuming your schema uses 'comment')
    response = client.post('/comments/', json={"comment": "the movie is funny"}, headers={
        "Authorization": f"Bearer {token}"
    })
    
    # Assert it was created successfully
    assert response.status_code == 201  # Expect a 201 status code for successful creation
    assert response.json()['comment'] == "the movie is funny"
    
    return movie_id, token


# create reply
def test_create_reply(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    comment_response = client.post('/comments/', json={"comment": "the movie is funny"}, headers={
        "Authorization": f"Bearer {token}"
    })
    
     # Assert it was created successfully
    assert comment_response.status_code == 201  
    # Get the comment_id
    comment_id = comment_response.json()['id']
    
    
    response = client.post(f'/comments/{comment_id}/replies/', json={"reply": "yes, very funny"}, headers={"Authorization": f"Bearer {token}"})
    
     # Assert it was created successfully
    assert response.status_code == 200  # Expect a 201 status code for successful creation
    
    replies = response.json()['replies'] 
    assert replies[-1]['reply'] == 'yes, very funny' 
    return comment_id, token
    
    
#  test for getting all comments and replies
def test_get_comments_by_movie_id(setup_db):
    login_response = client.post("/login", data={
    "username": "testuser",
    "password": "testpassword"
    })
    token = login_response.json()["access_token"]
     
    movie_response = client.post("/movies", json={
            "title": "Test Movie",
            "genre": "A test movie description",
            "publisher": "Test Publisher",
            "year_published": "2024"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
     # Assert it was created successfully
    assert movie_response.status_code == 201
    movie_id = movie_response.json()['id']

    response = client.get(f'/comments/{movie_id}/comments')
    
    assert response.status_code == 200
    assert len(response.json()) >= 0 
    
    
# delete comment
def test_delete_comments(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
        })
    token = login_response.json()["access_token"]
    
    comment_id = 1
    
    response = client.delete(f"/comments/{comment_id}", headers={"Authorization": f"Bearer {token}" })
    
    assert response.status_code == 200
    assert response.json()['message'] == 'comment deleted successfuly'

# test to delete reply
def test_delete_reply(setup_db):
    login_response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
        })
    token = login_response.json()["access_token"]
    
    reply_id = 1
    
    response = client.delete(f"/comments/replies/{reply_id}", headers={"Authorization": f"Bearer {token}" })
    
    assert response.status_code == 200
    assert response.json()['message'] == 'reply deleted successfuly'

