from typing import Optional
from pydantic import BaseModel


# The classes declared here will be used to represent association tables

# defining our GenreSong schema

class GenreSongBase(BaseModel):
    song_id: int
    genre_id: int

class GenreSongCreate(GenreSongBase):
    pass

class GenreSongUpdate(BaseModel):
    song_id: Optional[int]
    genre_id: Optional[int]
    

class GenreSong(GenreSongBase):
    id: int

    class Config:
        orm_mode = True