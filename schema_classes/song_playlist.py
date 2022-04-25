from typing import Optional
from pydantic import BaseModel


# The classes declared here will be used to represent association tables

# defining our SongPlaylist schema

class SongPlaylistBase(BaseModel):
    song_id: int
    playlist_id: int

class SongPlaylistCreate(SongPlaylistBase):
    pass

class SongPlaylistUpdate(BaseModel):
    song_id: Optional[int]
    playlist_id: Optional[int]
    

class SongPlaylist(SongPlaylistBase):
    id: int

    class Config:
        orm_mode = True