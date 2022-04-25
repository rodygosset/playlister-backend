from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Artist schema

class ArtistBase(BaseModel):
    name: str
    user_id: int

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(BaseModel):
    new_name: str

class Artist(ArtistBase):
    id: int

    class Config:
        orm_mode = True