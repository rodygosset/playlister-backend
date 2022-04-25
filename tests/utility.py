# utility functions
from sqlalchemy.orm.session import Session
from starlette.responses import Response
from starlette.testclient import TestClient

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from .. import crud, schemas
from ..auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# /!\ test environment setup /!\

# create & setup a test database

def db_setup() -> sessionmaker:
    """

    Create and setup the test database.

    Returns:
        sessionmaker: Used to connect to the database.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal

def db_populate(db: Session):
    """

    Populate the test database with necessary data.

    Args:
        db (Session): Used to connect to the database.
    """
    test_pwd = "testpassword123"
    crud.create_user(db, schemas.UserCreate(
            username="test",
            first_name="Test",
            family_name="Test",
            email="test@example.com",
            hashed_password=get_password_hash(test_pwd)
    ))

# useful in setup, to upload data to the API before running the tests

def post_json(json_file_path: str, url: str, client: TestClient):
    # log in 
    auth_header = get_auth_header(login_as_test(client))
    # upload the data
    items = []
    with open(json_file_path, "r") as data_file:
        items = json.load(data_file)
    for item in items:
        response = client.post(url,
                               headers=auth_header, json=item)
        assert response.status_code == 200, response.text


def login_as_test(client: TestClient) -> Response:
    """

    Provide the API with valid credentials and get a token in return.

    Returns:
        Response: The API response.
    """
    # try logging in with the test account
    test_login_data = {
        "username": "test",
        "password": "testpassword123"
    }
    # login request...
    response = client.post("/token/", data=test_login_data)
    return response

def login_as_test1(client: TestClient) -> Response:
    """

    Provide the API with valid credentials and get a token in return.

    Returns:
        Response: The API response.
    """
    # try logging in with the second test account
    test1_login_data = {
        "username": "test1",
        "password": "test1password123"
    }
    # login request...
    response = client.post("/token/", data=test1_login_data)
    return response

def login(client: TestClient, username: str, password: str) -> Response:
    """"

    Provide the API with valid credentials and get a token in return.

    Returns:
        Response: The API response.
    """
    login_data = {"username": username, "password": password}
    response = client.post("/token/", data=login_data)
    return response

def get_auth_header(resp: Response) -> dict:
    """

    Build an HTTP authentication header from a response containing a token.

    Args:
        resp (Response): The HTTP response containing the token.

    Raises:
        Exception: Occurs when the response's data isn't formatted correctly.

    Returns:
        dict: The HTTP authentication header.
    """
    token = resp.json()
    if "token_type" not in token or "access_token" not in token:
        raise Exception(f"Incorrect token format : {token}.")
    auth_header = {"Authorization": f"{token['token_type']} {token['access_token']}"}
    return auth_header

