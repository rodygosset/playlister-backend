from datetime import timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from .. import models, schemas, crud

# search Song objects

def search_songs(db: Session, search_params: schemas.SongSearchParams, current_user: schemas.User, skip: Optional[int] = None, max: Optional[int] = None) -> List[models.Song]:
    """
    Retrieve from the database a List of Song objects matching the provided parameters.

    Args:
        db (Session): The session used to access the database.
        search_params (schemas.SongSearchParams): The list of search parameters.
        current_user (schemas.User): The user who's music library we're working in.
        skip (Optional[int]): If provided, represents the number of search results to skip.
        max (Optional[int]): if provided, represents the maximum number of search results to return.
    
    Returns:
        List[models.Song]: The list of Song objects matching the parameters.
    """
    songs = db.query(models.Song).filter(models.Song.user_id == current_user.id)
    if search_params.title is not None:
        # this filter is a bit long to write
        # because we're doing case-insensitive search
        # ==> we convert both the column & the search parameters to lowercase
        songs = songs.filter(
            func.lower(models.Song.title)
            .contains(search_params.title.lower())
        )
    if search_params.key is not None:
        songs = songs.filter(
            func.lower(models.Song.key)
            .contains(search_params.key.lower())
        )
    if search_params.url is not None:
        songs = songs.filter(
            func.lower(models.Song.url)
            .contains(search_params.url.lower())
        )
    if search_params.bpm is not None:
        songs = songs.filter(models.Song.bpm == search_params.bpm)
    
    if search_params.duration_minutes is not None:
        minutes = timedelta(minutes=search_params.duration_minutes)
        minutes_plus_one = timedelta(minutes=search_params.duration_minutes + 1)
        songs = songs.filter(models.Song.duration >= minutes, models.Song.duration < minutes_plus_one)
        if search_params.duration_seconds is not None:
            seconds = timedelta(seconds=search_params.duration_seconds)
            songs = songs.filter(models.Song.duration == minutes + seconds)
    

    if search_params.tags is not None:
        for tag in search_params.tags:
            db_tag = crud.get_tag_by_name(db, tag, current_user)
            if db_tag is None:
                return [] # empty search results if the tag doesn't exist
            # get a list of the Song objects associated to the current TagSong object
            tag_song_items = db.query(models.TagSong).filter(models.TagSong.tag_id == db_tag.id).all()
            # get the IDs of each Song object that appears in this list
            tag_songs_ids = [tag_song_item.song_id for tag_song_item in tag_song_items]
            songs = songs.filter(models.Song.id.in_(tag_songs_ids))
    
    if search_params.genres is not None:
        for genre in search_params.genres:
            db_genre = crud.get_genre_by_name(db, genre, current_user)
            if db_genre is None:
                return [] # empty search results if the genre doesn't exist
            # get a list of the Song objects associated to the current GenreSong object
            genre_song_items = db.query(models.GenreSong).filter(models.GenreSong.genre_id == db_genre.id).all()
            # get the IDs of each Song object that appears in this list
            genre_songs_ids = [genre_song_item.song_id for genre_song_item in genre_song_items]
            songs = songs.filter(models.Song.id.in_(genre_songs_ids))
    
    if search_params.artists is not None:
        for artist in search_params.artists:
            db_artist = crud.get_artist_by_name(db, artist, current_user)
            if db_artist is None:
                return [] # empty search results if the artist doesn't exist
            # get a list of the Song objects associated to the current ArtistSong object
            artist_song_items = db.query(models.ArtistSong).filter(models.ArtistSong.artist_id == db_artist.id).all()
            # get the IDs of each Song object that appears in this list
            artist_songs_ids = [artist_song_item.song_id for artist_song_item in artist_song_items]
            songs = songs.filter(models.Song.id.in_(artist_songs_ids))
    


    if search_params.release_year is not None:
        songs = songs.filter(extract("year", models.Song.release_date) == search_params.release_year)
    if search_params.release_month is not None:
        songs = songs.filter(extract("month", models.Song.release_date) == search_params.release_month)
    if search_params.release_day is not None:
        songs = songs.filter(extract("day", models.Song.release_date) == search_params.release_day)
    
    if skip is not None:
        songs = songs.offset(skip)
    if max is not None:
        songs = songs.limit(max)
    
    return songs.all()