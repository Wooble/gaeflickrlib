API Reference
=============

This page documents the currently-implemented Flickr API methods
available through gaeflickrlib.  Presently, a tiny minority of
Flickr's API has been implemented.  This documentation is also
incomplete; for complete details on any method see Flickr's
documentation.

.. class:: GaeFlickrLib

   .. method:: auth_checkToken(auth_token)

      Checks the validity of a Flickr auth token.  ``auth_token`` can
      be either a string containing the token or a ``GFLToken``
      object; in either case the methods returns ``False`` if the
      token is invalid, or a ``GFLToken`` object if it is valid.

   .. method:: auth_getFrob()

      Request a frob for desktop authentication.  Returns the frob as
      a string.  This method is probably not very useful within App
      Engine, but may be used from the remote_api_shell for testing.

   .. method:: auth_getToken_full

   .. method:: favorites_getList

   .. method:: groups_pools_getPhotos

   .. method:: groups_pools_remove

   .. method:: people_getPhotos

   .. method:: people_getPublicPhotos

   .. method:: photos_delete

   .. method:: photos_getContactsPhotos

   .. method:: photos_getContactsPublicPhotos

   .. method:: photos_search

   .. method:: 
