from typing import Optional
from pydantic import BaseModel


# The classes declared here will be used to represent association tables

# defining our TagSong schema

class TagSongBase(BaseModel):
    song_id: int
    tag_id: int

class TagSongCreate(TagSongBase):
    pass

class TagSongUpdate(BaseModel):
    song_id: Optional[int]
    tag_id: Optional[int]
    

class TagSong(TagSongBase):
    id: int

    class Config:
        orm_mode = True