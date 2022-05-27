import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:playlister@localhost/postgres"

DATABASE_URL = os.environ['DATABASE_URL']

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


# creating a fresh engine

engine = create_engine(
    DATABASE_URL, 
    # connect_args={"check_same_thread": False}
)


# fresh session

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# fresh base

Base = declarative_base()