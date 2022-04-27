from fastapi import FastAPI, Depends, HTTPException 
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm


# the module that handles authentication (login, registering & authenticated requests)

from .auth import *

# modules handling database operations

from . import models
from .database import engine
from .utility import *

# import our routers

from .routers import users
from .routers import tags
from .routers import genres
from .routers import artists
from .routers import songs
from .routers import playlists

# init

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# import our routers
# these take care of all the endpoints not related directly to the root of the API

app.include_router(users.router)
app.include_router(tags.router)
app.include_router(genres.router)
app.include_router(artists.router)
app.include_router(songs.router)
app.include_router(playlists.router)


# the endpoint /token will be used by the frontend to login 
# meaning a form will send username & password and receive a token in exchange
# if the provided credentials are correct

@app.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/hello/")
async def say_hello(token: str = Depends(oauth2_scheme)):
    return {"message": "Hello, World!"}


