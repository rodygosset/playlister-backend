from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions

def get_song_playlist_by_id(db: Session, id: int) -> models.SongPlaylist:
    """

    Retrieve a SongPlaylist object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.SongPlaylist: The retrieved SongPlaylist object (if found), None (if not found).
    """
    return db.query(models.SongPlaylist).filter(models.SongPlaylist.id == id).first()

def get_song_playlist_by_key(db: Session, song_id: int, playlist_id: int) -> models.SongPlaylist:
    """

    Retrieve a SongPlaylist object from the database using the value of its 'song_id' & 'playlist_id' cells.

    Args:
        db (Session): The session used to access the database.
        song_id (int): The value of the record's 'song_id' cell.
        playlist_id (int): The value of the record's 'playlist_id' cell.

    Returns:
        models.SongPlaylist: The retrieved SongPlaylist object (if found), None (if not found).
    """
    return db.query(models.SongPlaylist).filter(models.SongPlaylist.song_id == song_id).filter(models.SongPlaylist.playlist_id == playlist_id).first()

def get_all_song_playlist_items(db: Session) -> List[models.SongPlaylist]:
    """

    Retrieve all the SongPlaylist objects from the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.SongPlaylist]: The list of objects.
    """
    return db.query(models.SongPlaylist).all()


def create_song_playlist(db: Session, song_playlist: schemas.SongPlaylistCreate) -> models.SongPlaylist:
    """

    Create a new SongPlaylist object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        song_playlist (schemas.SongPlaylistCreate): The object to be created.

    Returns:
        models.SongPlaylist: The newly created object.
    """
    db_song_playlist = models.SongPlaylist(**song_playlist.dict())
    db.add(db_song_playlist)
    db.commit()
    db.refresh(db_song_playlist)
    return db_song_playlist

def delete_song_playlist_from_db(db: Session, id: int) -> models.SongPlaylist:
    """

    Delete a SongPlaylist object from the database.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.SongPlaylist: The deleted object.
    """
    song_playlist = get_song_playlist_by_id(db, id)
    db.delete(song_playlist)
    db.commit()
    return song_playlist



def update_song_playlist(db: Session, id: int, song_playlist: schemas.SongPlaylistUpdate) -> models.SongPlaylist:
    """

    Update a SongPlaylist object.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        song_playlist (schemas.SongPlaylistUpdate): The object containing the information to be updated.

    Returns:
        models.SongPlaylist: The updated object.
    """
    db_song_playlist = get_song_playlist_by_id(db, id)
    if song_playlist.playlist_id is not None:
        db_song_playlist.playlist_id = song_playlist.playlist_id
    if song_playlist.song_id is not None:
        db_song_playlist.song_id = song_playlist.song_id
    db.add(db_song_playlist)
    db.commit()
    db.refresh(db_song_playlist)
    return db_song_playlist