from jose import JWTError
import jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "f12a98d0996773731f2d22985f92ba1748e42e92872dde0da4fa609440f00fa6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id = user_id)
    except JWTError:
        raise credentials_exception
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"} )
    token = verify_token(token, credentials_exception )
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user