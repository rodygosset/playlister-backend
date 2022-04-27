

from fastapi.testclient import TestClient
import os

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
# /!\ TEST SETUP /!\

def test_setup():
    """
    Make sure we have all the resources we need to run the tests.
    """
    test1_pwd = "test1password123"
    crud.create_user(db, schemas.UserCreate(
            username="test1",
            first_name="Test",
            family_name="Test",
            email="test1@example.com",
            hashed_password=get_password_hash(test1_pwd)
    ))
    



# --------------------------------------------------------------------------
# /!\ TEST POST /!\

post_data = {
    "name": "Big Room"
}

def test_post_genre_401_login():
    """
    Make sure that a POST at '/api/genres/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    global post_data
    # trying to post without being logged in
    response = client.post("/api/genres/", json=post_data)
    assert response.status_code == 401, response.text


def test_post_genre():
    """
    Make sure that a POST at '/api/genres/':
    - returns the newly created 'Genre' object when nothing goes wrong.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # trying to post without running into any HTTP errors
    response = client.post("/api/genres/", headers=auth_header, json=post_data)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 1,
        "name": "Big Room",
        "user_id": 1
    }
    assert data == expected_data, "Incorrect response format or data."

def test_post_genre_409_duplicate():
    """
    Make sure that a POST at '/api/genres/':
    - returns an HTTP 409 when the item already exists in the database.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post data that already exists in the DB
    # must result in a 409
    response = client.post("/api/genres/", headers=auth_header, json=post_data)
    assert response.status_code == 409, response.text

def test_post_genre_2nd_item():
    """
    Make sure that a POST at '/api/genres/':
    - returns the newly created 'Genre' object when nothing goes wrong.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post another item
    post_data["name"] = "Future Bounce"
    response = client.post("/api/genres/", headers=auth_header, json=post_data)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 2,
        "name": "Future Bounce",
        "user_id": 1
    }
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST GET ALL /!\

def test_get_all_genres_401_login():
    """
    Make sure that a GET at '/api/genres/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    # trying to GET without being logged in
    response = client.get("/api/genres/")
    assert response.status_code == 401, response.text

def test_get_all_genres_ownership():
    """
    Make sure that a GET at '/api/genres/':
    - returns an empty array as the response's data when logged in with an account that has an empty library.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test1(client))
    # verify that we receive an empty array as reponse data
    # when making this request from an account that hasn't created any genres
    # ==> users can't access each other's music libraries
    response = client.get("/api/genres/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [], "Incorrect response format or data."

def test_get_all_genres():
    """
    Make sure that a GET at '/api/genres/':
    - returns the list of 'Genre' objects when nothing goes wrong.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test(client))
    # now checking that we recieve the correct data when nothing goes wrong
    response = client.get("/api/genres/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "Big Room",
            "user_id": 1
        },
        {
            "id": 2,
            "name": "Future Bounce",
            "user_id": 1
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



# --------------------------------------------------------------------------
# /!\ TEST PUT /!\


put_data = {
    "new_name": "Future House"
}

def test_put_genre_401_login():
    """
    Make sure that a PUT at '/api/genres/{name}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    global put_data
    # try to PUT without being logged in
    response = client.put("/api/genres/Future Bounce", json=put_data)
    assert response.status_code == 401, response.text


def test_put_genre_404_ownership():
    """
    Make sure that a PUT at '/api/genres/{name}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    global put_data
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.put("/api/genres/Future Bounce", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_genre_404_name():
    """
    Make sure that a PUT at '/api/genres/{name}':
    - returns an HTTP 404 when the 'Genre' object doesn't exist in the DB.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.put("/api/genres/non_existent_item", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_genre_409_name_in_use():
    """
    Make sure that a PUT at '/api/genres/{name}':
    - returns an HTTP 409 when the 'new_name' attribute corresponds to an existing Genre object.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to change the 'name' attribute to one that's already used
    # ==> 409 
    response = client.put("/api/genres/Future Bounce", headers=auth_header, json={"new_name": "Big Room"})
    assert response.status_code == 409, response.text

def test_put_genre():
    """
    Make sure that a PUT at '/api/genres/{name}':
    - returns the updated 'Genre' object when nothing goes wrong.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT without running into any HTTP errors
    response = client.put("/api/genres/Future Bounce", headers=auth_header, json=put_data)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 2,
        "name": "Future House",
        "user_id": 1
    }
    assert data == expected_data, "Incorrect response format or data."



# --------------------------------------------------------------------------
# /!\ TEST DELETE /!\

def test_delete_genre_401_login():
    """
    Make sure that a DELETE at '/api/genres/{name}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    # try to DELETE without being logged in
    response = client.delete("/api/genres/Future House")
    assert response.status_code == 401, response.text


def test_delete_genre_404_ownership():
    """
    Make sure that a DELETE at '/api/genres/{name}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.delete("/api/genres/Future House", headers=auth_header)
    assert response.status_code == 404, response.text


def test_delete_genre_404():
    """
    Make sure that a DELETE at '/api/genres/{name}':
    - returns an HTTP 404 when the 'Genre' object doesn't exist in the DB.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.delete("/api/genres/non_existent_item", headers=auth_header)
    assert response.status_code == 404, response.text

def test_delete_genre():
    """
    Make sure that a DELETE at '/api/genres/{name}':
    - returns the deleted 'Genre' object when nothing goes wrong.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to DELETE an item without running into any HTTP errors
    response = client.delete("/api/genres/Future House", headers=auth_header)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 2,
        "name": "Future House",
        "user_id": 1
    }
    assert data == expected_data, "Incorrect response format or data."
