"""exception handlers for GaeFlickrLibExceptions.  Each takes a
message as the argument.  If the return value is not None, it will be
used as the return value for the corresponding flickr API method. If
it is None, the exception will be re-raised."""
import logging

def checkToken(message):
    if '98' in message:
        return False
    else:
        return None
