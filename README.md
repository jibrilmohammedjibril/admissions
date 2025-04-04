# School Admission System Backend

A FastAPI-based backend system for managing school admissions with user authentication and file upload capabilities.

## Features

- User registration and authentication with JWT tokens
- Secure file upload for application documents
- UUID-based application tracking
- Role-based access control (Admin/Applicant)
- PostgreSQL database integration

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a PostgreSQL database named `admissions_db`
5. Update the `.env` file with your database credentials and secret key
6. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /signup`: Register a new user
- `POST /token`: Login and get JWT token

### Applications
- `POST /application/upload`: Upload or update an application
- `GET /application/{uuid}`: Get application details

## Environment Variables

Create a `.env` file with the following variables:
```
DATABASE_URL=postgresql://username:password@localhost:5432/admissions_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Security

- All endpoints except `/signup` and `/token` require JWT authentication
- Passwords are hashed using bcrypt
- File uploads are stored in a separate directory with UUID-based organization
- Role-based access control for application viewing

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 