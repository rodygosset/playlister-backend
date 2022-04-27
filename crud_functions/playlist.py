
from typing import List
from sqlalchemy.orm import Session

from ..crud_functions.song import get_song_by_title
from ..crud_functions.utils import unpack_full_song_title

from .. import crud
from ..crud_functions.artist import get_artist_by_name
from ..crud_functions.genre import get_genre_by_name
from ..crud_functions.tag import get_tag_by_name
from .. import models, schemas
from ..utility import *

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


# CRUD functions for the Playlist model

def get_playlist_song_objects(db: Session, playlist: models.Playlist) -> List[models.Song]:
    """

    Retrieve all the Song objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        playlist (models.Playlist): The provided Playlist object.

    Returns:
        List[models.Song]: The retrieved Song objects.
    """
    if playlist is None:
        return None
    song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.playlist_id == playlist.id).all()
    song_playlist_ids = [song_playlist_item.song_id for song_playlist_item in song_playlist_items]
    playlist_songs = db.query(models.Song).filter(models.Song.id.in_(song_playlist_ids)).all()
    return playlist_songs

def get_playlist_songs(db: Session, playlist: models.Playlist) -> List[str]:
    """

    Retrieve all the Song objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        playlist (models.Playlist): The provided Playlist object.

    Returns:
        List[str]: The title for each of the retrieved Song objects.
    """
    if playlist is None:
        return None
    playlist_songs = get_playlist_song_objects(db, playlist)
    return [playlist_song.title for playlist_song in playlist_songs]



def get_playlist_tag_objects(db: Session, playlist: models.Playlist) -> List[models.Tag]:
    """

    Retrieve all the Tag objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        playlist (models.Playlist): The provided Playlist object.

    Returns:
        List[models.Tag]: The retrieved Tag objects.
    """
    if playlist is None:
        return None
    tag_playlist_items = db.query(models.TagPlaylist).filter(models.TagPlaylist.playlist_id == playlist.id).all()
    tag_playlist_ids = [tag_playlist_item.tag_id for tag_playlist_item in tag_playlist_items]
    playlist_tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_playlist_ids)).all()
    return playlist_tags

def get_playlist_tags(db: Session, playlist: models.Playlist) -> List[str]:
    """

    Retrieve all the Tag objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        playlist (models.Playlist): The provided Playlist object.

    Returns:
        List[str]: The names of the retrieved Tag objects.
    """
    if playlist is None:
        return None
    playlist_tags = get_playlist_tag_objects(db, playlist)
    return [playlist_tag.name for playlist_tag in playlist_tags]



def get_playlist_by_id(db: Session, playlist_id: int, current_user: schemas.User) -> models.Playlist:
    """

    Retrieve a playlist object from from a user's music library using its ID.

    Args:
        db (Session): The session used to access the database.
        playlist_id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        [models.Playlist]: The Playlist object (if found), None (if not found).
    """
    return db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id).filter(models.Playlist.id == playlist_id).first()

def get_playlist_by_name(db: Session, name: str, current_user: schemas.User) -> models.Playlist:
    """

    Retrieve a playlist object from a user's music library using the value of its 'name' cell.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        [models.Playlist]: The Playlist (if found), None (if not found).
    """
    return db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id).filter(models.Playlist.name == name).first()

def get_playlists_from_db(db: Session, max: int, current_user: schemas.User) -> List[models.Playlist]:
    """

    Get a list of Playlist objects.

    Args:
        db (Session): The session used to access the database.
        max (int): The maximum number of playlists to return.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        List[models.Playlist]: The list of Playlist objects retrieved from the database.
    """
    nb_playlists = len(get_all_playlists(db, current_user))
    if max >= nb_playlists:
        return get_all_playlists(db, current_user)
    return db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id).offset(nb_playlists - max).all()


def get_all_playlists(db: Session, current_user: schemas.User) -> List[models.Playlist]:
    """

    Get a list of all the Playlist objects in the database.

    Args:
        db (Session): The session used to access the database.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        List[models.Playlist]: The list of Playlist objects retrieved from the database.
    """
    return db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id).all()


