
import os
from fastapi.testclient import TestClient
from sqlalchemy.engine.base import NestedTransaction
from starlette.testclient import TestClient

# necessary imports to open & use a database connection

from ..main import app, get_db
from .utility import *

# /!\ test environment setup /!\

if os.path.isfile("test.db"):
    os.remove("test.db")

# setting up the test database

TestingSessionLocal = db_setup()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# override the app dependencies, to make sure we're using our test DB

app.dependency_overrides[get_db] = override_get_db

# populating the database

db = next(override_get_db())

db_populate(db)

client = TestClient(app)

# /!\ Test functions /!\


# --------------------------------------------------------------------------
# /!\ TEST POST USER /!\


new_user = {
        "username": "test",
        "first_name": "Test",
        "family_name": "Test",
        "email": "test1@example.com",
        "hashed_password": "test1password123"
    }

def test_post_user_400_username_taken():
    """
    Make sure that a POST at '/api/users/':
    - returns an HTTP 400 error if the username is already taken.
    """
    global new_user
    response = client.post("/api/users/", json=new_user)
    # make sure we're getting an http 400 error
    # when trying to create a user with a pre-existing username
    assert response.status_code == 400, response.text

def test_post_user_400_email_taken():
    """
    Make sure that a POST at '/api/users/':
    - returns an HTTP 400 error if the username is already taken.
    """
    global new_user
    new_user["username"] = "test1"
    new_user["email"] = "test@example.com"
    response = client.post("/api/users/", json=new_user)
    # make sure we're getting an http 400 error
    # when trying to create a user with an e-mail address
    # that's already taken
    assert response.status_code == 400, response.text

def test_post_user():
    """
    Make sure that a POST at '/api/users/':
    - returns the newly created User object when nothing goes wrong.
    """
    global new_user
    new_user["email"] = "test1@example.com"
    response = client.post("/api/users/", json=new_user)
    # make sure we got an HTTP_200_OK status
    # & that we didn't get an empty response
    assert response.status_code == 200, response.text
    # get the response data as a dictionary
    data = response.json()
    # make sure all the expected keys are present
    expected_data = {
        **new_user, 
        "id": 2, 
        "is_active": True
    }
    expected_data.pop("hashed_password")
    assert expected_data == data, "Format de réponse ou données incorrects."


# --------------------------------------------------------------------------
# /!\ TEST LOGIN /!\

def test_login_401_incorrect_credentials():
    """
    Make sure that a POST at '/token/':
    - returns an HTTP 401 error when incorrect credentials are provided.
    """
    # trying with the wrong credentials
    response = client.post("/token/", data={"username": "test", "password": "123" })
    assert response.status_code == 401, response.text

def test_login():
    """
    Make sure that a POST at '/token/':
    - returns a valid token when correct credentials are provided.
    """
    # try logging in with the test account
    test_login_data = {
        "username": "test",
        "password": "testpassword123"
    }
    # logging in...
    response = client.post("/token/", data=test_login_data)
    assert response.status_code == 200, f"Response : {response.headers}"
    data = response.json()
    assert "access_token" in data, "No valid taken found in API response."
    assert "token_type" in data, "No token found in API response."
    # try logging in with the second test account (with the correct credentials)
    test1_login_data = {
        "username": "test1",
        "password": "test1password123"
    }
    response = client.post("/token/", data=test1_login_data)
    data = response.json()
    assert response.status_code == 200, f"Response : {response}"
    assert "access_token" in data, "Pas de token valide dans la réponse."
    assert "token_type" in data, "La réponse ne contient pas le token."

# --------------------------------------------------------------------------
# /!\ TEST GET CURRENT USER'S INFO /!\

def test_get_current_user_401_login():
    """
    Make sure that a GET at '/api/users/me':
    - returns an HTTP 401 error when the user is not logged in.
    """
    # try getting the data without being logged in
    # must result in a, HTTP 401 error
    response = client.get("/api/users/me")
    assert response.status_code == 401, response.text

def test_get_current_user():
    """
    Make sure that a GET at '/api/users/me':
    - returns the right User object when nothing goes wrong.
    """
    # log in...
    auth_header = get_auth_header(login_as_test(client))
    # making the API call
    response = client.get("/api/users/me", headers=auth_header)
    data = response.json()
    expected_data = {
        "id": 1,
        "username": "test",
        "first_name": "Test",
        "family_name": "Test",
        "email": "test@example.com",
        "is_active": True
    }
    # making sure we're getting an HTTP 200
    assert response.status_code == 200, response.text
    # making sure the data is what's expected
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST GET A LIST OF USERS FROM THE DB /!\


