import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
import os

SQLALCHEMY_DATABASE_URL = os.environ.get('TEST_DB_URL', "sqlite:///./test.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

def test_signup(setup_db):
    response = client.post("/signup", json={
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

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

    response = client.post("/movies/", json={
        "title": "Test Movie",
        "description": "A test movie description",
        "publisher": "Test Publisher"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    print(response.json())  # Debugging line to print the error response
    assert response.status_code == 201
    assert response.json()["title"] == "Test Movie"

def test_get_movies(setup_db):
    response = client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()) > 0
