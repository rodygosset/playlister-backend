from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas

# some of those CRUD operations require the user to be authenticated
# checks for appropriate permissions aren't performed here
# rather, they're performed in the files calling the following functions


# CRUD functions for the User model

# getters

def get_user_by_id(db: Session, user_id: int) -> models.User:
    """

    Retrieve a User object from the database using its ID.

    Args:
        db (Session): The session used to access the database.
        user_id (int): Equivalent to sqlite's ROWID -> the value of the record's primary key.

    Returns:
        [models.User]: The User (if found), None (if not found).
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> models.User:
    """

    Retrieve a User object from the database using its username.

    Args:
        db (Session): The session used to access the database.
        username (str): The value of the record's 'username' cell.

    Returns:
        [models.User]: The User (if found), None (if not found).
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> models.User:
    """

    Retrieve a User object from the database using its email address.

    Args:
        db (Session): The session used to access the database.
        email (str): The value of the record's 'email' cell.

    Returns:
        models.User: The User (if found), None (if not found).
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """

    Get a list of User objects (starting at index 'skip' and ending at index 'limit').

    Args:
        db (Session): The session used to access the database.
        skip (int, optional): Start index. Defaults to 0.
        limit (int, optional): End index. Defaults to 100.

    Returns:
        List[models.User]: The list of User objects retrieved from the database.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def get_all_users(db: Session) -> List[models.User]:
    """

    Get a list of all the User objects in the database.

    Args:
        db (Session): The session used to access the database.

    Returns:
        List[models.User]: The list of User objects retrieved from the database.
    """
    return db.query(models.User).all()


# useful for registration

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """

    Create a new User in the database.

    Args:
        db (Session): The session used to access the database.
        user (schemas.UserCreate): The User object to be inserted into the database.

    Returns:
        models.User: The newly created User.
    """
    # we don't hash the password here
    # password hashing upon user registration is handled in auth.py
    # this function recieves a schemas.UserCreate instance with an already hashed password
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# careful with that one...

def delete_user_from_db(db: Session, username: str) -> models.User:
    """

    Delete a User from the database.

    Args:
        db (Session): The session used to access the database.
        username (str): The value of the record's 'username' cell.

    Returns:
        models.User: The deleted User object.
    """
    user = get_user_by_username(db, username=username)
    db.delete(user)
    db.commit()
    return user

def update_user(db: Session, updater: str, username: str, user: schemas.UserUpdate) -> models.User:
    """

    Update User information.

    Args:
        db (Session): The session used to access the database.
        updater (str): The 'username' corresponding to the user making the changes.
        username (str): The value of the record's 'username' cell.
        user (schemas.UserUpdate): The object containing the changes to be made.

    Returns:
        models.User: The updated models.User object.
    """
    db_user = get_user_by_username(db, username)
    if db_user is None:
        return None
    
    # update each field present in the UserUpdate object in the database User object
    # except for new_username, which we don't need to store
    for var, value in vars(user).items():
        if var == "new_username":
            continue
        # print("Updating " + str(var) + " => " + str(user_dict[var]))
        setattr(db_user, var, value) if value else None
    if user.dict()["new_username"] is not None:
        db_user.username = user.new_username
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
