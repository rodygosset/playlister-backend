# Playlister API

This API is the heart of the Playlister App.
It is used by the frontend of the App to manage and access data. 

## Installation

Clone this repository and use [pipenv](https://pipenv.pypa.io/en/latest/) to install the API.

```bash
pipenv install
```

## Usage

To start the API (from this folder, and assuming it is named 'backend')

```bash
pipenv shell
cd ..
uvicorn backend.main:app
```

## API documentation

This API implements [this database diagram](https://dbdiagram.io/d/6266fc5895e7f23c616dff16)  
To access the full documentation for this API, which indicates how to interact with it using HTTP requests,  
run the API locally, and go to <localhost:8000/docs>.

## Example data & DB population

This repository contains some example data, in the form of JSON files,  
which can be found in the json/ folder.  
This data can be POSTed to the API by running the following bash commands (after having started the API): 

```bash
pipenv shell
python3 scripts/db_populate.py
```