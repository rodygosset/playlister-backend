# Dependency

from fastapi import HTTPException, status
from .database import SessionLocal

def get_db():
    """
        Used in the dependency injection system to handle database connection opening and closing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def raise_http_400(detail: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )

def raise_http_401(detail: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail
    )


def raise_http_403(detail: str):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def raise_http_404(detail: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )

def raise_http_409(detail: str):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail
    )
