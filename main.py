import os

from _dlib_pybind11.image_dataset_metadata import images
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from httpx import delete
from sqlalchemy.orm import Session
from app.models import User  # Assuming you have a User model defined somewhere
from app.scheme import CreateUser  # Assuming you have a schema for user creation

import os.path
import shutil
from datetime import datetime
from typing import Annotated
from fastapi import status
from fastapi.exceptions import HTTPException
from app.database import engine, get_db
from app import models
# from starlette import status, schemas
from pydantic import BaseModel, Field
from app import scheme
import requests


models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI(
    title='OpenCV API',
    version='0.0.1',
)

path = '/home/tolqinjon/PycharmProjects/OpenCV/Attendance.csv'
with open(path, 'r+') as file:
    users = file.readlines()
    access_list = []
    for user in users:
        access_list.append(user.split('\n')[0])


@app.get('/login_time_info')
def access():
    return access_list


@app.get('/')
async def all_users(db: db_dependency):
    users = db.query(User).all()
    return users


@app.get('/user/{user_id}')
async def detail(db: db_dependency, user_id: int):
    current_user = db.query(User).filter(User.id == user_id).first()
    if current_user is not None:
        return current_user
    raise HTTPException(status_code=404, detail='User not found')


@app.post('/create-user/')
async def create_user(
        db: db_dependency,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        role: str = 'user',
        image: UploadFile = File(None)
):
    try:
        photo_path = os.path.join("images", image.filename)
        with open(photo_path, 'wb') as f:
            f.write(image.file.read())

        new_user = User(
            username=username,
            last_name=last_name,
            first_name=first_name,
            email=email,
            role=role,
            image=photo_path
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        data = {
            'id': User.id,
            'username': User.username,
            'last_name': User.last_name,
            'first_name': User.first_name,
            'email': User.email,
            'role': User.role,
            'image': User.image,
            'created_at': User.created_at
        }

        return data
    except Exception as e:
        raise HTTPException(status_code=200, detail=str(e))


@app.put('/edit-user/{user_id}', response_model=None)
async def edit_user(
    user_id: int,
    user: CreateUser = Depends(),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user_model = db.query(User).filter(User.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail=f'User with id {user_id} not found')

    # Update the user model with the new data
    for key, value in user.dict().items():
        setattr(user_model, key, value)

    if image:
        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)
        photo_path = os.path.join(images_dir, image.filename)
        with open(photo_path, 'wb') as f:
            f.write(image.file.read())
        user_model.image = photo_path

    db.commit()
    db.refresh(user_model)  # Refresh the instance to get the updated data

    return {
        "message": "User edited successfully",
        "user": user_model
    }


@app.delete('/delete-user/{id}')
def delete_user(db: db_dependency, user_id: int):
    current_user = db.query(User).filter(User.id == user_id).first()

    if current_user is None:
        raise HTTPException(status_code=404, detail="Bunday malumot mavjud emas!")
    else:
        # foydalanuvchi rasm malumotini fayldan o`chirib tashlash
        # image_path = current_user.image
        # if image_path and os.path.exists(image_path):
        #     os.remove(image_path)
        #     print(f"Image {image_path} deleted.")

        # foydalanuvchi o`chirilgandan so`ng rasm malumoti boshqa faylga saqlanadi
        source_path = current_user.image
        destination_path = 'deleted_images/'

        if os.path.exists(source_path):
            try:
                # Move the file
                shutil.move(source_path, destination_path)
                print(f"Image has been moved to {destination_path}.")
            except Exception as e:
                print(f"An error occurred while moving the file: {e}")
        else:
            print(f"The file {source_path} does not exist.")

        db.delete(current_user)
        db.commit()

    return 'User deleted'
