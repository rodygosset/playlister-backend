# This file is used to centralize access to the Pydantic models
# Everytime a new model is created, it must be imported here

from .schema_classes.user import *
from .schema_classes.tag import *
from .schema_classes.genre import *
from .schema_classes.artist import *
from .schema_classes.song import *
from .schema_classes.playlist import *