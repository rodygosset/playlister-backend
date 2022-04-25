from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our Tag schema

class TagBase(BaseModel):
    name: str
    user_id: int

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    new_name: str

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True