from datetime import timedelta
from typing import Optional, List
from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Playlist schema

class PlaylistBase(BaseModel):
    name: str
    user_id: int
    tags: List[str]
    songs: List[str]

class PlaylistCreate(BaseModel):
    name: str
    songs: Optional[List[str]]
    tags: Optional[List[str]]

class PlaylistUpdate(BaseModel):
    new_name: Optional[str]
    songs: Optional[List[str]]
    tags: Optional[List[str]]

class Playlist(PlaylistBase):
    id: int

    class Config:
        orm_mode = True
        