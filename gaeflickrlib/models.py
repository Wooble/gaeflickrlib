from google.appengine.ext import db
import logging

class GFLToken:
    """A Flickr auth token"""

    def __init__(self, rsp):
        self.data = {}
        self.data['token'] = str(get_text(rsp.getElementsByTagName('token')[0]
                                     .childNodes))
        self.data['perms'] = str(get_text(rsp.getElementsByTagName('perms')[0]
                                     .childNodes))
        user = rsp.getElementsByTagName('user')[0]
        self.data['nsid'] = user.getAttribute('nsid')
        self.data['username'] = user.getAttribute('username')
        self.data['fullname'] = user.getAttribute('fullname')

    def __dict__(self):
        return self.data

    def __str__(self):
        return self.data['token']    

    def __getitem__(self, key):
        return self.data[key]

class GFLPhoto:
    """Information about a single Flickr photo."""

    def __init__(self, photo):
        self.data = {}
        #logging.debug("GFLPhoto __init__: " + photo.toxml())
        for key, value in photo.attributes.items():
            self.data[key] = value

    def url(self, size = None):
        """Return URL for a photo; defaults to medium size"""
        purl = 'http://farm'
        purl += self.data['farm'] + '.static.flickr.com/'
        purl += self.data['server'] + '/'
        purl += self.data['id'] + '_'
        purl += self.data['secret'] 
        if size is not None:
            purl += '_' + size
        purl += '.jpg'
        return purl

    def url_s(self):
        """Convenience method to return URL for small size photo"""
        return self.url(size = 's')

    def __getitem__(self, key):
        return self.data[key]
    

class GFLPhotoList:
    """A list of Flickr photos, as returned by many API methods"""
    def __init__(self, rsp):
        self.photos = []
        self.metadata = {}
        for attrib, val in \
                rsp.getElementsByTagName('photos')[0].attributes.items():
            self[attrib] = val 
        for photoxml in rsp.getElementsByTagName('photo'):
            photo = GFLPhoto(photoxml)
            self.photos.append(photo)
        logging.debug("GFLPhotoList __init__ length: " + str(len(self.photos)))

    def __iter__(self):
        return self.photos.__iter__()

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, data):
        self.metadata[key] = data


class FlickrAuthSession(db.Model):
    """model to store a user's auth token; key_name is
    to be set to the cookie value.
    """
    tokenobj = db.TextProperty()
    session_date = db.DateTimeProperty(auto_now_add = True)
