from typing import List
from fastapi import APIRouter, Depends

from ..search_functions.utils import search_check_boundaries

from .. import schemas, crud, search
from ..auth import *
from ..utility import *
from . import users
from .data_validation.songs_data_check import *


router = APIRouter(tags=["songs"])

# /!\ Song endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Song objects

# get the list of Song objects owned by the current user

@router.get("/api/songs/", response_model=List[schemas.Song])
def get_req_songs(max: Optional[int] = None, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    db_songs = None
    if max is not None:
        if max < 0:
            raise_http_400(f"Cannot process request : max value cannot be negative (max={max}).")
        db_songs = crud.get_songs_from_db(db, max, current_user)
    else :
        db_songs = crud.get_all_songs(db, current_user)
    # for each 'Song' object, add the associated Tag, Genre and Artist objects to it
    songs = [{**db_song.__dict__, "tags": crud.get_song_tags(db, db_song), "genres": crud.get_song_genres(db, db_song), "artists": crud.get_song_artists(db, db_song)} for db_song in db_songs]
    return songs

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
    # make sure the song is associated to at least one artist
    if len(song.artists) == 0:
        raise_http_400(f"Cannot add new song '{song.title}' to the library: no artist specified.")
    # make sure an object with the same name doesn't already exist in the DB
    for artist in song.artists:
        if crud.get_song_by_title(db, artist, song.title, current_user) is not None:
            raise_http_409(f"Song '{song.title} by {artist}' already exists.'")
    db_song = crud.create_song(db, song, current_user)
    # get the list of tags associated to this song object
    tags = crud.get_song_tags(db, db_song)
    # get the list of genres associated to this song object
    genres = crud.get_song_genres(db, db_song)
    # get the list of artists associated to this song object
    artists = crud.get_song_artists(db, db_song)
    song = { **db_song.__dict__, "tags": tags, "genres": genres, "artists": artists }
    return song



# search Song objects matching the parameters in the provided schemas.SongSearchParams object

@router.post("/api/songs/search/", response_model=List[schemas.Song])
def search_songs(
    search_params: schemas.SongSearchParams, 
    skip: Optional[int] = None, 
    max: Optional[int] = None, 
    current_user: schemas.User = Depends(users.read_users_me), 
    db: Session = Depends(get_db)
):
    search_check_boundaries(skip, max)
    db_songs = search.search_songs(db, search_params, current_user, skip, max)
    songs = [{**db_song.__dict__, "tags": crud.get_song_tags(db, db_song), "genres": crud.get_song_genres(db, db_song), "artists": crud.get_song_artists(db, db_song)} for db_song in db_songs]
    return songs

# get the number of Song objects matching the parameters in the provided schemas.SongSearchParams object

@router.post("/api/songs/search/nb")
def search_songs_nb(search_params: schemas.SongSearchParams, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    db_songs = search.search_songs(db, search_params, current_user)
    return {"nb_results": len(db_songs)}


# make changes to a Song object's data

@router.put("/api/artists/{artist_name}/{song_title}", response_model=schemas.Song)
def put_song(artist_name: str, song_title: str, song: schemas.SongUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # perform data validation before trying to apply the changes to the Song object
    put_song_data_check(artist_name, song_title, song, current_user, db)
    db_song = crud.update_song(db, artist_name, song_title, song, current_user)
    # get the list of tags associated to this song object
    tags = crud.get_song_tags(db, db_song)
    # get the list of genres associated to this song object
    genres = crud.get_song_genres(db, db_song)
    # get the list of artists associated to this song object
    artists = crud.get_song_artists(db, db_song)
    song = { **db_song.__dict__, "tags": tags, "genres": genres, "artists": artists }
    return song



# delete Song objects

@router.delete("/api/artists/{artist_name}/{song_title}", response_model=schemas.Song)
def delete_song(artist_name: str, song_title: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
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
    crud.delete_song(db, artist_name, song_title, current_user)
    return song

