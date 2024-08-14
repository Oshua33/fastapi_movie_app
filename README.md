# Movie and Comment Management API

This is a FastAPI-based application for managing movies, their ratings, comments, and replies. The API allows users to perform CRUD operations on movies, rate movies, comment on movies, and reply to comments.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication and authorization
- CRUD operations for movies
- Rate movies
- Comment on movies
- Reply to comments

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/oshua33/capstone_project.git
   cd capstone_project
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   # Example for SQLite, ensure the database URL in your settings is correct
   alembic upgrade head
   ```

## Usage

1. **Run the application**:

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation**:
   Open your web browser and navigate to `http://127.0.0.1:8000/docs` to view the interactive API documentation provided by Swagger UI.

## API Endpoints

### Users

- **Sign Up**:

  ```http
  POST /signup
  ```

  **Request Body**:

  ```json
  {
    "username": "string",
    "full_name": "string",
    "email": "string",
    "password": "string"
  }
  ```

- **Login**:
  ```http
  POST /login
  ```
  **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

### Movies

- **Get Movies**:

  ```http
  GET /movies
  ```

- **Get Movie by ID**:

  ```http
  GET /movies/{movie_id}
  ```

- **Create Movie**:

  ```http
  POST /movies
  ```

  **Request Body**:

  ```json
  {
    "title": "string",
    "genre": "string",
    "publisher": "string",
    "year_published": "int"
  }
  ```

- **Update Movie**:

  ```http
  PUT /movies/{movie_id}
  ```

  **Request Body**:

  ```json
  {
    "title": "string",
    "genre": "string",
    "publisher": "string",
    "year_published": "int"
  }
  ```

- **Delete Movie**:
  ```http
  DELETE /movies/{movie_id}
  ```

### Ratings

- **Create Rating**:

  ```http
  POST /ratings/{movie_id}
  ```

  **Request Body**:

  ```json
  {
    "rating": "float"
  }
  ```

- **Get Rating by Movie ID**:
  ```http
  GET /ratings/{movie_id}
  ```

### Comments

- **Create Comment**:

  ```http
  POST /comments
  ```

  **Request Body**:

  ```json
  {
    "comment": "string",
    "movie_id": "int"
  }
  ```

- **Get Comments and Replies by Movie ID**:
  ```http
  GET /comments/{movie_id}/replies
  ```

### Replies

- **Create Reply**:
  ```http
  POST /comments/{comment_id}/replies
  ```
  **Request Body**:
  ```json
  {
    "reply": "string"
  }
  ```

## Project Structure

capstone_project/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── models.py
│ ├── schemas.py
│ ├── crud.py
│ ├── auth.py
│ ├── dependencies.py
│ └── database.py
├── alembic/
│ ├── versions/
│ └── env.py
├── tests/
│ ├── init.py
│ ├── test_comments.py
│ └── test_replies.py
├── venv/
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md

## Contributing

1. **Fork the repository**
2. **Create a new branch** (`git checkout -b feature/your-feature`)
3. **Commit your changes** (`git commit -m 'Add some feature'`)
4. **Push to the branch** (`git push origin feature/your-feature`)
5. **Create a new Pull Request**

## License

<!-- This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. -->
