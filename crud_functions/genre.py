from typing import List
from sqlalchemy.orm import Session

from ..crud_functions.utils import get_full_song_title

from .. import models, schemas, crud

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


def get_genre_genre_song_objects(db: Session, genre: models.Genre) -> List[models.GenreSong]:
    """

    Retrieve all the GenreSong objects associated to a Genre object.

    Args:
        db (Session): The session used to access the database.
        genre (models.Genre): The provided Genre object.

    Returns:
        List[models.GenreSong]: The retrieved GenreSong objects.
    """
    if genre is None:
        return None
    genre_song_items = db.query(models.GenreSong).filter(models.GenreSong.genre_id == genre.id).all()
    return genre_song_items

def get_genre_songs(db: Session, genre: models.Genre, current_user: schemas.User) -> List[str]:
    """

    Retrieve all the Song objects associated to a Genre object.

    Args:
        db (Session): The session used to access the database.
        genre (models.Genre): The provided Genre object.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        List[str]: The full title for each of the retrieved Song objects.
    """
    if genre is None:
        return None
    genre_song_items = get_genre_genre_song_objects(db, genre)
    song_ids = [genre_song_item.song_id for genre_song_item in genre_song_items]
    db_songs = [crud.get_song_by_id(db, song_id, current_user) for song_id in song_ids]
    return [get_full_song_title(db, db_song) for db_song in db_songs]


def get_genre_by_id(db: Session, id: int, current_user: schemas.User) -> models.Genre:
    """

    Retrieve a Genre object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Genre: The retrieved Genre object (if found), None (if not found).
    """
    return db.query(models.Genre).filter(models.Genre.user_id == current_user.id).filter(models.Genre.id == id).first()

def get_genre_by_name(db: Session, name: str, current_user: schemas.User) -> models.Genre:
    """

    Retrieve a Genre object from the database using the value of its 'name' cell.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Genre: The retrieved Genre object (if found), None (if not found).
    """
    return db.query(models.Genre).filter(models.Genre.user_id == current_user.id).filter(models.Genre.name == name).first()

def get_all_genres(db: Session, current_user: schemas.User) -> List[models.Genre]:
    """

    Retrieve all the Genre objects from the database.

    Args:
        db (Session): The session used to access the database.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        List[models.Genre]: The list of objects.
    """
    return db.query(models.Genre).filter(models.Genre.user_id == current_user.id).all()


def create_genre(db: Session, genre: schemas.GenreCreate, current_user: schemas.User) -> models.Genre:
    """

    Create a new Genre object and save it into the database.

    Args:
        db (Session): The session used to access the database.
        genre (schemas.GenreCreate): The object to be created.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Genre: The newly created object.
    """
    new_genre_dict = { **genre.dict(), "user_id": current_user.id }
    db_genre = models.Genre(**new_genre_dict)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

def delete_genre_from_db(db: Session, name: str, current_user: schemas.User) -> models.Genre:
    """

    Delete a Genre object from the database.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Genre: The deleted object.
    """
    genre = get_genre_by_name(db, name, current_user)
    # dissociate the Genre object from all the GenreSong
    # & GenrePlaylist it was associated to
    association_items = get_genre_genre_song_objects(db, genre)
    for item in association_items:
        crud.delete_genre_song_from_db(db, item.id)
    db.delete(genre)
    db.commit()
    return genre



def update_genre(db: Session, name: str, genre: schemas.GenreUpdate, current_user: schemas.User) -> models.Genre:
    """

    Update a Genre object.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        genre (schemas.GenreUpdate): The object containing the information to be updated.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Genre: The updated object.
    """
    db_genre = get_genre_by_name(db, name, current_user)
    db_genre.name = genre.new_name
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre