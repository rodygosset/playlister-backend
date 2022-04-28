

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
    
    



# --------------------------------------------------------------------------
# /!\ TEST POST /!\

post_data = {
    "title": "Legacy",
    "key": "G Major",
    "bpm": 128,
    "url": "https://youtu.be/nHn39P1bAT4",
    "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
    "release_date": "2021-12-10",
    "tags": ["Energetic"],
    "genres": ["EDM", "Bass House"],
    "artists": ["Dirty Palm", "Benix"]
}

def test_post_song_401_login():
    """
    Make sure that a POST at '/api/songs/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    global post_data
    # trying to post without being logged in
    response = client.post("/api/songs/", json=post_data)
    assert response.status_code == 401, response.text

def test_post_song_404_tags():
    """
    Make sure that a POST at '/api/songs/':
    - returns an HTTP 404 when one of the specified tags doesn't exist.
    """
    global post_data
    wrong_post_data = post_data.copy()
    wrong_post_data["tags"] = ["Energetic", "non-existent-tag"]
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try POSTing this ==> 404
    response = client.post("/api/songs/", headers=auth_header, json=wrong_post_data)
    assert response.status_code == 404, response.text

def test_post_song_404_genres():
    """
    Make sure that a POST at '/api/songs/':
    - returns an HTTP 404 when one of the specified genres doesn't exist.
    """
    global post_data
    wrong_post_data = post_data.copy()
    wrong_post_data["genres"] = ["Bass House", "non-existent-genre"]
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try POSTing this ==> 404
    response = client.post("/api/songs/", headers=auth_header, json=wrong_post_data)
    assert response.status_code == 404, response.text


def test_post_song_404_artists():
    """
    Make sure that a POST at '/api/songs/':
    - returns an HTTP 404 when one of the specified artists doesn't exist.
    """
    global post_data
    wrong_post_data = post_data.copy()
    wrong_post_data["artists"] = ["Martin Garrix", "King Julian"]
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try POSTing this ==> 404
    response = client.post("/api/songs/", headers=auth_header, json=wrong_post_data)
    assert response.status_code == 404, response.text

def test_post_song():
    """
    Make sure that a POST at '/api/songs/':
    - returns the newly created 'Song' object when nothing goes wrong.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # trying to post without running into any HTTP errors
    response = client.post("/api/songs/", headers=auth_header, json=post_data)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 1,
        "title": "Legacy",
        "key": "G Major",
        "bpm": 128,
        "url": "https://youtu.be/nHn39P1bAT4",
        "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
        "release_date": "2021-12-10",
        "user_id": 1,
        "tags": ["Energetic"],
        "genres": ["EDM", "Bass House"],
        "artists": ["Dirty Palm", "Benix"]
    }
    assert data == expected_data, "Incorrect response format or data."

def test_post_song_409_duplicate():
    """
    Make sure that a POST at '/api/songs/':
    - returns an HTTP 409 when the item already exists in the database.
    """
    global post_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post data that already exists in the DB
    # must result in a 409
    response = client.post("/api/songs/", headers=auth_header, json=post_data)
    assert response.status_code == 409, response.text


post_data_1 = {
    "title": "Diamonds",
    "key": "C# Minor",
    "bpm": 125,
    "url": "https://www.beatport.com/track/diamonds/16087263",
    "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
    "release_date": "2021-12-31",
    "tags": ["Energetic"],
    "genres": ["Bass House"],
    "artists": ["Martin Garrix", "Julian Jordan"]
} 

def test_post_song_2nd_item():
    """
    Make sure that a POST at '/api/songs/':
    - returns the newly created 'Song' object when nothing goes wrong.
    """
    global post_data_1
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to post another item
    response = client.post("/api/songs/", headers=auth_header, json=post_data_1)
    assert response.status_code == 200, response.text
    # make sure we recieve the correct data back
    data = response.json()
    expected_data = {
        "id": 2,
        "title": "Diamonds",
        "key": "C# Minor",
        "bpm": 125,
        "url": "https://www.beatport.com/track/diamonds/16087263",
        "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
        "release_date": "2021-12-31",
        "user_id": 1,
        "tags": ["Energetic"],
        "genres": ["Bass House"],
        "artists": ["Martin Garrix", "Julian Jordan"]
    }
    assert data == expected_data, "Incorrect response format or data."


# --------------------------------------------------------------------------
# /!\ TEST GET ALL /!\