def create_playlist(db: Session, new_playlist: schemas.PlaylistCreate, current_user: schemas.User) -> models.Playlist:
    """

    Create a new Playlist object in the database.

    Args:
        db (Session): The session used to access the database.
        new_playlist (schemas.PlaylistCreate): The Playlist object to be inserted into the database.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Playlist: The newly created Playlist object.
    """
    new_playlist_dict = new_playlist.dict()
    new_playlist_dict["user_id"] = current_user.id
    tags = new_playlist_dict.pop("tags")
    songs = new_playlist_dict.pop("songs")
    # make sure all the tags listed do exist in the database
    if tags is not None:
        for tag in tags:
            db_tag = get_tag_by_name(db, tag, current_user)
            if not db_tag:
                raise_http_404(f"Cannot add playlist '{new_playlist.name}' to the library because tag '{tag}' does not exist.")
    # make sure all the songs listed do exist in the database
    if songs is not None:
        for full_song_title in songs:
            artist, song_title = unpack_full_song_title(full_song_title)
            db_song = get_song_by_title(db, artist, song_title, current_user)
            if not db_song:
                raise_http_404(f"Cannot add playlist '{new_playlist.name}' to the library because song '{song}' does not exist.")
    db_playlist = models.Playlist(**new_playlist_dict)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    # associate the newly created Playlist object to the provided Tag objects
    if tags is not None:
        for tag in tags:
            db_tag = get_tag_by_name(db, tag, current_user)
            tag_playlist_item = schemas.TagPlaylistCreate(playlist_id=db_playlist.id, tag_id=db_tag.id)
            crud.create_tag_playlist(db, tag_playlist_item)
    # associate the newly created Playlist object to the provided Song objects
    if songs is not None:
        for full_song_title in songs:
            artist, song_title = unpack_full_song_title(full_song_title)
            db_song = get_song_by_title(db, artist, song_title, current_user)
            song_playlist_item = schemas.SongPlaylistCreate(playlist_id=db_playlist.id, song_id=db_song.id)
            crud.create_song_playlist(db, song_playlist_item)
    return db_playlist


def delete_playlist(db: Session, name: str, current_user: schemas.User) -> models.Playlist:
    """

    Delete a playlist object from a user's music library.

    Args:
        db (Session): The session used to access the database.
        name (str): The value of the record's 'name' cell.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        models.Playlist: The deleted Playlist object.
    """
    db_playlist = get_playlist_by_name(db, name, current_user)
    if db_playlist is None:
        return None
    # on delete, we need to delete all the SongPlaylist objects associated to this one
    song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.playlist_id == db_playlist.id).all()
    for song_playlist_item in song_playlist_items:
        crud.delete_song_playlist_from_db(db, song_playlist_item.id)
    # on delete, we need to delete all the TagPlaylist objects associated to this one
    tag_playlist_items = db.query(models.TagPlaylist).filter(models.TagPlaylist.playlist_id == db_playlist.id).all()
    for tag_playlist_item in tag_playlist_items:
        crud.delete_tag_playlist_from_db(db, tag_playlist_item.id)
    # now delete the Playlist object
    db.delete(db_playlist)
    db.commit()
    return db_playlist




# used by the update_playlist() function

