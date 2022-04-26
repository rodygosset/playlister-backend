from typing import List
from fastapi import APIRouter, Depends

import models
from .. import schemas, crud
from ..auth import *
from ..utility import *
from . import users

router = APIRouter(tags=["genres"])

# /!\ Genre endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Genre objects

# get the list of Genre objects owned by the current user

@router.get("/api/genres/", response_model=List[schemas.Genre])
def get_all_genres(current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    return crud.get_all_genres(db, current_user)


# get info about a specific Genre object (using its name)

@router.get("/api/genres/{name}", response_model=schemas.Genre)
def get_genre_using_name(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the genre exists before returning it
    db_genre = crud.get_genre_by_name(db, name, current_user)
    if not db_genre:
        raise_http_404(f"Genre '{name}' does not exist.")
    # get the list of songs associated to this genre object
    song_ids = [song_genre.song_id for song_genre in crud.get_genre_genre_song_objects(db, db_genre)]
    songs = [song.name for song in db.query(models.Song).filter(models.Song.id.in_(song_ids)).all()]
    genre = { **db_genre.__dict__, "songs": songs }
    return genre

# add a new 'Genre' object to the database

@router.post("/api/genres/", response_model=schemas.Genre)
def post_genre(genre: schemas.GenreCreate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure an object with the same name doesn't already exist in the DB
    if crud.get_genre_by_name(db, genre.name, current_user) is not None:
        raise_http_409(f"Genre '{genre.name}' already exists.'")
    return crud.create_genre(db, genre)

# make changes to a Genre object

@router.put("/api/genres/{name}", response_model=schemas.Genre)
def put_genre(name: str, genre: schemas.GenreUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_genre = crud.get_genre_by_name(db, name, current_user)
    if not db_genre:
        raise_http_404(f"Genre '{name}' does not exist.")
    # if the name is also changing, 
    # make sure there isn't already a genre using that same name
    if crud.get_genre_by_name(db, genre.new_name, current_user) is not None:
        raise_http_409(f"Genre '{genre.new_name}' already exists.")
    return crud.update_genre(db, name, genre)



# delete Genre objects

@router.delete("/api/genres/{name}", response_model=schemas.Genre)
def delete_genre(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_genre = crud.get_genre_by_name(db, name)
    if not db_genre:
        raise_http_404(f"Genre '{name}' does not exist.")
    return crud.delete_genre_from_db(db, name, current_user)
