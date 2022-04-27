import re
from typing import List
from sqlalchemy.orm import Session

from ..utility import raise_http_400

from .. import models, crud

# this file is used simply to privide tools used in our crud functions

# for a provided Song object, return its full title
# formatted as such --> '<artist> - <song_title>'

def get_full_song_title(db: Session, song: models.Song) -> str:
    return f"{crud.get_song_artists(db, song)[0]} - {song.title}"


# The following function verifies that the string given as an argument
# matches the following format --> '<artist> - <song_title>'

def is_song_title_formatted_correctly(full_song_title: str) -> bool:
    if re.match(r"^[^-]+ - [^-]+$", full_song_title):
        return True
    else: 
        return False

def unpack_full_song_title(full_song_title: str) -> List[str]:
    if not is_song_title_formatted_correctly(full_song_title):
        raise_http_400(f"'{full_song_title}' is not a valid song title.")
    return full_song_title.split(' - ')
    