from typing import Optional, List
from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Playlist schema

class PlaylistBase(BaseModel):
    name: str
    user_id: int

class PlaylistCreate(PlaylistBase):
    songs: Optional[List[str]]
    tags: Optional[List[str]]

class PlaylistUpdate(BaseModel):
    new_name: str

class Playlist(PlaylistBase):
    id: int

    class Config:
        orm_mode = True