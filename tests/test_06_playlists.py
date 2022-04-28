

from datetime import timedelta
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
    # POST some of the data we need to be able to perform the tests
    post_json("backend/json/tags.json", "/api/tags/", client)
    post_json("backend/json/genres.json", "/api/genres/", client)
    post_json("backend/json/artists.json", "/api/artists/", client)
    post_json("backend/json/songs.json", "/api/songs/", client)
    
    



# --------------------------------------------------------------------------
# /!\ TEST POST /!\

post_data = {
    "name": "GOATs",
    "tags": ["Energetic"],
    "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
}

def test_post_playlist_401_login():
    """
    Make sure that a POST at '/api/playlists/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    global post_data
    # trying to post without being logged in
    response = client.post("/api/playlists/", json=post_data)
    assert response.status_code == 401, response.text

def test_post_playlist_404_tags():
    """
    Make sure that a POST at '/api/playlists/':
    - returns an HTTP 404 when one of the specified tags doesn't exist.
    """
    global post_data
    wrong_post_data = post_data.copy()
    wrong_post_data["tags"] = ["Energetic", "non-existent-tag"]
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try POSTing this ==> 404
    response = client.post("/api/playlists/", headers=auth_header, json=wrong_post_data)
    assert response.status_code == 404, response.text


def test_post_playlist_404_songs():
    """
    Make sure that a POST at '/api/playlists/':
    - returns an HTTP 404 when one of the specified songs doesn't exist.
    """
    global post_data
    wrong_post_data = post_data.copy()
    wrong_post_data["songs"] = ["Martin Garrix - Diamonds", "King Julian - I Like to Move It"]
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try POSTing this ==> 404
    response = client.post("/api/playlists/", headers=auth_header, json=wrong_post_data)
    assert response.status_code == 404, response.text

def test_post_playlist():
    """
    Make sure that a POST at '/api/playlists/':
    - returns the newly created 'Playlist' object when nothing goes wrong.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # trying to post without running into any HTTP errors
    response = client.post("/api/playlists/", headers=auth_header, json=post_data)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 1,
        "name": "GOATs",
        "user_id": 1,
        "tags": ["Energetic"],
        "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
    }
    assert data == expected_data, "Incorrect response format or data."

def test_post_playlist_409_duplicate():
    """
    Make sure that a POST at '/api/playlists/':
    - returns an HTTP 409 when the item already exists in the database.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post data that already exists in the DB
    # must result in a 409
    response = client.post("/api/playlists/", headers=auth_header, json=post_data)
    assert response.status_code == 409, response.text


post_data_1 = {
    "name": "FH Sweets",
    "tags": ["Energetic"],
    "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
} 

def test_post_playlist_2nd_item():
    """
    Make sure that a POST at '/api/playlists/':
    - returns the newly created 'Playlist' object when nothing goes wrong.
    """
    global post_data_1
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post another item
    response = client.post("/api/playlists/", headers=auth_header, json=post_data_1)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 2,
        "name": "FH Sweets",
        "user_id": 1,
        "tags": ["Energetic"],
        "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
    }
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST GET ALL /!\

def test_get_all_playlists_401_login():
    """
    Make sure that a GET at '/api/playlists/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    # trying to GET without being logged in
    response = client.get("/api/playlists/")
    assert response.status_code == 401, response.text

def test_get_all_playlists_ownership():
    """
    Make sure that a GET at '/api/playlists/':
    - returns an empty array as the response's data when logged in with an account that has an empty library.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test1(client))
    # verify that we receive an empty array as reponse data
    # when making this request from an account that hasn't created any playlists
    # ==> users can't access each other's music libraries
    response = client.get("/api/playlists/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [], "Incorrect response format or data."

def test_get_all_playlists():
    """
    Make sure that a GET at '/api/playlists/':
    - returns the list of 'Playlist' objects when nothing goes wrong.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test(client))
    # now checking that we recieve the correct data when nothing goes wrong
    response = client.get("/api/playlists/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        },
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."





# --------------------------------------------------------------------------
# /!\ TEST SEARCH /!\


def test_search_playlists_401_login():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    # try to search without being logged in
    response = client.post("/api/playlists/search/", json={})
    # should result in a 401
    assert response.status_code == 401, response.text


def test_search_playlists_empty_ownership():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns an empty array when connected with a different user's account.
    """
    search_params = {
        "name": "s"
    }
    # log in
    auth_header = get_auth_header(login_as_test1(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."

def test_search_playlists_400_negative_value():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns an HTTP 400 error when 'skip' or 'max' has a negative value.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # make sure we get an HTTP 400 when skip has a negative value
    response = client.post("/api/playlists/search/?skip=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text
    # make sure we get an HTTP 400 when max has a negative value
    response = client.post("/api/playlists/search/?max=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text
    # try with both
    response = client.post("/api/playlists/search/?skip=-1&max=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text

def test_search_playlists_by_name():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns the list of Playlist objects matching our 'name' search parameter when nothing goes wrong.
    """
    search_params = {
        "name": "F"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "name": "G"
    }
    # try another search
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "name": "s"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        },
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."


def test_search_playlists_by_tags():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns the list of Playlist objects matching our 'tags' search parameter when nothing goes wrong.
    """
    search_params = {
        "tags": ["Energetic"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        },
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "tags": ["non-existent-tag"]
    }
    # try another search
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."

def test_search_playlists_by_songs():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns the list of Playlist objects matching our 'songs' search parameter when nothing goes wrong.
    """
    search_params = {
        "songs": ["Julian Jordan - Diamonds"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "songs": ["Benix - Legacy"]
    }
    # try another search
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_playlists_no_result():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns an empty list when no Playlist object matches our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return no result
    search_params = {
        "name": "High On Life"
    }
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."


def test_search_playlists_all():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns a list of all Playlist objects in the DB when they all match our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return all Playlist objects
    search_params = {}
    response = client.post("/api/playlists/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "name": "GOATs",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Martin Garrix - Diamonds", "RetroVision - Bring The Beat Back"]
        },
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."


