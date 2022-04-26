from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions

def get_artist_song_by_id(db: Session, id: int) -> models.ArtistSong:
    """

    Retrieve a ArtistSong object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.ArtistSong: The retrieved ArtistSong object (if found), None (if not found).
    """
    return db.query(models.ArtistSong).filter(models.ArtistSong.id == id).first()

def get_artist_song_by_key(db: Session, artist_id: int, song_id: int) -> models.ArtistSong:
    """

    Retrieve a ArtistSong object from the database using the value of its 'artist_id' & 'song_id' cells.

    Args:
        db (Session): The session used to access the database.
        artist_id (int): The value of the record's 'artist_id' cell.
        song_id (int): The value of the record's 'song_id' cell.

    Returns:
        models.ArtistSong: The retrieved ArtistSong object (if found), None (if not found).
    """
    return db.query(models.ArtistSong).filter(models.ArtistSong.artist_id == artist_id).filter(models.ArtistSong.song_id == song_id).first()

def get_all_artist_song_items(db: Session) -> List[models.ArtistSong]:
    """

    Retrieve all the ArtistSong objects from the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.ArtistSong]: The list of objects.
    """
    return db.query(models.ArtistSong).all()


def create_artist_song(db: Session, artist_song: schemas.ArtistSongCreate) -> models.ArtistSong:
    """

    Create a new ArtistSong object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        artist_song (schemas.ArtistSongCreate): The object to be created.

    Returns:
        models.ArtistSong: The newly created object.
    """
    db_artist_song = models.ArtistSong(**artist_song.dict())
    db.add(db_artist_song)
    db.commit()
    db.refresh(db_artist_song)
    return db_artist_song

def delete_artist_song_from_db(db: Session, id: int) -> models.ArtistSong:
    """

    Delete a ArtistSong object from the database.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.ArtistSong: The deleted object.
    """
    artist_song = get_artist_song_by_id(db, id)
    db.delete(artist_song)
    db.commit()
    return artist_song



def update_artist_song(db: Session, id: int, artist_song: schemas.ArtistSongUpdate) -> models.ArtistSong:
    """

    Update a ArtistSong object.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        artist_song (schemas.ArtistSongUpdate): The object containing the information to be updated.

    Returns:
        models.ArtistSong: The updated object.
    """
    db_artist_song = get_artist_song_by_id(db, id)
    if artist_song.song_id is not None:
        db_artist_song.song_id = artist_song.song_id
    if artist_song.artist_id is not None:
        db_artist_song.artist_id = artist_song.artist_id
    db.add(db_artist_song)
    db.commit()
    db.refresh(db_artist_song)
    return db_artist_song