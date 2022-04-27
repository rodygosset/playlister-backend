from ..utility import *

def search_check_boundaries(skip: int, max: int):
    """
    Make sure the values for skip and max used in a search request are valid (strictly greater than 0).

    Args:
        skip (int): The number of elements to skip in the search results.
        max (int): The maximum amount of results to send back.
    """
    if skip is not None:
        if skip < 0:
            raise_http_400(f"Cannot process request : min value cannot be negative (max={max}).")
    if max is not None:
        if max < 0:
            raise_http_400(f"Cannot process request : max value cannot be negative (max={max}).")
    