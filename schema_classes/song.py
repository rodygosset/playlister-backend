from datetime import date, timedelta
from typing import List, Optional
from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Song schema

class SongBase(BaseModel):
    title: str
    key: str
    bpm: int
    url: str
    duration: timedelta
    release_date: date
    user_id: int
    tags: List[str]
    genres: List[str]
    artists: List[str]

class SongCreate(SongBase):
    title: str
    key: str
    bpm: int
    url: str
    duration: timedelta
    release_date: date
    tags: Optional[List[str]]
    genres: Optional[List[str]]
    artists: List[str]


class SongUpdate(BaseModel):
    new_title: Optional[str]
    key: Optional[str]
    bpm: Optional[int]
    url: Optional[str]
    duration: Optional[timedelta]
    release_date: Optional[date]
    user_id: Optional[int]
    tags: Optional[List[str]]
    genres: Optional[List[str]]
    artists: Optional[List[str]]

class SongSearchParams(BaseModel):
    title: Optional[str]
    key: Optional[str]
    bpm: Optional[int]
    url: Optional[str]
    duration: Optional[timedelta]
    release_year: Optional[int]
    release_month: Optional[int]
    release_day: Optional[int]
    tags: Optional[List[str]]
    genres: Optional[List[str]]
    artists: Optional[List[str]]

class Song(SongBase):
    id: int

    class Config:
        orm_mode = True