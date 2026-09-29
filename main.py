from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import bcrypt

from database import engine
from schemas import UserRegister, UserLogin
from JWT_handler import create_access_token, verify_access_token


app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# JWT SECURITY
# =========================

security = HTTPBearer()


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "Auth Backend is running"
    }


# =========================
# REGISTER
# =========================

@app.post("/register")
def register(user: UserRegister):

    with engine.connect() as connection:

        # Check if email already exists
        result = connection.execute(
            text("""
                SELECT id
                FROM Users
                WHERE email = :email
            """),
            {
                "email": user.email
            }
        )

        existing_user = result.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Insert user
        connection.execute(
            text("""
                INSERT INTO Users (name, email, password)
                VALUES (:name, :email, :password)
            """),
            {
                "name": user.name,
                "email": user.email,
                "password": hashed_password
            }
        )

        connection.commit()

    return {
        "message": "User registered successfully"
    }


# =========================
# LOGIN
# =========================

@app.post("/login")
def login(user: UserLogin):

    with engine.connect() as connection:

        # Find user
        result = connection.execute(
            text("""
                SELECT id, name, email, password
                FROM Users
                WHERE email = :email
            """),
            {
                "email": user.email
            }
        )

        db_user = result.fetchone()

        # User not found
        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Check password
        password_correct = bcrypt.checkpw(
            user.password.encode("utf-8"),
            db_user.password.encode("utf-8")
        )

        if not password_correct:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Create JWT Access Token
        access_token = create_access_token(
            user_id=db_user.id,
            email=db_user.email
        )

    # Return token to frontend
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# PROFILE - PROTECTED
# =========================

@app.get("/profile")
def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Get token
    token = credentials.credentials

    # Verify token
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Get user ID from token
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Get user from database
    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT id, name, email
                FROM Users
                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        )

        db_user = result.fetchone()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }