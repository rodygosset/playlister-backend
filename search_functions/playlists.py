from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from ..crud_functions.utils import unpack_full_song_title

from .. import models, schemas, crud

# search Playlist objects

def search_playlists(db: Session, search_params: schemas.PlaylistSearchParams, current_user: schemas.User, skip: Optional[int] = None, max: Optional[int] = None) -> List[models.Playlist]:
    """
    Retrieve from the database a List of Playlist objects matching the provided parameters.

    Args:
        db (Session): The session used to access the database.
        search_params (schemas.PlaylistSearchParams): The list of search parameters.
        current_user (schemas.User): The user who's music library we're working in.
        skip (Optional[int]): If provided, represents the number of search results to skip.
        max (Optional[int]): if provided, represents the maximum number of search results to return.
    
    Returns:
        List[models.Playlist]: The list of Playlist objects matching the parameters.
    """
    playlists = db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id)
    if search_params.name is not None:
        # this filter is a bit long to write
        # because we're doing case-insensitive search
        # ==> we convert both the column & the search parameters to lowercase
        playlists = playlists.filter(
            func.lower(models.Playlist.name)
            .contains(search_params.name.lower())
        )
    
    if search_params.tags is not None:
        for tag in search_params.tags:
            db_tag = crud.get_tag_by_name(db, tag, current_user)
            if db_tag is None:
                return [] # empty search results if the tag doesn't exist
            # get a list of the Playlist objects associated to the current TagPlaylist object
            tag_playlist_items = db.query(models.TagPlaylist).filter(models.TagPlaylist.tag_id == db_tag.id).all()
            # get the IDs of each Playlist object that appears in this list
            playlists_ids = [tag_playlist_item.playlist_id for tag_playlist_item in tag_playlist_items]
            playlists = playlists.filter(models.Playlist.id.in_(playlists_ids))

    if search_params.songs is not None:
        for song in search_params.songs:
            artist_name, song_title = unpack_full_song_title(song)
            db_song = crud.get_song_by_title(db, artist_name, song_title, current_user)
            if db_song is None:
                return [] # empty search results if the song doesn't exist
            # get a list of the Playlist objects associated to the current SongPlaylist object
            song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.song_id == db_song.id).all()
            # get the IDs of each Playlist object that appears in this list
            playlists_ids = [song_playlist_item.playlist_id for song_playlist_item in song_playlist_items]
            playlists = playlists.filter(models.Playlist.id.in_(playlists_ids))
    
    if skip is not None:
        playlists = playlists.offset(skip)
    if max is not None:
        playlists = playlists.limit(max)
    
    return playlists.all()