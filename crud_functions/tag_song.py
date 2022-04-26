from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions

def get_tag_song_by_id(db: Session, id: int) -> models.TagSong:
    """

    Retrieve a TagSong object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.TagSong: The retrieved TagSong object (if found), None (if not found).
    """
    return db.query(models.TagSong).filter(models.TagSong.id == id).first()

def get_tag_song_by_key(db: Session, tag_id: int, song_id: int) -> models.TagSong:
    """

    Retrieve a TagSong object from the database using the value of its 'tag_id' & 'song_id' cells.

    Args:
        db (Session): The session used to access the database.
        tag_id (int): The value of the record's 'tag_id' cell.
        song_id (int): The value of the record's 'song_id' cell.

    Returns:
        models.TagSong: The retrieved TagSong object (if found), None (if not found).
    """
    return db.query(models.TagSong).filter(models.TagSong.tag_id == tag_id).filter(models.TagSong.song_id == song_id).first()

def get_all_tag_song_items(db: Session) -> List[models.TagSong]:
    """

    Retrieve all the TagSong objects from the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.TagSong]: The list of objects.
    """
    return db.query(models.TagSong).all()


def create_tag_song(db: Session, tag_song: schemas.TagSongCreate) -> models.TagSong:
    """

    Create a new TagSong object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        tag_song (schemas.TagSongCreate): The object to be created.

    Returns:
        models.TagSong: The newly created object.
    """
    db_tag_song = models.TagSong(**tag_song.dict())
    db.add(db_tag_song)
    db.commit()
    db.refresh(db_tag_song)
    return db_tag_song

def delete_tag_song_from_db(db: Session, id: int) -> models.TagSong:
    """

    Delete a TagSong object from the database.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.TagSong: The deleted object.
    """
    tag_song = get_tag_song_by_id(db, id)
    db.delete(tag_song)
    db.commit()
    return tag_song



def update_tag_song(db: Session, id: int, tag_song: schemas.TagSongUpdate) -> models.TagSong:
    """

    Update a TagSong object.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        tag_song (schemas.TagSongUpdate): The object containing the information to be updated.

    Returns:
        models.TagSong: The updated object.
    """
    db_tag_song = get_tag_song_by_id(db, id)
    if tag_song.song_id is not None:
        db_tag_song.song_id = tag_song.song_id
    if tag_song.tag_id is not None:
        db_tag_song.tag_id = tag_song.tag_id
    db.add(db_tag_song)
    db.commit()
    db.refresh(db_tag_song)
    return db_tag_song