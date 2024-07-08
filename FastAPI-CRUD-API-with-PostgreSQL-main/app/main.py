from typing import Optional
from fastapi import FastAPI , Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from . import  schemas
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)



app = FastAPI()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#venv\Scripts\activate.bat } Used to enter our virtual environment
#uvicorn app.main:app --reload } Used to reload the server


#Schema for post or to update post this schema will be used


#Establishing connection to database by using psycopg2    
while True:
    try:
        conn=psycopg2.connect(host='localhost', database='Fastapi', user='postgres', password='tesla369', cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database connection established")
        break
    except Exception as error:
        print("Failed to connect to database")
        print("Error: ",error)
        time.sleep(2)

#Hard coded post
my_posts = [{"title":"title of post1","content":"content of post1", "id":1}, {"title":"title of post2","content":"content of post2", "id":2}]

#Function to find post by id
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
           return i

        

#Getting root/home page

@app.get("/")
async def root():
    return {"message": "Welcome to the FastApi"}


#Getting all the posts

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts=db.query(models.Post).all()
    #cursor.execute("""SELECT * FROM posts""")
    #posts=cursor.fetchall()
    return posts

#Creating a post

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
   #cursor.execute("""INSERT INTO posts(title, content, published) VALUES(%s, %s, %s) RETURNING* """, (post.title, post.content, post.published))
   #This approach keeps us secure from SQL injection attack
   #new_post=cursor.fetchone()
   #conn.commit() #using it yo finalize the changes in database
   new_post=models.Post(#title=post.title, content= post.content, published=post.published
       **post.dict()    #unpacking the dictionary- it also do the same thhing but we don't need to hardcode everytime we add a column
       )

   db.add(new_post)
   db.commit()
   db.refresh(new_post)
   return{"data": new_post}



#Getting a post by id

@app.get("/posts/{id}")
def get_post(id: int, response: Response,  db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id= %s""", (str(id)))
    #post=cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post not found with id: {id}")
    return post



@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):
    #cursor.execute("""DELETE FROM posts WHERE id= %s returning *""", (str(id)))
    #deleted_post=cursor.fetchone()
    #conn.commit()
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id: {id}")
    

    post.delete(synchronize_session=False)
    db.commit()
    #Here we don't need to return any data or message as we are deleting , that's why returning status itself
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int, updated_post:schemas.PostCreate,  db: Session = Depends(get_db) ):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id=%s RETURNING *""", (post.title, post.content, post.published, str(id)))
    #updated_post=cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id: {id}")
    
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
