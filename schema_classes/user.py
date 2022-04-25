from typing import Optional

from pydantic import BaseModel


# The classes declared here will be used to send / recieve objects through HTTP
# Like the classes in models.py, they implement our database diagram.


# defining our User schema

class UserBase(BaseModel):
    username: str
    firstName: str
    familyName: str
    email: str

class UserCreate(BaseModel):
    username: str
    firstName: str
    familyName: str
    email: str
    hashed_password: str

# used to update the current user (no need to specify the username)

class UserUpdate(BaseModel):
    new_username: Optional[str]
    firstName: Optional[str]
    familyName: Optional[str]
    email: Optional[str]
    

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True