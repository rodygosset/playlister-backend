
from typing import List
from sqlalchemy.orm import Session

from .. import crud
from ..crud_functions.artist import get_artist_by_name
from ..crud_functions.genre import get_genre_by_name
from ..crud_functions.tag import get_tag_by_name
from .. import models, schemas
from ..utility import *

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


# CRUD functions for the Song model

def get_song_tag_objects(db: Session, song: models.Song) -> List[models.Tag]:
    """

    Retrieve all the Tag objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[models.Tag]: The retrieved Tag objects.
    """
    if song is None:
        return None
    tag_song_items = db.query(models.TagSong).filter(models.TagSong.song_id == song.id).all()
    tag_song_ids = [tag_song_item.tag_id for tag_song_item in tag_song_items]
    song_tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_song_ids)).all()
    return song_tags

def get_song_tags(db: Session, song: models.Song) -> List[str]:
    """

    Retrieve all the Tag objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[str]: The names of the retrieved Tag objects.
    """
    if song is None:
        return None
    song_tags = get_song_tag_objects(db, song)
    return [song_tag.name for song_tag in song_tags]


def get_song_genre_objects(db: Session, song: models.Song) -> List[models.Genre]:
    """

    Retrieve all the Genre objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[models.Genre]: The retrieved Genre objects.
    """
    if song is None:
        return None
    genre_song_items = db.query(models.GenreSong).filter(models.GenreSong.song_id == song.id).all()
    genre_song_ids = [genre_song_item.genre_id for genre_song_item in genre_song_items]
    song_genres = db.query(models.Genre).filter(models.Genre.id.in_(genre_song_ids)).all()
    return song_genres

def get_song_genres(db: Session, song: models.Song) -> List[str]:
    """

    Retrieve all the Genre objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[str]: The names of the retrieved Genre objects.
    """
    if song is None:
        return None
    song_genres = get_song_genre_objects(db, song)
    return [song_genre.name for song_genre in song_genres]

def get_song_artist_objects(db: Session, song: models.Song) -> List[models.Artist]:
    """

    Retrieve all the Artist objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[models.Artist]: The retrieved Artist objects.
    """
    if song is None:
        return None
    artist_song_items = db.query(models.ArtistSong).filter(models.ArtistSong.song_id == song.id).all()
    artist_song_ids = [artist_song_item.artist_id for artist_song_item in artist_song_items]
    song_artists = db.query(models.Artist).filter(models.Artist.id.in_(artist_song_ids)).all()
    return song_artists

def get_song_artists(db: Session, song: models.Song) -> List[str]:
    """

    Retrieve all the Artist objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[str]: The names of the retrieved Artist objects.
    """
    if song is None:
        return None
    song_artists = get_song_artist_objects(db, song)
    return [song_artist.name for song_artist in song_artists]




def get_song_playlist_objects(db: Session, song: models.Song) -> List[models.Playlist]:
    """

    Retrieve all the Playlist objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[models.Playlist]: The retrieved Playlist objects.
    """
    if song is None:
        return None
    song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.song_id == song.id).all()
    song_playlist_ids = [song_playlist_item.playlist_id for song_playlist_item in song_playlist_items]
    song_playlists = db.query(models.Playlist).filter(models.Playlist.id.in_(song_playlist_ids)).all()
    return song_playlists

def get_song_playlists(db: Session, song: models.Song) -> List[str]:
    """

    Retrieve all the Playlist objects associated to a Song object.

    Args:
        db (Session): The session used to access the database.
        song (models.Song): The provided Song object.

    Returns:
        List[str]: The names of the retrieved Playlist objects.
    """
    if song is None:
        return None
    song_playlists = get_song_playlist_objects(db, song)
    return [song_playlist.name for song_playlist in song_playlists]

def get_song_by_id(db: Session, song_id: int, current_user: schemas.User) -> models.Song:
    """

    Retrieve a Song object from from a user's music library using its ID.

    Args:
        db (Session): The session used to access the database.
        song_id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        [models.Song]: The Song object (if found), None (if not found).
    """
    return db.query(models.Song).filter(models.Song.user_id == current_user.id).filter(models.Song.id == song_id).first()

