from fastapi import FastAPI,HTTPException,Depends,status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session

app=FastAPI()
Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title:str
    content:str
    user_id:int
    
class PostBaseForPut(BaseModel):
    title:str
    content:str
    user_id:int
    id:int
    
class UserBase(BaseModel):
    username:str
    
class QueryBase(BaseModel):
    user_id:int
    
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    


@app.get('/posts/',status_code=status.HTTP_200_OK)
async def get_posts(db:Session=Depends(get_db)):
    db_posts=list(db.query(models.Post))
    return db_posts

@app.post('/posts/',status_code=status.HTTP_201_CREATED)
async def create_post(post:PostBase,db:Session=Depends(get_db)):
    db_post=models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    

@app.post('/users/',status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase,db:Session=Depends(get_db)):
    db_user=models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    
@app.get('/users/{user_id}',status_code=status.HTTP_200_OK)
async def read_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404,detail='User not found')
    return user

@app.get('/posts/{post_id}',status_code=status.HTTP_200_OK)
async def read_post(post_id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==post_id).first()
    if post is None:
        raise HTTPException(status_code=404,detail='User not found')
    return post

@app.delete('/posts/{post_id}',status_code=status.HTTP_200_OK)
async def delete_post(post_id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==post_id).first()
    if post:
        db.delete(post)
        db.commit()
    
@app.put('/posts/{post_id}',status_code=status.HTTP_200_OK)
async def update_post(post_id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==post_id).first()
    db._update_impl(post)
    db.commit()
    
@app.put('/posts/',status_code=status.HTTP_200_OK)
async def update_post_mine(post:PostBaseForPut,db:Session=Depends(get_db)):
    post_id=post.id
    new_post_db=PostBase(**post.model_dump())#De todos los campos de post request, agarrar los campos q estan en postbase y hacerlos un form
    
    post_db_old=db.query(models.Post).filter(models.Post.id==post_id).first()
    
    post_db_old.title=new_post_db.title
    post_db_old.content=new_post_db.content
    post_db_old.user_id=new_post_db.user_id
    db.commit()
    
    return post_db_old
    
@app.post('/query/',status_code=status.HTTP_200_OK)
async def get_query(post:QueryBase,db:Session=Depends(get_db)):
    posts_db=list(db.query(models.Post).filter(models.Post.user_id==post.user_id))
    return posts_db