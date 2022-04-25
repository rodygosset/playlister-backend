from typing import List
from fastapi import APIRouter, Depends

from ..schema_classes.user import UserUpdate
from .. import schemas, crud
from ..auth import *
from ..utility import *
from .data_validation.users_data_check import *

router = APIRouter(tags=["users"])



# return the current user's info (token provided)

@router.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# used to register
# this function :
# -- checks whether a user with the same username or email exists
# -- if not, creates the user in the database
# -- returns the newly created user
# -- lets the frontend handle the login with another API call

@router.post("/api/users/", response_model=schemas.User)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # first, check that the data is correct
    register_new_user_data_check(user, db)
    # if it is, create the user in the database and return it
    user.hashed_password = get_password_hash(user.hashed_password)
    return crud.create_user(db=db, user=user)


# return a list of all the users
# only for development purposes,
# there's no need for it to be in production


@router.get("/api/users/", response_model=List[schemas.User])
def read_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(read_users_me)):
    # # only proceed if the user is an admin
    # raise_exception_if_not_admin(db, current_user)
    # print("Hello from router :-D")
    return crud.get_all_users(db)


# update personal info
# any logged in user is allowed to do that

@router.put("/api/users/me", response_model=schemas.User)
def put_user_me(user: schemas.UserUpdate, current_user: schemas.User = Depends(read_users_me), db: Session = Depends(get_db)):
    # make sure the data is valid
    put_user_me_data_check(user, current_user, db)
    user_update = UserUpdate(**user.dict(), username=current_user.username)
    return crud.update_user(db, current_user.username, current_user.username, user_update)

# delete a user from the database
# admin-only operation

@router.delete("/api/users/me", response_model=schemas.User)
def delete_user(current_user: schemas.User = Depends(read_users_me), db: Session = Depends(get_db)):
    return crud.delete_user_from_db(db, current_user.username)

