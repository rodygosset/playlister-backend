from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions

def get_tag_playlist_by_id(db: Session, id: int) -> models.TagPlaylist:
    """

    Retrieve a TagPlaylist object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.TagPlaylist: The retrieved TagPlaylist object (if found), None (if not found).
    """
    return db.query(models.TagPlaylist).filter(models.TagPlaylist.id == id).first()

def get_tag_playlist_by_key(db: Session, tag_id: int, playlist_id: int) -> models.TagPlaylist:
    """

    Retrieve a TagPlaylist object from the database using the value of its 'tag_id' & 'playlist_id' cells.

    Args:
        db (Session): The session used to access the database.
        tag_id (int): The value of the record's 'tag_id' cell.
        playlist_id (int): The value of the record's 'playlist_id' cell.

    Returns:
        models.TagPlaylist: The retrieved TagPlaylist object (if found), None (if not found).
    """
    return db.query(models.TagPlaylist).filter(models.TagPlaylist.tag_id == tag_id).filter(models.TagPlaylist.playlist_id == playlist_id).first()

def get_all_tag_playlist_items(db: Session) -> List[models.TagPlaylist]:
    """

    Retrieve all the TagPlaylist objects from the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.TagPlaylist]: The list of objects.
    """
    return db.query(models.TagPlaylist).all()


def create_tag_playlist(db: Session, tag_playlist: schemas.TagPlaylistCreate) -> models.TagPlaylist:
    """

    Create a new TagPlaylist object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        tag_playlist (schemas.TagPlaylistCreate): The object to be created.

    Returns:
        models.TagPlaylist: The newly created object.
    """
    db_tag_playlist = models.TagPlaylist(**tag_playlist.dict())
    db.add(db_tag_playlist)
    db.commit()
    db.refresh(db_tag_playlist)
    return db_tag_playlist

def delete_tag_playlist_from_db(db: Session, id: int) -> models.TagPlaylist:
    """

    Delete a TagPlaylist object from the database.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        models.TagPlaylist: The deleted object.
    """
    tag_playlist = get_tag_playlist_by_id(db, id)
    db.delete(tag_playlist)
    db.commit()
    return tag_playlist



def update_tag_playlist(db: Session, id: int, tag_playlist: schemas.TagPlaylistUpdate) -> models.TagPlaylist:
    """

    Update a TagPlaylist object.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        tag_playlist (schemas.TagPlaylistUpdate): The object containing the information to be updated.

    Returns:
        models.TagPlaylist: The updated object.
    """
    db_tag_playlist = get_tag_playlist_by_id(db, id)
    if tag_playlist.playlist_id is not None:
        db_tag_playlist.playlist_id = tag_playlist.playlist_id
    if tag_playlist.tag_id is not None:
        db_tag_playlist.tag_id = tag_playlist.tag_id
    db.add(db_tag_playlist)
    db.commit()
    db.refresh(db_tag_playlist)
    return db_tag_playlist