def get_song_by_title(db: Session, artist_name: str, song_title: str, current_user: schemas.User) -> models.Song:
    """

    Retrieve a Song object from a user's music library using its full name (artist + title).

    Args:
        db (Session): The session used to access the database.
        artist_name (str): One of the Artist objects associated to that song.
        song_title (str): The value of the record's 'title' cell.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        [models.Song]: The Song (if found), None (if not found).
    """
    # get all songs matching song_title
    db_songs = db.query(models.Song).filter(models.Song.user_id == current_user.id).filter(models.Song.title == song_title).all()
    # for each song, get a list of the artists associated to it
    artists = [get_song_artists(db, db_song) for db_song in db_songs]
    # filter the list to get the one that's associated to the specified artist
    i = 0
    while i < len(artists):
        if artist_name in artists[i]:
            return db_songs[i]
        i += 1
    return None



def get_songs_from_db(db: Session, max: int, current_user: schemas.User) -> List[models.Song]:
    """

    Get a list of Song objects.

    Args:
        db (Session): The session used to access the database.
        max (int): The maximum number of songs to return.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        List[models.Song]: The list of Song objects retrieved from the database.
    """
    nb_songs = len(get_all_songs(db, current_user))
    if max >= nb_songs:
        return get_all_songs(db, current_user)
    return db.query(models.Song).filter(models.Song.user_id == current_user.id).offset(nb_songs - max).all()
    



def get_all_songs(db: Session, current_user: schemas.User) -> List[models.Song]:
    """

    Get a list of all the Song objects in the database.

    Args:
        db (Session): The session used to access the database.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        List[models.Song]: The list of Song objects retrieved from the database.
    """
    return db.query(models.Song).filter(models.Song.user_id == current_user.id).all()


def create_song(db: Session, new_song: schemas.SongCreate, current_user: schemas.User) -> models.Song:
    """

    Create a new Song object in the database.

    Args:
        db (Session): The session used to access the database.
        new_song (schemas.SongCreate): The Song object to be inserted into the database.
        current_user (schemas.User): The user who's music library we're working in.

    Returns:
        models.Song: The newly created Song object.
    """
    new_song_dict = new_song.dict()
    new_song_dict["user_id"] = current_user.id
    tags = new_song_dict.pop("tags")
    genres = new_song_dict.pop("genres")
    artists = new_song_dict.pop("artists")
    # make sure all the tags listed do exist in the database
    if tags is not None:
        for tag in tags:
            db_tag = get_tag_by_name(db, tag, current_user)
            if not db_tag:
                raise_http_404(f"Cannot add song '{new_song.title}' to the library because tag '{tag}' does not exist.")
    # make sure all the genres listed do exist in the database
    if genres is not None:
        for genre in genres:
            db_genre = get_genre_by_name(db, genre, current_user)
            if not db_genre:
                raise_http_404(f"Cannot add song '{new_song.title}' to the library because genre '{genre}' does not exist.")
    # make sure all the artists listed do exist in the database
    if len(artists) == 0:
        raise_http_400(f"Cannot add song '{new_song.title}' because no artists were specified.")
    else:
        for artist in artists:
            db_artist = get_artist_by_name(db, artist, current_user)
            if not db_artist:
                raise_http_404(f"Cannot add song '{new_song.title}' to the library because artist '{artist}' does not exist.")
    db_song = models.Song(**new_song_dict)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    # associate the newly created Song object to the provided tags
    if tags is not None:
        for tag in tags:
            db_tag = get_tag_by_name(db, tag, current_user)
            tag_song_item = schemas.TagSongCreate(song_id=db_song.id, tag_id=db_tag.id)
            crud.create_tag_song(db, tag_song_item)
    # associate the newly created Song object to the provided genres
    if genres is not None:
        for genre in genres:
            db_genre = get_genre_by_name(db, genre, current_user)
            genre_song_item = schemas.GenreSongCreate(song_id=db_song.id, genre_id=db_genre.id)
            crud.create_genre_song(db, genre_song_item)
    # associate the newly created Song object to the provided artists
    if artists is not None:
        for artist in artists:
            db_artist = get_artist_by_name(db, artist, current_user)
            artist_song_item = schemas.ArtistSongCreate(song_id=db_song.id, artist_id=db_artist.id)
            crud.create_artist_song(db, artist_song_item)
    return db_song