def test_get_all_songs_401_login():
    """
    Make sure that a GET at '/api/songs/':
    - returns an HTTP 401 when the user isn't logged in.
    """
    # trying to GET without being logged in
    response = client.get("/api/songs/")
    assert response.status_code == 401, response.text

def test_get_all_songs_ownership():
    """
    Make sure that a GET at '/api/songs/':
    - returns an empty array as the response's data when logged in with an account that has an empty library.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test1(client))
    # verify that we receive an empty array as reponse data
    # when making this request from an account that hasn't created any songs
    # ==> users can't access each other's music libraries
    response = client.get("/api/songs/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [], "Incorrect response format or data."

def test_get_all_songs():
    """
    Make sure that a GET at '/api/songs/':
    - returns the list of 'Song' objects when nothing goes wrong.
    """
    # logging in as the test user 
    auth_header = get_auth_header(login_as_test(client))
    # now checking that we recieve the correct data when nothing goes wrong
    response = client.get("/api/songs/", headers=auth_header)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."





# --------------------------------------------------------------------------
# /!\ TEST SEARCH /!\


def test_search_songs_401_login():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    # try to search without being logged in
    response = client.post("/api/songs/search/", json={})
    # should result in a 401
    assert response.status_code == 401, response.text
    

def test_search_songs_empty_ownership():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns an empty list when logged in with another user's account.
    """
    # log in
    auth_header = get_auth_header(login_as_test1(client))
    # try to search without getting any HTTP errors
    search_params = {
        "title": "a"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_400_negative_value():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns an HTTP 400 error when 'skip' or 'max' has a negative value.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # make sure we get an HTTP 400 when skip has a negative value
    response = client.post("/api/songs/search/?skip=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text
    # make sure we get an HTTP 400 when max has a negative value
    response = client.post("/api/songs/search/?max=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text
    # try with both
    response = client.post("/api/songs/search/?skip=-1&max=-1", headers=auth_header, json={})
    assert response.status_code == 400, response.text

def test_search_songs_by_title():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'title' search parameter when nothing goes wrong.
    """
    search_params = {
        "title": "D"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "title": "Leg"
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "title": "a"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_key():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'key' search parameter when nothing goes wrong.
    """
    search_params = {
        "key": "C#"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "key": "G"
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "key": "m"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_bpm():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'bpm' search parameter when nothing goes wrong.
    """
    search_params = {
        "bpm": 125
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "bpm": 128
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_url():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'url' search parameter when nothing goes wrong.
    """
    search_params = {
        "url": "beatport"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "url": "youtu.be"
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "url": "https://"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_tags():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'tags' search parameter when nothing goes wrong.
    """
    search_params = {
        "tags": ["Energetic"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "tags": ["non-existent-tag"]
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_genres():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'genres' search parameter when nothing goes wrong.
    """
    search_params = {
        "genres": ["EDM"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "genres": ["Bass House"]
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_artists():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'artists' search parameter when nothing goes wrong.
    """
    search_params = {
        "artists": ["Benix"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "artists": ["Martin Garrix"]
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_duration_minutes():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'duration_minutes' search parameter when nothing goes wrong.
    """
    search_params = {
        "duration_minutes": 3
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "duration_minutes": 2
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_duration_seconds():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'duration_seconds' search parameter when nothing goes wrong.
    """
    search_params = {
        "duration_minutes": 3,
        "duration_seconds": 23
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "duration_minutes": 2,
        "duration_seconds": 39
    }
    # try another search
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_no_result():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns an empty list when no Song object matches our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return no result
    search_params = {
        "title": "High On Life"
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_all():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns a list of all Song objects in the DB when they all match our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return all Song objects
    search_params = {}
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_boundaries():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the part of the search results that correspond to the 'skip' & 'max' query parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # all Song objects match our search parameters when they're empty
    search_params = {}
    # try getting only some of the results
    response = client.post("/api/songs/search/?skip=1&max=1", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # list of results should be empty when max == 0
    response = client.post("/api/songs/search/?skip=1&max=0", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_release_year():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'release_year' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_year
    search_params = {
        "release_year": 2021
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_year
    search_params = {
        "release_year": 2020
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."

def test_search_songs_by_release_month():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'release_month' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_month
    search_params = {
        "release_month": 12
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        },
        {
            "id": 2,
            "title": "Diamonds",
            "key": "C# Minor",
            "bpm": 125,
            "url": "https://www.beatport.com/track/diamonds/16087263",
            "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
            "release_date": "2021-12-31",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["Bass House"],
            "artists": ["Martin Garrix", "Julian Jordan"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_month
    search_params = {
        "release_month": 6
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_release_day():
    """
    Make sure that a POST at '/api/songs/search/?skip={skip}&max={max}':
    - returns the list of Song objects matching our 'release_day' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_day
    search_params = {
        "release_day": 10
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = [
        {
            "id": 1,
            "title": "Legacy",
            "key": "G Major",
            "bpm": 128,
            "url": "https://youtu.be/nHn39P1bAT4",
            "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
            "release_date": "2021-12-10",
            "user_id": 1,
            "tags": ["Energetic"],
            "genres": ["EDM", "Bass House"],
            "artists": ["Dirty Palm", "Benix"]
        }
    ]
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_day
    search_params = {
        "release_day": 27
    }
    response = client.post("/api/songs/search/", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = []
    assert data == expected_data, "Incorrect response format or data."

# --------------------------------------------------------------------------
# /!\ TEST GET NUMBER SEARCH RESULTS /!\

def test_search_songs_nb_401_login():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns an HTTP 401 error when the user isn't logged in.
    """
    # try to search without being logged in
    response = client.post("/api/songs/search/nb", json={})
    # should result in a 401
    assert response.status_code == 401, response.text


def test_search_songs_nb_empty_ownership():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns 0 when logged in with another user's account.
    """
    # log in
    auth_header = get_auth_header(login_as_test1(client))
    # try to search without getting any HTTP errors
    search_params = {
        "title": "a"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_title_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the numer of Song objects matching our 'title' search parameter when nothing goes wrong.
    """
    search_params = {
        "title": "D"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "title": "Leg"
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "title": "a"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_key_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'key' search parameter when nothing goes wrong.
    """
    search_params = {
        "key": "C#"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "key": "G"
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "key": "m"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_bpm_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'bpm' search parameter when nothing goes wrong.
    """
    search_params = {
        "bpm": 125
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "bpm": 128
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_url_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'url' search parameter when nothing goes wrong.
    """
    search_params = {
        "url": "beatport"
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "url": "youtu.be"
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try a search that will give more results
    search_params = {
        "url": "https://"
    }
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_tags_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'tags' search parameter when nothing goes wrong.
    """
    search_params = {
        "tags": ["Energetic"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "tags": ["non-existent-tag"]
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."



def test_search_songs_by_genres_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'genres' search parameter when nothing goes wrong.
    """
    search_params = {
        "genres": ["EDM"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "genres": ["Bass House"]
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_artists_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'artists' search parameter when nothing goes wrong.
    """
    search_params = {
        "artists": ["Benix"]
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting into any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    search_params = {
        "artists": ["Martin Garrix"]
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_duration_minutes_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'duration_minutes' search parameter when nothing goes wrong.
    """
    search_params = {
        "duration_minutes": 3
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "duration_minutes": 2
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."




def test_search_songs_by_duration_seconds_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our 'duration_seconds' search parameter when nothing goes wrong.
    """
    search_params = {
        "duration_minutes": 3,
        "duration_seconds": 23
    }
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try to search without getting any HTTP errors
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try another search
    search_params = {
        "duration_minutes": 2,
        "duration_seconds": 39
    }
    # try another search
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_nb_no_result():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns 0 when no Song object matches our search parameters.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return no result
    search_params = {
        "title": "High On Life"
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."

def test_search_songs_max_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the number of Song objects matching our empty search parameters when nothing goes wrong (should be the number of Song objects in the database).
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try a search that will return all Song objects
    search_params = {}
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_release_year_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the numer of Song objects matching our 'release_year' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_year
    search_params = {
        "release_year": 2021
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_year
    search_params = {
        "release_year": 2020
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."

def test_search_songs_by_release_month_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the numer of Song objects matching our 'release_month' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_month
    search_params = {
        "release_month": 12
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 2}
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_month
    search_params = {
        "release_month": 6
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."


def test_search_songs_by_release_day_nb():
    """
    Make sure that a POST at '/api/songs/search/nb':
    - returns the numer of Song objects matching our 'release_day' search parameter when nothing goes wrong.
    """
    # log in
    auth_header = get_auth_header(login_as_test(client))
    # try searching using release_day
    search_params = {
        "release_day": 10
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 1}
    assert data == expected_data, "Incorrect response format or data."
    # try searching using release_day
    search_params = {
        "release_day": 27
    }
    response = client.post("/api/songs/search/nb", headers=auth_header, json=search_params)
    assert response.status_code == 200, response.text
    data = response.json()
    expected_data = {"nb_results": 0}
    assert data == expected_data, "Incorrect response format or data."



# --------------------------------------------------------------------------
# /!\ TEST PUT /!\


put_data = {
    "new_title": "Funk"
}

def test_put_song_401_login():
    """
    Make sure that a PUT at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    global put_data
    # try to PUT without being logged in
    response = client.put("/api/artists/Julian Jordan/Diamonds", json=put_data)
    assert response.status_code == 401, response.text


def test_put_song_404_ownership():
    """
    Make sure that a PUT at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    global put_data
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.put("/api/artists/Julian Jordan/Diamonds", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_song_404_name():
    """
    Make sure that a PUT at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 404 when the 'Song' object doesn't exist in the DB.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.put("/api/artists/King Julian/non_existent_song", headers=auth_header, json=put_data)
    assert response.status_code == 404, response.text

def test_put_song_409_name_in_use():
    """
    Make sure that a PUT at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 409 when the 'new_name' attribute corresponds to an existing Song object.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to change the 'name' attribute to one that's already used
    # ==> 409 
    response = client.put("/api/artists/Dirty Palm/Legacy", headers=auth_header, json={"new_title": "Legacy"})
    assert response.status_code == 409, response.text

def test_put_song():
    """
    Make sure that a PUT at '/api/artists/{artist_name}/{song_title}':
    - returns the updated 'Song' object when nothing goes wrong.
    """
    global put_data
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT without running into any HTTP errors
    response = client.put("/api/artists/Julian Jordan/Diamonds", headers=auth_header, json=put_data)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 2,
        "title": "Funk",
        "key": "C# Minor",
        "bpm": 125,
        "url": "https://www.beatport.com/track/diamonds/16087263",
        "duration": int(timedelta(minutes=3, seconds=23).total_seconds()),
        "release_date": "2021-12-31",
        "user_id": 1,
        "tags": ["Energetic"],
        "genres": ["Bass House"],
        "artists": ["Martin Garrix", "Julian Jordan"]
    }
    assert data == expected_data, "Incorrect response format or data."



# --------------------------------------------------------------------------
# /!\ TEST DELETE /!\

def test_delete_song_401_login():
    """
    Make sure that a DELETE at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 401 when the user isn't logged in as an admin, or at all.
    """
    # try to DELETE without being logged in
    response = client.delete("/api/artists/Dirty Palm/Legacy")
    assert response.status_code == 401, response.text


def test_delete_song_404_ownership():
    """
    Make sure that a DELETE at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 404 when the user tries to access data located in another user's library.
    """
    # log in as the test1 user
    auth_header = get_auth_header(login_as_test1(client))
    response = client.delete("/api/artists/Dirty Palm/Legacy", headers=auth_header)
    assert response.status_code == 404, response.text


def test_delete_song_404():
    """
    Make sure that a DELETE at '/api/artists/{artist_name}/{song_title}':
    - returns an HTTP 404 when the 'Song' object doesn't exist in the DB.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to PUT an item that doesnt exist
    response = client.delete("/api/songs/non_existent_item", headers=auth_header)
    assert response.status_code == 404, response.text

def test_delete_song():
    """
    Make sure that a DELETE at '/api/artists/{artist_name}/{song_title}':
    - returns the deleted 'Song' object when nothing goes wrong.
    """
    # log in as the test user
    auth_header = get_auth_header(login_as_test(client))
    # try to DELETE an item without running into any HTTP errors
    response = client.delete("/api/artists/Dirty Palm/Legacy", headers=auth_header)
    assert response.status_code == 200, response.text
    # make sure the server responds with the updated data
    data = response.json()
    expected_data = {
        "id": 1,
        "title": "Legacy",
        "key": "G Major",
        "bpm": 128,
        "url": "https://youtu.be/nHn39P1bAT4",
        "duration": int(timedelta(minutes=2, seconds=39).total_seconds()),
        "release_date": "2021-12-10",
        "user_id": 1,
        "tags": ["Energetic"],
        "genres": ["EDM", "Bass House"],
        "artists": ["Dirty Palm", "Benix"]
    }
    assert data == expected_data, "Incorrect response format or data."