def update_playlist_songs(db: Session, db_playlist: models.Playlist, playlist: schemas.PlaylistUpdate, current_user: schemas.User) -> bool:
    """

    Update the list of Song objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        db_playlist (models.Playlist): The Playlist object stored in the database.
        playlist (schemas.PlaylistUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's music library we're working in.

    Raises:
        HTTPException: Raise a "404 NOT FOUND" error if one of the Songs objects can't be found.

    Returns:
        bool: True if successful, False if not.
    """
    if playlist.songs is None:
        return False
    current_songs = get_playlist_songs(db, db_playlist)
    # start with checking whether some songs were disassociated from the Playlist object
    for full_song_title in current_songs:
        if full_song_title not in playlist.songs:
            # if a song's been removed
            artist, song_title = unpack_full_song_title(full_song_title)
            db_song = get_song_by_title(db, artist, song_title, current_user)
            if db_song is not None:
                song_playlist_item = crud.get_song_playlist_by_key(db, db_song.id, db_playlist.id)
                if song_playlist_item is not None:
                    crud.delete_song_playlist_from_db(db, song_playlist_item.id)
    # now check if any song has been added
    for full_song_title in playlist.songs:
        if full_song_title not in current_songs:
            # if a song's been added
            # make sure it already exists in the database
            artist, song_title = unpack_full_song_title(full_song_title)
            db_song = get_song_by_title(db, artist, song_title, current_user)
            if not db_song:
                raise_http_404(f"Cannot add song '{full_song_title}' to playlist '{db_playlist.name}' because the song does not exist.")
            # associate the song to the Playlist object
            song_playlist_item = schemas.SongPlaylistCreate(playlist_id=db_playlist.id, song_id=db_song.id)
            crud.create_song_playlist(db, song_playlist_item)
    return True



# used by the update_playlist() function

def update_playlist_tags(db: Session, db_playlist: models.Playlist, playlist: schemas.PlaylistUpdate, current_user: schemas.User) -> bool:
    """

    Update the list of Tag objects associated to a Playlist object.

    Args:
        db (Session): The session used to access the database.
        db_playlist (models.Playlist): The Playlist object stored in the database.
        playlist (schemas.PlaylistUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's music library we're working in.

    Raises:
        HTTPException: Raise a "404 NOT FOUND" error if one of the Tags objects can't be found.

    Returns:
        bool: True if successful, False if not.
    """
    if playlist.tags is None:
        return False
    current_tags = get_playlist_tags(db, db_playlist)
    # start with checking whether some tags were disassociated from the Playlist object
    for current_tag in current_tags:
        if current_tag not in playlist.tags:
            # if a tag's been removed
            db_tag = get_tag_by_name(db, current_tag, current_user)
            tag_playlist_item = crud.get_tag_playlist_by_key(db, db_tag.id, db_playlist.id)
            crud.delete_tag_playlist_from_db(db, tag_playlist_item.id)
    # now check if any file has been added
    for tag in playlist.tags:
        if tag not in current_tags:
            # if a tag's been added
            # make sure it already exists in the database
            db_tag = get_tag_by_name(db, tag, current_user)
            if not db_tag:
                raise_http_404(f"Cannot add tag '{tag}' to playlist '{db_playlist.name}' because the tag does not exist.")
            # associate the tag to the Playlist object
            tag_playlist_item = schemas.TagPlaylistCreate(playlist_id=db_playlist.id, tag_id=db_tag.id)
            crud.create_tag_playlist(db, tag_playlist_item)
    return True


# make changes to a playlist object
# used by the PUT API endpoint for Playlist objects

def update_playlist(db: Session, name: str, playlist: schemas.PlaylistUpdate, current_user: schemas.User) -> models.Playlist:
    """

    Update a Playlist object.

    Args:
        db (Session): The session used to access the database.
        updater (str): The username of the User making the changes.
        name (str): The value of the record's 'name' cell.
        playlist (schemas.PlaylistUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's playlist library we're working in.

    Returns:
        models.Playlist: The updated Playlist object.
    """
    db_playlist = get_playlist_by_name(db, name, current_user)
    if db_playlist is None:
        return None
    # start with updating the list of tags associated to the Playlist object
    if playlist.tags is not None:
        update_playlist_tags(db, db_playlist, playlist, current_user)
    # start with updating the list of songs associated to the Playlist object
    if playlist.songs is not None:
        update_playlist_songs(db, db_playlist, playlist, current_user)
    # update each field present in the PlaylistUpdate object in the database Playlist object
    # except for new_name, which we don't need to store
    for var, value in vars(playlist).items():
        if var == "new_name" or var == "tags" or var == "songs":
            continue
        setattr(db_playlist, var, value) if value else None
    if playlist.new_name is not None:
        db_playlist.name = playlist.new_name
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist
