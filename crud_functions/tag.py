from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas, crud

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


def get_tag_tag_song_objects(db: Session, tag: models.Tag) -> List[models.TagSong]:
    """

    Retrieve all the TagSong objects associated to a Tag object.

    Args:
        db (Session): The session used to access the database.
        tag (models.Tag): The provided Tag object.

    Returns:
        List[models.TagSong]: The retrieved TagSong objects.
    """
    if tag is None:
        return None
    tag_song_items = db.query(models.TagSong).filter(models.TagSong.tag_id == tag.id).all()
    return tag_song_items

def get_tag_tag_playlist_objects(db: Session, tag: models.Tag) -> List[models.TagPlaylist]:
    """

    Retrieve all the TagPlaylist objects associated to a Tag object.

    Args:
        db (Session): The session used to access the database.
        tag (models.Tag): The provided Tag object.

    Returns:
        List[models.TagPlaylist]: The retrieved TagPlaylist objects.
    """
    if tag is None:
        return None
    tag_playlist_items = db.query(models.TagPlaylist).filter(models.TagPlaylist.tag_id == tag.id).all()
    return tag_playlist_items


def get_tag_by_id(db: Session, id: int, current_user: schemas.User) -> models.Tag:
    """

    Retrieve a Tag object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Tag: The retrieved Tag object (if found), None (if not found).
    """
    return db.query(models.Tag).filter(models.Tag.user_id == current_user.id).filter(models.Tag.id == id).first()

def get_tag_by_name(db: Session, name: str, current_user: schemas.User) -> models.Tag:
    """

    Retrieve a Tag object from the database using the value of its 'name' cell.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Tag: The retrieved Tag object (if found), None (if not found).
    """
    return db.query(models.Tag).filter(models.Tag.user_id == current_user.id).filter(models.Tag.name == name).first()

def get_all_tags(db: Session, current_user: schemas.User) -> List[models.Tag]:
    """

    Retrieve all the Tag objects from the database.

    Args:
        db (Session): The session used to access the database.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        List[models.Tag]: The list of objects.
    """
    return db.query(models.Tag).filter(models.Tag.user_id == current_user.id).all()


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """

    Create a new Tag object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        tag (schemas.TagCreate): The object to be created.

    Returns:
        models.Tag: The newly created object.
    """
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag_from_db(db: Session, name: str, current_user: schemas.User) -> models.Tag:
    """

    Delete a Tag object from the database.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Tag: The deleted object.
    """
    tag = get_tag_by_name(db, name, current_user)
    # dissociate the Tag object from all the TagSong
    # & TagPlaylist it was associated to
    association_items = get_tag_tag_song_objects(db, tag)
    for item in association_items:
        crud.delete_tag_song_from_db(db, item.id)
    association_items = get_tag_tag_playlist_objects(db, tag)
    for item in association_items:
        crud.delete_tag_playlist_from_db(db, item.id)
    db.delete(tag)
    db.commit()
    return tag



def update_tag(db: Session, name: str, tag: schemas.TagUpdate) -> models.Tag:
    """

    Update a Tag object.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        tag (schemas.TagUpdate): The object containing the information to be updated.

    Returns:
        models.Tag: The updated object.
    """
    db_tag = get_tag_by_name(db, name)
    db_tag.name = tag.new_name
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag