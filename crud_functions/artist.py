from typing import List
from sqlalchemy.orm import Session

from .. import models, schemas, crud

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


def get_artist_artist_song_objects(db: Session, artist: models.Artist) -> List[models.ArtistSong]:
    """

    Retrieve all the ArtistSong objects associated to an artist object.

    Args:
        db (Session): The session used to access the database.
        artist (models.Artist): The provided Artist object.

    Returns:
        List[models.ArtistSong]: The retrieved ArtistSong objects.
    """
    if artist is None:
        return None
    artist_song_items = db.query(models.ArtistSong).filter(models.ArtistSong.artist_id == artist.id).all()
    return artist_song_items


def get_artist_by_id(db: Session, id: int, current_user: schemas.User) -> models.Artist:
    """

    Retrieve an artist object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Artist: The retrieved Artist object (if found), None (if not found).
    """
    return db.query(models.Artist).filter(models.Artist.user_id == current_user.id).filter(models.Artist.id == id).first()

def get_artist_by_name(db: Session, name: str, current_user: schemas.User) -> models.Artist:
    """

    Retrieve an artist object from the database using the value of its 'name' cell.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Artist: The retrieved Artist object (if found), None (if not found).
    """
    return db.query(models.Artist).filter(models.Artist.user_id == current_user.id).filter(models.Artist.name == name).first()

def get_all_artists(db: Session, current_user: schemas.User) -> List[models.Artist]:
    """

    Retrieve all the Artist objects from the database.

    Args:
        db (Session): The session used to access the database.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        List[models.Artist]: The list of objects.
    """
    return db.query(models.Artist).filter(models.Artist.user_id == current_user.id).all()


def create_artist(db: Session, artist: schemas.ArtistCreate) -> models.Artist:
    """

    Create a new Artist object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        artist (schemas.ArtistCreate): The object to be created.

    Returns:
        models.Artist: The newly created object.
    """
    db_artist = models.Artist(**artist.dict())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

def delete_artist_from_db(db: Session, name: str, current_user: schemas.User) -> models.Artist:
    """

    Delete an artist object from the database.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Artist: The deleted object.
    """
    artist = get_artist_by_name(db, name, current_user)
    # dissociate the Artist object from all the ArtistSong
    # & ArtistPlaylist it was associated to
    association_items = get_artist_artist_song_objects(db, artist)
    for item in association_items:
        crud.delete_artist_song_from_db(db, item.id)
    db.delete(artist)
    db.commit()
    return artist



def update_artist(db: Session, name: str, artist: schemas.ArtistUpdate, current_user: schemas.User) -> models.Artist:
    """

    Update an artist object.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        artist (schemas.ArtistUpdate): The object containing the information to be updated.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Artist: The updated object.
    """
    db_artist = get_artist_by_name(db, name, current_user)
    db_artist.name = artist.new_name
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist