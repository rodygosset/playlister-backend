from typing import List
from fastapi import APIRouter, Depends

import models
from .. import schemas, crud
from ..auth import *
from ..utility import *
from . import users

router = APIRouter(tags=["songs"])

# /!\ Song endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Song objects

# get the list of Song objects owned by the current user

@router.get("/api/songs/", response_model=List[schemas.Song])
def get_all_songs(current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    return crud.get_all_songs(db, current_user)


# get info about a specific Song object (using its name)

@router.get("/api/artists/{artist_name}/{song_title}", response_model=schemas.Song)
def get_song_using_name(artist_name: str, song_title: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the song exists before returning it
    db_song = crud.get_song_by_title(db, artist_name, song_title, current_user)
    if not db_song:
        raise_http_404(f"Song '{song_title} by {artist_name}' does not exist.")
    # get the list of tags associated to this song object
    tags = crud.get_song_tags(db, db_song)
    # get the list of genres associated to this song object
    genres = crud.get_song_genres(db, db_song)
    # get the list of artists associated to this song object
    artists = crud.get_song_artists(db, db_song)
    song = { **db_song.__dict__, "tags": tags, "genres": genres, "artists": artists }
    return song

# add a new 'Song' object to the database

@router.post("/api/songs/", response_model=schemas.Song)
def post_song(song: schemas.SongCreate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure an object with the same name doesn't already exist in the DB
    if crud.get_song_by_name(db, song.name, current_user) is not None:
        raise_http_409(f"Song '{song.name}' already exists.'")
    return crud.create_song(db, song)

# make changes to a Song object

@router.put("/api/songs/{name}", response_model=schemas.Song)
def put_song(name: str, song: schemas.SongUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_song = crud.get_song_by_name(db, name, current_user)
    if not db_song:
        raise_http_404(f"Song '{name}' does not exist.")
    # if the name is also changing, 
    # make sure there isn't already a song using that same name
    if crud.get_song_by_name(db, song.new_name, current_user) is not None:
        raise_http_409(f"Song '{song.new_name}' already exists.")
    return crud.update_song(db, name, song)



# delete Song objects

@router.delete("/api/songs/{name}", response_model=schemas.Song)
def delete_song(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_song = crud.get_song_by_name(db, name)
    if not db_song:
        raise_http_404(f"Song '{name}' does not exist.")
    return crud.delete_song_from_db(db, name, current_user)