def test_search_playlists_boundaries():
    """
    Make sure that a POST at '/api/playlists/search/?skip={skip}&max={max}':
    - returns the part of the search results that correspond to the 'skip' & 'max' query parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # all Playlist objects match our search parameters when they're empty
    search_params = {}
    # try getting only some of the results
    response = client.post("/api/playlists/search/?skip=1&max=1", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "name": "FH Sweets",
            "user_id": 1,
            "tags": ["Energetic"],
            "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # list of results should be empty when max == 0
    response = client.post("/api/playlists/search/?skip=1&max=0", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST GET NUMBER SEARCH RESULTS /!\

def test_search_playlists_nb_401_login():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    # try to search without being logged in
    response = client.post("/api/playlists/search/nb", json={})
    # should result in a 401
    assert response.status_code == 401, response.text



def test_search_playlists_nb_empty_ownership():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns 0 when connected with a different user's account.
    """
    search_params = {
        "name": "s"
    }
    # log in
    auth_header = get_auth_header(login_as_test1(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."




def test_search_playlists_by_name_nb():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns the numer of Playlist objects matching our 'name' search parameter when nothing goes wrong.
    """
    search_params = {
        "name": "G"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "name": "FH"
    }
    # try another search
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "name": "s"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."




def test_search_playlists_by_tags_nb():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns the number of Playlist objects matching our 'tags' search parameter when nothing goes wrong.
    """
    search_params = {
        "tags": ["Energetic"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "tags": ["non-existent-tag"]
    }
    # try another search
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."



def test_search_playlists_by_songs_nb():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns the number of Playlist objects matching our 'songs' search parameter when nothing goes wrong.
    """
    search_params = {
        "songs": ["Benix - Legacy"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "songs": ["Brooks - Better When You're Gone"]
    }
    # try another search
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."



def test_search_playlists_nb_no_result():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns 0 when no Playlist object matches our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return no result
    search_params = {
        "name": "High On Life"
    }
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."

def test_search_playlists_max_nb():
    """
    Make sure that a POST at '/api/playlists/search/nb':
    - returns the number of Playlist objects matching our empty search parameters when nothing goes wrong (should be the number of Playlist objects in the database).
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return all Playlist objects
    search_params = {}
    response = client.post("/api/playlists/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST PUT /!\


put_data = {
    "new_name": "The GOATs",
    "songs": ["RetroVision - Bring The Beat Back"]
}

def test_put_playlist_401_login():
    """
    Make sure that a PUT at '/api/playlists/{name}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    global put_data
    # try to PUT without being logged in
    response = client.put("/api/playlists/GOATs", json=put_data)
    assert response.status_code == 401, response.text


def test_put_playlist_404_ownership():
    """
    Make sure that a PUT at '/api/playlists/{name}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    global put_data
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.put("/api/playlists/GOATs", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_playlist_404_name():
    """
    Make sure that a PUT at '/api/playlists/{name}':
    - returns an HTTP 404 when the 'Playlist' object doesn't exist in the DB.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.put("/api/playlists/non-existent-playlist", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_playlist_409_name_in_use():
    """
    Make sure that a PUT at '/api/playlists/{name}':
    - returns an HTTP 409 when the 'new_name' attribute corresponds to an existing Playlist object.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to change the 'name' attribute to one that's already used
    # ==> 409 
    response = client.put("/api/playlists/FH Sweets", headers=auth_header, json={"new_name": "GOATs"})
    assert response.status_code == 409, response.text

def test_put_playlist():
    """
    Make sure that a PUT at '/api/playlists/{name}':
    - returns the updated 'Playlist' object when nothing goes wrong.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT without running into any HTTP errors
    response = client.put("/api/playlists/GOATs", headers=auth_header, json=put_data)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 1,
        "name": "The GOATs",
        "user_id": 1,
        "tags": ["Energetic"],
        "songs": ["RetroVision - Bring The Beat Back"]
    }
    assert data == expected_data, "Incorrect response format or data."



# --------------------------------------------------------------------------
# /!\ TEST DELETE /!\

def test_delete_playlist_401_login():
    """
    Make sure that a DELETE at '/api/playlists/{name}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    # try to DELETE without being logged in
    response = client.delete("/api/playlists/FH Sweets")
    assert response.status_code == 401, response.text


def test_delete_playlist_404_ownership():
    """
    Make sure that a DELETE at '/api/playlists/{name}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.delete("/api/playlists/FH Sweets", headers=auth_header)
    assert response.status_code == 404, response.text


def test_delete_playlist_404():
    """
    Make sure that a DELETE at '/api/playlists/{name}':
    - returns an HTTP 404 when the 'Playlist' object doesn't exist in the DB.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.delete("/api/playlists/non_existent_item", headers=auth_header)
    assert response.status_code == 404, response.text

def test_delete_playlist():
    """
    Make sure that a DELETE at '/api/playlists/{name}':
    - returns the deleted 'Playlist' object when nothing goes wrong.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to DELETE an item without running into any HTTP errors
    response = client.delete("/api/playlists/FH Sweets", headers=auth_header)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 2,
        "name": "FH Sweets",
        "user_id": 1,
        "tags": ["Energetic"],
        "songs": ["Dirty Palm - Legacy", "Brooks - Better When You're Gone"]
    }
    assert data == expected_data, "Incorrect response format or data."
