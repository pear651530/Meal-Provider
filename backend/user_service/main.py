from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import func

from . import models, schemas, database
from .database import get_db

# Create FastAPI app
app = FastAPI(title="User Service API")

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = "mealprovider"  # Should be obtained from environment variables in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Add API key configuration
API_KEY = "mealprovider_admin_key"  # Should be obtained from environment variables in production

# Authentication related functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )
    return current_user

def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# 用戶相關路由
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role="employee"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/users/{user_id}/dining-records/", response_model=List[schemas.DiningRecord])
def get_user_dining_records(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.DiningRecord).filter(models.DiningRecord.user_id == user_id).all()

@app.post("/dining-records/{dining_record_id}/reviews/", response_model=schemas.Review)
def create_review(
    dining_record_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_dining_record = db.query(models.DiningRecord).filter(
        models.DiningRecord.id == dining_record_id,
        models.DiningRecord.user_id == current_user.id
    ).first()
    
    if not db_dining_record:
        raise HTTPException(status_code=404, detail="Dining record not found")
    
    db_review = models.Review(
        **review.dict(),
        user_id=current_user.id,
        dining_record_id=dining_record_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dining-records/{dining_record_id}", response_model=schemas.DiningRecord)
def get_dining_record(
    dining_record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_dining_record = db.query(models.DiningRecord).filter(
        models.DiningRecord.id == dining_record_id,
        models.DiningRecord.user_id == current_user.id
    ).first()
    
    if not db_dining_record:
        raise HTTPException(status_code=404, detail="Dining record not found")
    
    return db_dining_record

@app.get("/dining-records/{dining_record_id}/reviews/", response_model=schemas.Review)
def get_dining_record_review(
    dining_record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First verify the dining record belongs to the user
    db_dining_record = db.query(models.DiningRecord).filter(
        models.DiningRecord.id == dining_record_id,
        models.DiningRecord.user_id == current_user.id
    ).first()
    
    if not db_dining_record:
        raise HTTPException(status_code=404, detail="Dining record not found")
    
    # Get the review for this dining record
    db_review = db.query(models.Review).filter(
        models.Review.dining_record_id == dining_record_id,
        models.Review.user_id == current_user.id
    ).first()
    
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return db_review

@app.put("/dining-records/{dining_record_id}/reviews/", response_model=schemas.Review)
def update_review(
    dining_record_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First verify the dining record belongs to the user
    db_dining_record = db.query(models.DiningRecord).filter(
        models.DiningRecord.id == dining_record_id,
        models.DiningRecord.user_id == current_user.id
    ).first()
    
    if not db_dining_record:
        raise HTTPException(status_code=404, detail="Dining record not found")
    
    # Get the existing review
    db_review = db.query(models.Review).filter(
        models.Review.dining_record_id == dining_record_id,
        models.Review.user_id == current_user.id
    ).first()
    
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Update the review
    for key, value in review.dict().items():
        setattr(db_review, key, value)
    
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/users/unpaid", response_model=List[schemas.UnpaidUser])
def get_unpaid_users(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    # Query all users with unpaid dining records
    unpaid_records = db.query(
        models.User.id,
        models.User.username,
        models.DiningRecord.total_amount
    ).join(
        models.DiningRecord,
        models.User.id == models.DiningRecord.user_id
    ).filter(
        models.DiningRecord.payment_status == "unpaid"
    ).all()
    
    # Group by user and sum unpaid amounts
    user_unpaid = {}
    for user_id, username, amount in unpaid_records:
        if user_id not in user_unpaid:
            user_unpaid[user_id] = {
                "user_id": user_id,
                "user_name": username,
                "unpaidAmount": 0
            }
        user_unpaid[user_id]["unpaidAmount"] += amount
    
    return list(user_unpaid.values())

@app.get("/ratings/{menu_item_id}", response_model=schemas.MenuItemRating)
def get_menu_item_rating(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    # Get all dining records for this menu item
    dining_records = db.query(models.DiningRecord).filter(
        models.DiningRecord.menu_item_id == menu_item_id
    ).all()
    
    if not dining_records:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Get all reviews for these dining records
    dining_record_ids = [dr.id for dr in dining_records]
    reviews = db.query(models.Review).filter(
        models.Review.dining_record_id.in_(dining_record_ids)
    ).all()
    
    # Calculate statistics
    total_reviews = len(reviews)  # Total number of reviews
    good_reviews = sum(1 for review in reviews if review.rating == "good")
    good_ratio = good_reviews / total_reviews if total_reviews > 0 else 0
    
    return {
        "menu_item_id": menu_item_id,
        "menu_item_name": dining_records[0].menu_item_name,  # All records should have the same name
        "total_reviews": total_reviews,
        "good_reviews": good_reviews,
        "good_ratio": good_ratio
    } 