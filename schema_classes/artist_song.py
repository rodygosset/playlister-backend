from typing import Optional
from pydantic import BaseModel


# The classes declared here will be used to represent association tables

# defining our ArtistSong schema

class ArtistSongBase(BaseModel):
    song_id: int
    artist_id: int

class ArtistSongCreate(ArtistSongBase):
    pass

class ArtistSongUpdate(BaseModel):
    song_id: Optional[int]
    artist_id: Optional[int]
    

class ArtistSong(ArtistSongBase):
    id: int

    class Config:
        orm_mode = True