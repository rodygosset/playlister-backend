from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


# The classes declared here will be used to read from / write into the database
# They implement our database diagram (which can be found in the project's documentation)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    firstName = Column(String)
    familyName = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