def delete_song(db: Session, artist_name: str, song_title: str, current_user: schemas.User) -> models.Song:
    """

    Delete a song object from a user's music library.

    Args:
        db (Session): The session used to access the database.
        artist_name (str): One of the Artist objects associated to that song.
        song_title (str): The value of the record's 'title' cell.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        models.Song: The deleted Song object.
    """
    db_song = get_song_by_title(db, artist_name, song_title, current_user)
    if db_song is None:
        return None
    # on delete, we need to delete all the TagSong objects associated to this one
    tag_song_items = db.query(models.TagSong).filter(models.TagSong.song_id == db_song.id).all()
    for tag_song_item in tag_song_items:
        crud.delete_tag_song_from_db(db, tag_song_item.id)
    # on delete, we need to delete all the GenreSong objects associated to this one
    genre_song_items = db.query(models.GenreSong).filter(models.GenreSong.song_id == db_song.id).all()
    for genre_song_item in genre_song_items:
        crud.delete_genre_song_from_db(db, genre_song_item.id)
    # on delete, we need to delete all the ArtistSong objects associated to this one
    artist_song_items = db.query(models.ArtistSong).filter(models.ArtistSong.song_id == db_song.id).all()
    for artist_song_item in artist_song_items:
        crud.delete_artist_song_from_db(db, artist_song_item.id)
    # on delete, we need to delete all the SongPlaylist objects associated to this one
    song_playlist_items = db.query(models.SongPlaylist).filter(models.SongPlaylist.song_id == db_song.id).all()
    for song_playlist_item in song_playlist_items:
        crud.delete_song_playlist_from_db(db, song_playlist_item.id)
    # now delete the Song object
    db.delete(db_song)
    db.commit()
    return db_song


# used by the update_song() function

def update_song_tags(db: Session, db_song: models.Song, song: schemas.SongUpdate, current_user: schemas.User) -> bool:
    """

    Update the list of Tag objects associated to a song object.

    Args:
        db (Session): The session used to access the database.
        db_song (models.Song): The Song object stored in the database.
        song (schemas.SongUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's music library we're working in.

    Raises:
        HTTPException: Raise a "404 NOT FOUND" error if one of the Tags objects can't be found.

    Returns:
        bool: True if successful, False if not.
    """
    if song.tags is None:
        return False
    current_tags = get_song_tags(db, db_song)
    # start with checking whether some tags were disassociated from the Song object
    for current_tag in current_tags:
        if current_tag not in song.tags:
            # if a tag's been removed
            db_tag = get_tag_by_name(db, current_tag, current_user)
            tag_song_item = crud.get_tag_song_by_key(db, db_tag.id, db_song.id)
            crud.delete_tag_song_from_db(db, tag_song_item.id)
    # now check if any tag has been added
    for tag in song.tags:
        if tag not in current_tags:
            # if a tag's been added
            # make sure it already exists in the database
            db_tag = get_tag_by_name(db, tag, current_user)
            if not db_tag:
                raise_http_404(f"Cannot add tag '{tag}' to song '{db_song.title}' because the tag does not exist.")
            # associate the tag to the Song object
            tag_song_item = schemas.TagSongCreate(song_id=db_song.id, tag_id=db_tag.id)
            crud.create_tag_song(db, tag_song_item)
    return True


# used by the update_song() function

