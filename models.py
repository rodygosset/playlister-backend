from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Interval, String, Date
from sqlalchemy.orm import relationship
from .database import Base


# The classes declared here will be used to read from / write into the database
# They implement our database diagram (which can be found in the project's documentation)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    family_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    tags = relationship("Tag")
    genres = relationship("Genre")
    artists = relationship("Artist")
    songs = relationship("Song")
    playlists = relationship("Playlist")

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    songs = relationship("TagSong")
    playlists = relationship("TagPlaylist")


class TagSong(Base):
    __tablename__ = "tag_song"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey('tag.id'))
    song_id = Column(Integer, ForeignKey('song.id'))

class TagPlaylist(Base):
    __tablename__ = "tag_playlist"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey('tag.id'))
    playlist_id = Column(Integer, ForeignKey('playlist.id'))

class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    songs = relationship("GenreSong")

class GenreSong(Base):
    __tablename__ = "genre_song"

    id = Column(Integer, primary_key=True, index=True)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    song_id = Column(Integer, ForeignKey('song.id'))

class Artist(Base):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    songs = relationship("ArtistSong")

class ArtistSong(Base):
    __tablename__ = "artist_song"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    song_id = Column(Integer, ForeignKey('song.id'))


class Song(Base):
    __tablename__ = "song"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    key = Column(String, nullable=False)
    bpm = Column(Integer, nullable=False)
    url = Column(String, unique=True, nullable=False)
    duration = Column(Interval, nullable=False)
    release_date = Column(Date)
    user_id = Column(Integer, ForeignKey('user.id'))
    tags = relationship("TagSong")
    genres = relationship("GenreSong")
    artists = relationship("ArtistSong")
    playlists = relationship("SongPlaylist")

class SongPlaylist(Base):
    __tablename__ = "song_playlist"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    playlist_id = Column(Integer, ForeignKey('playlist.id'))


class Playlist(Base):
    __tablename__ = "playlist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    tags = relationship("TagPlaylist")
    songs = relationship("SongPlaylist")

