from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/create", status_code = status.HTTP_201_CREATED, response_model = schemas.UserResponse)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:    
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already registered")   
    
@router.get("/{id}", response_model = schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"user with the id {id} was not found")
    return user    