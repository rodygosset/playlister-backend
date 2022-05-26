# Populate the database through API POST requests
# with the data found in the json files,
# located in the /code/app/json/ directory

# /!\ this script must run from the root of the project /!\
# --> must be executed from ../

from utils import *

# post all our JSON data in the correct order

post_json_unathenticated("/code/app/json/users.json", SERVER_URL + "/api/users/")

users = json.load(open('/code/app/json/users.json'))

for user in users:
    post_json("/code/app/json/tags.json", SERVER_URL + "/api/tags/", user["username"], user["hashed_password"])
    post_json("/code/app/json/genres.json", SERVER_URL + "/api/genres/", user["username"], user["hashed_password"])
    post_json("/code/app/json/artists.json", SERVER_URL + "/api/artists/", user["username"], user["hashed_password"])
    post_json("/code/app/json/songs.json", SERVER_URL + "/api/songs/", user["username"], user["hashed_password"])