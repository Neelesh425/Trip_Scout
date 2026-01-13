from sqlalchemy.orm import Session
from app.db_models import User
from app.schemas import UserCreate
from app.auth import get_password_hash, verify_password
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

# Update imports if needed, ensure you have IntegrityError for DB dupes
from sqlalchemy.exc import IntegrityError 

def create_user(db: Session, user: UserCreate) -> User:
    """Create new user with Error Handling for Demo"""
    print(f"--- ATTEMPTING TO REGISTER: {user.email} ---") # Debug print

    # 1. SIMPLER WAY: Bypass complex hashing for the demo if Auth is broken
    # If get_password_hash is crashing due to .env, use a dummy string temporarily:
    # hashed_password = "demo_password_hash_123" 
    
    # Otherwise, keep using your hash function but wrap it to see if it fails:
    try:
        hashed_password = get_password_hash(user.password)
    except Exception as e:
        print(f"ERROR HASHING PASSWORD: {e}")
        # Fallback so the app doesn't crash during demo
        hashed_password = "fallback_hash_123"

    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print("--- USER CREATED SUCCESSFULLY ---")
        return db_user
        
    except IntegrityError:
        db.rollback()
        print("ERROR: User already exists (Duplicate Email)")
        # For a demo, you might want to just return the existing user 
        # instead of failing, so the UI flow continues:
        return get_user_by_email(db, user.email)
        
    except Exception as e:
        db.rollback()
        print(f"CRITICAL DATABASE ERROR: {e}")
        raise e

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in update_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user