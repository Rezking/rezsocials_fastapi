from fastapi import FastAPI
from . import models
from .database import engine 
from .routers import post, user, auth, vote

app = FastAPI()

models.Base.metadata.create_all(bind = engine)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Welcome to my post app"}