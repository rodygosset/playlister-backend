from fastapi import Depends, HTTPException, status

from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from .crud import get_user_by_username
from . import schemas
from .utility import get_db, raise_http_400

# The backbone of the authentication system is here
# --> all the necessary functions to perform token creation (login) and user registration


SECRET_KEY = "5435790c3d5c6403c880fccdc330acfda6acf528087c74429acf5d21452d5258"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models

# -- Token Models

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



# used to get the hashed version of a password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# authentication utility functions

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """

    Verify whether a given 'plain_password' corresponds to a 'hashed_password'.

    Args:
        plain_password (str): Password in plain text.
        hashed_password (str): Hashed password.

    Returns:
        bool: True if the passwords match, False if not.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """

    Hash a given 'password'.

    Args:
        password (str): Password in plain text.

    Returns:
        str: The hashed version of the password.
    """
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> schemas.User:
    """

    Return a schemas.User object with the corresponding 'username'.

    Args:
        db (Session): The session used to access the database.
        username (str): The user's username.

    Returns:
        [type]: The schemas.User object (if found), None (if not found).
    """
    user = get_user_by_username(db, username)
    if user is not None:
        return schemas.User(**(user.__dict__))
    else:
        return None

def authenticate_user(db: Session, username:str, password: str):
    """

    Verify the credentials for the provided 'username'.

    Args:
        db (Session): The session used to access the database.
        username (str): The provided username.
        password (str): The provided password supposed to correspond to the user identified by the provided 'username'.

    Returns:
        bool, schemas.User: The corresponding schemas.User object (if credentials are valid), False if not.
    """
    user = get_user(db, username)
    # check whether the user exists
    if not user:
        return False
    # if they do exist, check whether the password is correct
    user_password = get_user_by_username(db, user.username).hashed_password
    if not verify_password(password, user_password):
        return False
    return user


# use the following function to create an access token 

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """

    Create an access token.

    Args:
        data (dict): The data used to generate the token.
        expires_delta (Optional[timedelta], optional): The amount of time after which the token will expire. Defaults to None.

    Returns:
        str: The newly created token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else: 
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# use the following function to get a user object using a token

async def get_user_using_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> schemas.User:
    """

    Retrieve a user from the database using a token.

    Args:
        token (str): The provided token containing the username. Defaults to Depends(oauth2_scheme).
        db (Session): The session used to access the database. Defaults to Depends(get_db).

    Raises:
        credentials_exception: Raised when the token isn't valid or the user can't be found in the database.

    Returns:
        schemas.User: the schemas.User object (if found), None (if not found).
    """
    # create once and for all the exception we throw when something goes wrong in this function
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Failed to validate the provided authentication information.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode / unpack the token into a usable dictionary
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        # check whether the token contains a username
        if username is None:
            # if not
            raise credentials_exception
        # if the user exists
        token_data = TokenData(username=username)
    except JWTError: # if the JWT is not correct
        raise credentials_exception
    # try to get the user
    user = get_user(db, username=token_data.username)
    if user is None: 
        # if we can't get the user with the requested username for some reason
        raise credentials_exception
    return user



# use the following function to get a user object using a token 
# while also checking whether that token has expired

async def get_current_active_user(current_user: schemas.User = Depends(get_user_using_token)):
    """

    Return a schemas.User object only if the User is active.

    Args:
        current_user (schemas.User): The User object to be returned. Defaults to Depends(get_user_using_token).

    Raises:
        HTTPException: Raised if the user isn't active.

    Returns:
        schemas.User: The retrieved schemas.User object.
    """
    if not current_user.is_active:
        raise_http_400("Inactive user.")
    return current_user


