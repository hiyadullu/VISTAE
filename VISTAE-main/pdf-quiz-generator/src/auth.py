from db.database import SessionLocal
from db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def register_user(name, email, password, role="student"):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return False, "Email already registered"
        hashed_password = get_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        return True, "User registered successfully"
    finally:
        db.close()

def authenticate_user(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        if not verify_password(password, user.password_hash):
            return False, "Incorrect password"
        return True, user
    finally:
        db.close()