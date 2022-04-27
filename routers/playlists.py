from typing import List
from fastapi import APIRouter, Depends

from ..search_functions.utils import search_check_boundaries

from .. import schemas, crud, search
from ..auth import *
from ..utility import *
from . import users

router = APIRouter(tags=["playlists"])

# /!\ Playlist endpoints /!\

# all these endpoints require the user to be logged in
# that is so because each model in the database is uniquely identified
# by the combination of its name and its owner


# used to manage Playlist objects

# get the list of Playlist objects owned by the current user

@router.get("/api/playlists/", response_model=List[schemas.Playlist])
def get_req_playlists(max: Optional[int] = None, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    db_playlists = None
    if max is not None:
        if max < 0:
            raise_http_400(f"Cannot process request : max value cannot be negative (max={max}).")
        db_playlists = crud.get_playlists_from_db(db, max, current_user)
    else :
        db_playlists = crud.get_all_playlists(db, current_user)
    # for each 'Playlist' object, add the associated Song and Tag objects to it
    playlists = [{**db_playlist.__dict__, "tags": crud.get_playlist_tags(db, db_playlist), "songs": crud.get_playlist_songs(db, db_playlist)} for db_playlist in db_playlists]
    return playlists


# get info about a specific Playlist object (using its name)

@router.get("/api/playlists/{name}", response_model=schemas.Playlist)
def get_playlist_using_name(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the playlist exists before returning it
    db_playlist = crud.get_playlist_by_name(db, name, current_user)
    if not db_playlist:
        raise_http_404(f"Playlist '{name}' does not exist.")
    # get the list of songs associated to this Playlist object
    songs = crud.get_playlist_songs(db, db_playlist)
    # get the list of tags associated to this Playlist object
    tags = crud.get_playlist_tags(db, db_playlist)
    playlist = { **db_playlist.__dict__, "songs": songs, "tags": tags }
    return playlist

# add a new 'Playlist' object to the database

@router.post("/api/playlists/", response_model=schemas.Playlist)
def post_playlist(playlist: schemas.PlaylistCreate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure an object with the same name doesn't already exist in the DB
    if crud.get_playlist_by_name(db, playlist.name, current_user) is not None:
        raise_http_409(f"Playlist '{playlist.name}' already exists.'")
    return crud.create_playlist(db, playlist, current_user)


# search Playlist objects matching the parameters in the provided schemas.PlaylistSearchParams object

@router.post("/api/playlists/search/", response_model=List[schemas.Playlist])
def search_playlists(
    search_params: schemas.PlaylistSearchParams, 
    skip: Optional[int] = None, 
    max: Optional[int] = None, 
    current_user: schemas.User = Depends(users.read_users_me), 
    db: Session = Depends(get_db)
):
    search_check_boundaries(skip, max)
    db_playlists = search.search_playlists(db, search_params, skip, max)
    playlists = [{**db_playlist.__dict__, "tags": crud.get_playlist_tags(db, db_playlist), "songs": crud.get_playlist_songs(db, db_playlist)} for db_playlist in db_playlists]
    return playlists

# get the number of Playlist objects matching the parameters in the provided schemas.PlaylistSearchParams object

@router.post("/api/playlists/search/nb")
def search_playlists_nb(search_params: schemas.PlaylistSearchParams, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    db_playlists = search.search_playlists(db, search_params)
    return {"nb_results": len(db_playlists)}



# make changes to a Playlist object

@router.put("/api/playlists/{name}", response_model=schemas.Playlist)
def put_playlist(name: str, playlist: schemas.PlaylistUpdate, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_playlist = crud.get_playlist_by_name(db, name, current_user)
    if not db_playlist:
        raise_http_404(f"Playlist '{name}' does not exist.")
    # if the name is also changing, 
    # make sure there isn't already a playlist using that same name
    if crud.get_playlist_by_name(db, playlist.new_name, current_user) is not None:
        raise_http_409(f"Playlist '{playlist.new_name}' already exists.")
    return crud.update_playlist(db, name, playlist)



# delete Playlist objects

@router.delete("/api/playlists/{name}", response_model=schemas.Playlist)
def delete_playlist(name: str, current_user: schemas.User = Depends(users.read_users_me), db: Session = Depends(get_db)):
    # make sure the object to be modified exists
    db_playlist = crud.get_playlist_by_name(db, name)
    if not db_playlist:
        raise_http_404(f"Playlist '{name}' does not exist.")
    return crud.delete_playlist(db, name, current_user)
