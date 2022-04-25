from typing import Optional
from pydantic import BaseModel


# The classes declared here will be used to represent association tables

# defining our TagPlaylist schema

class TagPlaylistBase(BaseModel):
    playlist_id: int
    tag_id: int

class TagPlaylistCreate(TagPlaylistBase):
    pass

class TagPlaylistUpdate(BaseModel):
    playlist_id: Optional[int]
    tag_id: Optional[int]
    

class TagPlaylist(TagPlaylistBase):
    id: int

    class Config:
        orm_mode = True