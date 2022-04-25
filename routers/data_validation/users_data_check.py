from ... import schemas, crud
from ...auth import *
from ...utility import *

# /!\ This file contains the functions used to validate the data recieved by the 'users' endpoints. /!\ 

# checks whether the data recieved by register_new_user() is correct

def register_new_user_data_check(user: schemas.UserCreate, db: Session):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise_http_400("This username is already taken.")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise_http_400("This email address is already in use.")

# checks whether the data recieved by put_user_me() is correct

def put_user_me_data_check(user: schemas.UserUpdate, current_user: schemas.User, db: Session):
    # here, no need to check if the provided 'user' exists, because it corresponds to the current_user
    if user.new_username is not None:
        # if the username is also changing, 
        # make sure there isn't already a user with that username
        if get_user_by_username(db, user.new_username) is not None:
            raise_http_409(f"The username '{user.new_username}' is already taken.")
