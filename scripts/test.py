from utils import *


# log in 
auth_header = get_auth_header(login("rody", "playlister"))
response = requests.get(SERVER_URL + "/hello/", headers=auth_header)
print(response.json())