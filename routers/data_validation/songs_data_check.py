
import json
from ... import schemas, crud
from ...auth import *
from ...utility import *

# /!\ This file contains the functions used to validate the data recieved by the 'songs' endpoints. /!\ 

# checks whether the data recieved by put_song() is correct


def put_song_data_check(artist_name: str, song_title: str, song: schemas.SongUpdate, current_user: schemas.User, db: Session):
    # make sure the object to be modified exists
    db_song = crud.get_song_by_title(db, artist_name, song_title, current_user)
    if not db_song:
        raise_http_404(f"Song '{song_title} by {artist_name}' does not exist.")
    # if the title is also changing, 
    # make sure there isn't already a song with that same title
    if song.new_title is not None: 
        duplicate = None
        artist = None
        if song.artists is not None and len(song.artists) != 0:
            for artist in song.artists:
                duplicate = crud.get_song_by_title(db, artist, song.new_title, current_user)
                if duplicate is not None:
                    raise_http_409(f"Song '{song.new_title} by {artist}' already exists.")
        else: 
            artists = crud.get_song_artists(db, db_song)
            for artist in artists:
                duplicate = crud.get_song_by_title(db, artist, song.new_title, current_user)
                if duplicate is not None:
                    raise_http_409(f"Song '{song.new_title} by {artist}' already exists.")