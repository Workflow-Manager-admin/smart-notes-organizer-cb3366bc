from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from src.api import models, auth
from src.api.database import get_db, User as DBUser
from src.api.auth import get_password_hash, authenticate_user, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(tags=["Authentication"])

# PUBLIC_INTERFACE
@router.post("/", response_model=models.User, summary="Register new user")
def register_user(user: models.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user with email and password.
    """
    db_user = db.query(DBUser).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    hashed_pw = get_password_hash(user.password)
    new_user = DBUser(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# PUBLIC_INTERFACE
@auth_router.post("/token", response_model=models.Token, summary="User login / token request")
def login_for_access_token(form_data: models.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and get JWT token.
    """
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@router.get("/me", response_model=models.User, summary="Get current user")
def read_users_me(current_user: DBUser = Depends(auth.get_current_user)):
    """
    Returns data for the currently authenticated user.
    """
    return current_user
