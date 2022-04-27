from typing import List
from fastapi import APIRouter, Depends

from .. import schemas, crud, models
from ..auth import *
from ..utility import *
from . import users

router = APIRouter(tags=["tags"])

# /!\ Tag endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Tag objects

# get the list of Tag objects owned by the current user

@router.get("/api/tags/", response_model=List[schemas.Tag])
def get_all_tags(current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    return crud.get_all_tags(db, current_user)


# get info about a specific Tag object (using its name)

@router.get("/api/tags/{name}", response_model=schemas.Tag)
def get_tag_using_name(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the tag exists before returning it
    db_tag = crud.get_tag_by_name(db, name, current_user)
    if not db_tag:
        raise_http_404(f"Tag '{name}' does not exist.")
    return db_tag

# add a new 'Tag' object to the database

@router.post("/api/tags/", response_model=schemas.Tag)
def post_tag(tag: schemas.TagCreate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure an object with the same name doesn't already exist in the DB
    if crud.get_tag_by_name(db, tag.name, current_user) is not None:
        raise_http_409(f"Tag '{tag.name}' already exists.'")
    return crud.create_tag(db, tag, current_user)

# make changes to a Tag object

@router.put("/api/tags/{name}", response_model=schemas.Tag)
def put_tag(name: str, tag: schemas.TagUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_tag = crud.get_tag_by_name(db, name, current_user)
    if not db_tag:
        raise_http_404(f"Tag '{name}' does not exist.")
    # if the name is also changing, 
    # make sure there isn't already a tag using that same name
    if crud.get_tag_by_name(db, tag.new_name, current_user) is not None:
        raise_http_409(f"Tag '{tag.new_name}' already exists.")
    return crud.update_tag(db, name, tag, current_user)



# delete Tag objects

@router.delete("/api/tags/{name}", response_model=schemas.Tag)
def delete_tag(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_tag = crud.get_tag_by_name(db, name, current_user)
    if not db_tag:
        raise_http_404(f"Tag '{name}' does not exist.")
    return crud.delete_tag_from_db(db, name, current_user)