def test_get_users_401_login():
    """
    Make sure that a GET at '/api/users/':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    response = client.get("/api/users/")
    # try getting the data without being logged in
    # must result in a, HTTP 401 error
    assert response.status_code == 401, response.text

def test_get_users():
    """
    Make sure that a GET at '/api/users/':
    - returns a list of User objects when nothing goes wrong.
    """
    auth_header = get_auth_header(login_as_test(client))
    # get a list of the users in the database
    expected_data = [
        {
            "id": 1,
            "username": "test",
            "first_name": "Test",
            "family_name": "Test",
            "email": "test@example.com",
            "is_active": True
        },
        {
            "id": 2,
            "username": "test1",
            "first_name": "Test",
            "family_name": "Test",
            "email": "test1@example.com",
            "is_active": True,
        }
    ]
    # request & assert
    response = client.get("/api/users/", headers=auth_header)
    data = response.json()
    assert response.status_code == 200, response.text
    assert data == expected_data, "Format de réponse ou données incorrects."


# --------------------------------------------------------------------------
# /!\ TEST PUT CURRENT USER /!\


# the data
put_data = {
    "email": "new_test@example.com"
}

def test_put_current_user_401_login():
    """
    Make sure that a PUT at '/api/users/me':
    - returns an HTTP 401 error when not logged in.
    """
    global put_data
    # try to PUT data without being logged in
    response = client.put("/api/users/me", json=put_data)
    # should result in a 401
    assert response.status_code == 401, response.text


def test_put_current_user_409_username():
    """
    Make sure that a PUT at '/api/users/me':
    - returns an HTTP 409 error when trying to change the username to one that's already used.
    """
    # log in as the 'test' user
    auth_header = get_auth_header(login_as_test1(client))
    # make sure we get a 409 when trying to change the username to one that's already used
    response = client.put("/api/users/me", headers=auth_header, json={"new_username": "test"})
    assert response.status_code == 409, response.text

def test_put_current_user():
    """
    Make sure that a PUT at '/api/users/me':
    - returns the updated User object when nothing goes wrong.
    """
    global put_data
    # log in as the 'test' user
    auth_header = get_auth_header(login_as_test1(client))
    put_data["new_username"] = "tester"
    # now try to make the changes without getting any HTTP errors
    # useful for assertion 
    expected_data = {
        "id": 2,
        "username": "tester",
        "first_name": "Test",
        "family_name": "Test",
        "email": "new_test@example.com",
        "is_active": True
    }
    # request
    response = client.put("/api/users/me", headers=auth_header, json=put_data)
    data = response.json()
    assert response.status_code == 200, response.text
    # making sure the data is what it's supposed to be
    assert data == expected_data, "Incorrect response format or data."
    # loggin back in 
    auth_header = get_auth_header(login(client, "tester", "test1password123"))
    # changing back the username
    put_data.update({"username": "tester", "new_username": "test1"})
    expected_data["username"] = "test1"
    response = client.put("/api/users/me", headers=auth_header, json=put_data)
    data = response.json()
    assert response.status_code == 200, response.text
    # making sure the data is what it's supposed to be
    assert data == expected_data, "Incorrect response format or data."

# --------------------------------------------------------------------------
# /!\ TEST DELETE /!\

def test_delete_user_401_login():
    """
    Make sure that a DELETE at '/api/users/me':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    # try to delete data without being logged in
    response = client.delete("/api/users/me")
    # should result in a 401
    assert response.status_code == 401, response.text

def test_delete_user():
    """
    Make sure that a DELETE at '/api/users/me':
    - returns the deleted User object when nothing goes wrong
    """
    # log in as test
    auth_header = get_auth_header(login_as_test(client))
    # now delete the test user
    response = client.delete("/api/users/me", headers=auth_header)
    deleted_user = response.json()
    # make sure everything when right
    assert response.status_code == 200, response.text
    # log in as test1
    auth_header = get_auth_header(login_as_test1(client))
    # check that the deleted user isn't present in the database anymore
    response = client.get("/api/users/", headers=auth_header)
    assert response.status_code == 200, response.text
    current_db_users = response.json()
    assert deleted_user not in current_db_users, "The user was not deleted from the database."