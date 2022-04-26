# This file is used to centralize access to CRUD operations
# Every time a new database model is added / implemented,
# Import it here

from .crud_functions.user import *
from .crud_functions.tag import *
from .crud_functions.tag_song import *
from .crud_functions.tag_playlist import *
from .crud_functions.genre import *
from .crud_functions.genre_song import *
from .crud_functions.artist import *
from .crud_functions.artist_song import *
from .crud_functions.song import *
from .crud_functions.song_playlist import *
from .crud_functions.playlist import *