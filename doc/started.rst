Getting Started
===============

There are 2 ways to create the GaeFlickrLib object, which provides the connection to the Flickr API.

You can create it yourself, manually::

    from gaeflickrlib import GaeFlickrLib

    flickr = GaeFlickrLib(api_key = 'some key', 
                          api_secret = 'some secret',
                          token = 'some user\'s credentials')
    photos = flickr.photos_search(text = '...')

where any of the parameters are option if gaeflconfig.py is provided
(otherwise, api_key is required).

Or, you can use the @FlickrAuthed decorator for your webapp request
handler methods, which will automatically handle auth sessions with
Flickr and create a ``flickr`` object for you in the method's
namespace::

    from gaeflickrlib import FlickrAuthed

    class MyHandler(webapp.RequestHandler):
        @FlickrAuthed
        def get(self):
            photos = flickr.photos_search(text = '...')

Note: this method requires the use of the
``FlickrAuthCallbackHandler`` request handler.
