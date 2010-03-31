Configuration 
============= 

gaeflicklib is configured in ``gaeflconfig.py``, which should be
located somewhere in your python path; in practice it should probably
be placed in the root of your App Engine application.

Presently, the only configuration options are::
 
   API_KEY = 'your API key'
   API_SECRET = 'your API secret'

filling in the API key and secret provided by Flickr when you sign up
for a key.

If gaeflickrlib cannot find a module called gaeflconfig.py, it will
issue a warning.  
