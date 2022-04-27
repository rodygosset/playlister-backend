from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from .. import models, schemas, crud

# search Playlist objects

def search_playlists(db: Session, search_params: schemas.PlaylistSearchParams, skip: Optional[int] = None, max: Optional[int] = None) -> List[models.Playlist]:
    """
    Retrieve from the database a List of Playlist objects matching the provided parameters.

    Args:
        db (Session): The session used to access the database.
        search_params (schemas.PlaylistSearchParams): The list of search parameters.
        skip (Optional[int]): If provided, represents the number of search results to skip.
        max (Optional[int]): if provided, represents the maximum number of search results to return.
    
    Returns:
        List[models.Playlist]: The list of Playlist objects matching the parameters.
    """
    playlists = db.query(models.Playlist)
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
            db_tag = crud.get_tag_by_name(db, tag)
            if db_tag is None:
                return [] # empty search results if the tag doesn't exist
            # get a list of the Playlist objects associated to the current TagPlaylist object
            tag_playlist_items = db.query(models.TagPlaylist).filter(models.TagPlaylist.tag_id == db_tag.id).all()
            # get the IDs of each Playlist object that appears in this list
            tag_playlists_ids = [tag_playlist_item.playlist_id for tag_playlist_item in tag_playlist_items]
            playlists = playlists.filter(models.Playlist.id.in_(tag_playlists_ids))
    
    if search_params.songs is not None:
        for song in search_params.songs:
            db_song = crud.get_song_by_name(db, song)
            if db_song is None:
                return [] # empty search results if the song doesn't exist
            # get a list of the Playlist objects associated to the current SongPlaylist object
            song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.song_id == db_song.id).all()
            # get the IDs of each Playlist object that appears in this list
            song_playlists_ids = [song_playlist_item.playlist_id for song_playlist_item in song_playlist_items]
            playlists = playlists.filter(models.Playlist.id.in_(song_playlists_ids))
    
    if skip is not None:
        playlists = playlists.offset(skip)
    if max is not None:
        playlists = playlists.limit(max)
    
    return playlists.all()