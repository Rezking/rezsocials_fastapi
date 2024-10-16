from fastapi import Response, status, HTTPException, Depends, APIRouter
from fastapi.params import Body
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/posts",
    tags = ["Posts"]
)

@router.get("/", response_model = List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search : Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.get("/private", response_model = List[schemas.PostResponse])
def get_private_posts(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).filter(models.Post.owner_id == user_id.id).all()
    return posts

@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)): 
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    new_post = models.Post( owner_id = user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model = schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} was not found")
    if post.owner_id != user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    return post

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} does not exist")
    if post.first().owner_id != user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)):
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    if updated_post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} does not exist")
    if updated_post.first().owner_id != user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_post.update(post.dict(), synchronize_session=False)
    db.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id).first()
    return updated_post