from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"


# creating a fresh engine

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)


# fresh session

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# fresh base

Base = declarative_base()