def update_song_genres(db: Session, db_song: models.Song, song: schemas.SongUpdate, current_user: schemas.User) -> bool:
    """

    Update the list of Genre objects associated to a song object.

    Args:
        db (Session): The session used to access the database.
        db_song (models.Song): The Song object stored in the database.
        song (schemas.SongUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's music library we're working in.

    Raises:
        HTTPException: Raise a "404 NOT FOUND" error if one of the Genres objects can't be found.

    Returns:
        bool: True if successful, False if not.
    """
    if song.genres is None:
        return False
    current_genres = get_song_genres(db, db_song)
    # start with checking whether some genres were disassociated from the Song object
    for current_genre in current_genres:
        if current_genre not in song.genres:
            # if a genre's been removed
            db_genre = get_genre_by_name(db, current_genre, current_user)
            genre_song_item = crud.get_genre_song_by_key(db, db_genre.id, db_song.id)
            crud.delete_genre_song_from_db(db, genre_song_item.id)
    # now check if any genre has been added
    for genre in song.genres:
        if genre not in current_genres:
            # if a genre's been added
            # make sure it already exists in the database
            db_genre = get_genre_by_name(db, genre, current_user)
            if not db_genre:
                raise_http_404(f"Cannot add genre '{genre}' to song '{db_song.title}' because the genre does not exist.")
            # associate the genre to the Song object
            genre_song_item = schemas.GenreSongCreate(song_id=db_song.id, genre_id=db_genre.id)
            crud.create_genre_song(db, genre_song_item)
    return True


# used by the update_song() function

def update_song_artists(db: Session, db_song: models.Song, song: schemas.SongUpdate, current_user: schemas.User) -> bool:
    """

    Update the list of Artist objects associated to a song object.

    Args:
        db (Session): The session used to access the database.
        db_song (models.Song): The Song object stored in the database.
        song (schemas.SongUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's music library we're working in.

    Raises:
        HTTPException: Raise a "404 NOT FOUND" error if one of the Artists objects can't be found.

    Returns:
        bool: True if successful, False if not.
    """
    if song.artists is None:
        return False
    if len(song.artists) == 0:
        raise_http_400("The list of artists associated to a song cannot be empty.")
    current_artists = get_song_artists(db, db_song)
    # start with checking whether some artists were disassociated from the Song object
    for current_artist in current_artists:
        if current_artist not in song.artists:
            # if an artist's been removed
            db_artist = get_artist_by_name(db, current_artist, current_user)
            artist_song_item = crud.get_artist_song_by_key(db, db_artist.id, db_song.id)
            crud.delete_artist_song_from_db(db, artist_song_item.id)
    # now check if any artist has been added
    for artist in song.artists:
        if artist not in current_artists:
            # if an artist's been added
            # make sure it already exists in the database
            db_artist = get_artist_by_name(db, artist, current_user)
            if not db_artist:
                raise_http_404(f"Cannot add artist '{artist}' to song '{db_song.title}' because the artist does not exist.")
            # associate the artist to the Song object
            artist_song_item = schemas.ArtistSongCreate(song_id=db_song.id, artist_id=db_artist.id)
            crud.create_artist_song(db, artist_song_item)
    return True


# make changes to a song object
# used by the PUT API endpoint for Song objects

def update_song(db: Session, artist_name: str, song_title: str, song: schemas.SongUpdate, current_user: schemas.User) -> models.Song:
    """

    Update a Song object.

    Args:
        db (Session): The session used to access the database.
        artist_name (str): One of the Artist objects associated to that song.
        song_title (str): The value of the record's 'title' cell.
        song (schemas.SongUpdate): The object containing the changes to be made.
        current_user (schemas.User): The user who's song library we're working in.

    Returns:
        models.Song: The updated Song object.
    """
    db_song = get_song_by_title(db, artist_name, song_title, current_user)
    if db_song is None:
        return None
    # start with updating the list of artists associated to the Song object
    if song.artists is not None:
        update_song_artists(db, db_song, song, current_user)
    # start with updating the list of tags associated to the Song object
    if song.tags is not None:
        update_song_tags(db, db_song, song, current_user)
    # start with updating the list of genres associated to the Song object
    if song.genres is not None:
        update_song_genres(db, db_song, song, current_user)
    # update each field present in the SongUpdate object in the database Song object
    # except for new_title, which we don't need to store
    for var, value in vars(song).items():
        if var == "new_title" or var == "tags" or var == "genres" or var == "artists":
            continue
        setattr(db_song, var, value) if value else None
    if song.new_title is not None:
        db_song.title = song.new_title
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song
