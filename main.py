from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from fastapi.middleware.cors import CORSMiddleware

# --- Initialisation de FastAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Changez "*" par l'URL de Streamlit si nécessaire
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration de base ---
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "sqlite:///./test.db"

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modèles ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    name = Column(String)
    calories = Column(Float)
    proteins = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)

Base.metadata.create_all(bind=engine)

# --- Sécurité (JWT et mots de passe) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Dépendances ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modèles Pydantic ---
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class MealRequest(BaseModel):
    name: str
    calories: float
    proteins: float
    carbs: float
    fats: float

# --- Endpoints ---
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        logger.warning("Email already registered: %s", request.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    try:
        hashed_password = get_password_hash(request.password)
        new_user = User(email=request.email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("User registered successfully: %s", request.email)
        return {"message": "User registered successfully"}
    except IntegrityError:
        db.rollback()
        logger.error("Database integrity error during registration for email: %s", request.email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning("Invalid login attempt for email: %s", request.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    logger.info("User logged in successfully: %s", request.email)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/meals")
def add_meal(request: MealRequest, db: Session = Depends(get_db)):
    try:
        meal = Meal(name=request.name, calories=request.calories, proteins=request.proteins, carbs=request.carbs, fats=request.fats, user_id=1)  # Test user
        db.add(meal)
        db.commit()
        logger.info("Meal added successfully: %s", request.name)
        return {"message": "Meal added successfully"}
    except Exception as e:
        db.rollback()
        logger.error("Error adding meal: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@app.get("/recommendation")
def get_recommendation():
    logger.info("Recommendation requested")
    return {"meal": "Poulet et riz", "calories": 600, "proteins": 40, "carbs": 50, "fats": 10}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/meals")
def get_meals(db: Session = Depends(get_db)):
    meals = db.query(Meal).all()
    return meals
