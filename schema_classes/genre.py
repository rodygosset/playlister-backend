from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Genre schema

class GenreBase(BaseModel):
    name: str
    user_id: int

class GenreCreate(BaseModel):
    name: str

class GenreUpdate(BaseModel):
    new_name: str

class Genre(GenreBase):
    id: int

    class Config:
        orm_mode = True