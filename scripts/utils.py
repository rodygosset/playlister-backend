

from typing import List
import requests, json
from requests import Response


SERVER_URL = "http://localhost:8000"

# a collection of useful functions


# functions used to log into the API

def login(username: str, password: str) -> Response:
    """

    Provide the API with valid admin credentials and get a token in return.

    Args:
        username (str): Account's username.
        password (str): Account's password.

    Returns:
        Response: The API response.
    """
    # try logging in with the admin account
    admin_login_data = {
        "username": username,
        "password": password
    }
    # login request...
    response = requests.post(SERVER_URL + "/token/", data=admin_login_data)
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
        raise Exception(f"Format du token incorret : {token}.")
    auth_header = {"Authorization": f"{token['token_type']} {token['access_token']}"}
    return auth_header



# useful to upload data to the API 

# /!\ JSON file has to represent an array of objects /!\


def post_json_unathenticated(json_file_path: str, url: str):
    # read the data from the JSON file
    items = []
    with open(json_file_path, "r") as data_file:
        items = json.load(data_file)
    for item in items:
        response = requests.post(url, json=item)
        assert response.status_code == 200, response.text




def post_json(json_file_path: str, url: str, username: str, password: str):
    # log in 
    auth_header = get_auth_header(login(username, password))
    # read the data from the JSON file
    items = []
    with open(json_file_path, "r") as data_file:
        items = json.load(data_file)
    for item in items:
        response = requests.post(url,
                               headers=auth_header, json=item)
        assert response.status_code == 200, response.text



def get_dict_with_key_value(arr: List[dict], key: str, value) -> int:
    for index, item in enumerate(arr):
        if key in item and item[key] == value: 
                return index
    return -1