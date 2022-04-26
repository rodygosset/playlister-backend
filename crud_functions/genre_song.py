from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions

def get_genre_song_by_id(db: Session, id: int) -> models.GenreSong:
    """

    Retrieve a GenreSong object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.GenreSong: The retrieved GenreSong object (if found), None (if not found).
    """
    return db.query(models.GenreSong).filter(models.GenreSong.id == id).first()

def get_genre_song_by_key(db: Session, genre_id: int, song_id: int) -> models.GenreSong:
    """

    Retrieve a GenreSong object from the database using the value of its 'genre_id' & 'song_id' cells.

    Args:
        db (Session): The session used to access the database.
        genre_id (int): The value of the record's 'genre_id' cell.
        song_id (int): The value of the record's 'song_id' cell.

    Returns:
        models.GenreSong: The retrieved GenreSong object (if found), None (if not found).
    """
    return db.query(models.GenreSong).filter(models.GenreSong.genre_id == genre_id).filter(models.GenreSong.song_id == song_id).first()

def get_all_genre_song_items(db: Session) -> List[models.GenreSong]:
    """

    Retrieve all the GenreSong objects from the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.GenreSong]: The list of objects.
    """
    return db.query(models.GenreSong).all()


def create_genre_song(db: Session, genre_song: schemas.GenreSongCreate) -> models.GenreSong:
    """

    Create a new GenreSong object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        genre_song (schemas.GenreSongCreate): The object to be created.

    Returns:
        models.GenreSong: The newly created object.
    """
    db_genre_song = models.GenreSong(**genre_song.dict())
    db.add(db_genre_song)
    db.commit()
    db.refresh(db_genre_song)
    return db_genre_song

def delete_genre_song_from_db(db: Session, id: int) -> models.GenreSong:
    """

    Delete a GenreSong object from the database.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.GenreSong: The deleted object.
    """
    genre_song = get_genre_song_by_id(db, id)
    db.delete(genre_song)
    db.commit()
    return genre_song



def update_genre_song(db: Session, id: int, genre_song: schemas.GenreSongUpdate) -> models.GenreSong:
    """

    Update a GenreSong object.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        genre_song (schemas.GenreSongUpdate): The object containing the information to be updated.

    Returns:
        models.GenreSong: The updated object.
    """
    db_genre_song = get_genre_song_by_id(db, id)
    if genre_song.song_id is not None:
        db_genre_song.song_id = genre_song.song_id
    if genre_song.genre_id is not None:
        db_genre_song.genre_id = genre_song.genre_id
    db.add(db_genre_song)
    db.commit()
    db.refresh(db_genre_song)
    return db_genre_song