from typing import List
from fastapi import APIRouter, Depends

import models
from .. import schemas, crud
from ..auth import *
from ..utility import *
from . import users

router = APIRouter(tags=["artists"])

# /!\ Artist endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Artist objects

# get the list of Artist objects owned by the current user

@router.get("/api/artists/", response_model=List[schemas.Artist])
def get_all_artists(current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    return crud.get_all_artists(db, current_user)


# get info about a specific Artist object (using its name)

@router.get("/api/artists/{name}", response_model=schemas.Artist)
def get_artist_using_name(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the artist exists before returning it
    db_artist = crud.get_artist_by_name(db, name, current_user)
    if not db_artist:
        raise_http_404(f"Artist '{name}' does not exist.")
    # get the list of songs associated to this artist object
    song_ids = [song_artist.song_id for song_artist in crud.get_artist_artist_song_objects(db, db_artist)]
    songs = [song.name for song in db.query(models.Song).filter(models.Song.id.in_(song_ids)).all()]
    # get the list of playlists associated to this artist object
    playlist_ids = [playlist_artist.playlist_id for playlist_artist in crud.get_artist_artist_playlist_objects(db, db_artist)]
    playlists = [playlist.name for playlist in db.query(models.Playlist).filter(models.Playlist.id.in_(playlist_ids)).all()]
    artist = { **db_artist.__dict__, "songs": songs, "playlists": playlists }
    return artist

# add a new 'Artist' object to the database

@router.post("/api/artists/", response_model=schemas.Artist)
def post_artist(artist: schemas.ArtistCreate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure an object with the same name doesn't already exist in the DB
    if crud.get_artist_by_name(db, artist.name, current_user) is not None:
        raise_http_409(f"Artist '{artist.name}' already exists.'")
    return crud.create_artist(db, artist)

# make changes to a Artist object

@router.put("/api/artists/{name}", response_model=schemas.Artist)
def put_artist(name: str, artist: schemas.ArtistUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_artist = crud.get_artist_by_name(db, name, current_user)
    if not db_artist:
        raise_http_404(f"Artist '{name}' does not exist.")
    # if the name is also changing, 
    # make sure there isn't already a artist using that same name
    if crud.get_artist_by_name(db, artist.new_name, current_user) is not None:
        raise_http_409(f"Artist '{artist.new_name}' already exists.")
    return crud.update_artist(db, name, artist)



# delete Artist objects

@router.delete("/api/artists/{name}", response_model=schemas.Artist)
def delete_artist(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_artist = crud.get_artist_by_name(db, name)
    if not db_artist:
        raise_http_404(f"Artist '{name}' does not exist.")
    return crud.delete_artist_from_db(db, name, current_user)
