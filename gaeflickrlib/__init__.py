"""Flickr API for Google App Engine"""
__version__ = "0.5"
        
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

#from models import *

import models

import logging
import urllib
import pickle

try:
    import gaeflconfig
    API_KEY = gaeflconfig.API_KEY
    API_SECRET = gaeflconfig.API_SECRET

except ImportError:
    logging.warn("no module gaeflconfig found in path")


METHODS = {
    'flickr.activity.userComments': [None, [], None],
    'flickr.activity.userPhotos': [None, [], None],
    'flickr.auth.checkToken': ['GFLToken', ['auth_token'], None], #needs exception handler
    'flickr.auth.getFrob': ['GFLFrob', [], None], # GFLFron not implemented yet
    'flickr.auth.getFullToken': ['GFLToken', ['mini_token'], None],
    'flickr.auth.getToken': ['GFLToken', ['frob'], None],
    'flickr.blogs.getList': [None, [], None],
    'flickr.blogs.getServices': [None, [], None],
    'flickr.blogs.postPhoto': [None, [], None],
    'flickr.collections.getInfo': [None, [], None],
    'flickr.collections.getTree': [None, [], None],
    'flickr.commons.getInstitutions': [None, [], None],
    'flickr.contacts.getList': [None, [], None],
    'flickr.contacts.getListRecentlyUploaded': [None, [], None],
    'flickr.contacts.getPublicList': [None, [], None],
    'flickr.favorites.add': [None, ['photo_id'], None],
    'flickr.favorites.getList': ['GFLPhotoList', [], None],
    'flickr.favorites.getPublicList': ['GFLPhotoList', ['user_id'], None],
    'flickr.favorites.remove': [None, ['photo_id'], None],
    'flickr.galleries.addPhoto': [None, [], None],
    'flickr.galleries.create': [None, [], None],
    'flickr.galleries.editMeta': [None, [], None],
    'flickr.galleries.editPhoto': [None, [], None],
    'flickr.galleries.editPhotos': [None, [], None],
    'flickr.galleries.getInfo': [None, [], None],
    'flickr.galleries.getList': [None, [], None],
    'flickr.galleries.getListForPhoto': [None, [], None],
    'flickr.galleries.getPhotos': [None, [], None],
    'flickr.groups.browse': [None, [], None],
    'flickr.groups.getInfo': [None, [], None],
    'flickr.groups.members.getList': [None, [], None],
    'flickr.groups.pools.add': [None, [], None],
    'flickr.groups.pools.getContext': [None, [], None],
    'flickr.groups.pools.getGroups': [None, [], None],
    'flickr.groups.pools.getPhotos': ['GFLPhotoList', ['group_id'], None],
    'flickr.groups.pools.remove': [None, ['group_id', 'photo_id'], None],
    'flickr.groups.search': [None, [], None],
    'flickr.interestingness.getList': [None, [], None],
    'flickr.machinetags.getNamespaces': [None, [], None],
    'flickr.machinetags.getPairs': [None, [], None],
    'flickr.machinetags.getPredicates': [None, [], None],
    'flickr.machinetags.getRecentValues': [None, [], None],
    'flickr.machinetags.getValues': [None, [], None],
    'flickr.panda.getList': [None, [], None],
    'flickr.panda.getPhotos': [None, [], None],
    'flickr.people.findByEmail': [None, [], None],
    'flickr.people.findByUsername': [None, [], None],
    'flickr.people.getInfo': [None, [], None],
    'flickr.people.getPhotos': ['GFLPhotoList', ['user_id'], None],
    'flickr.people.getPhotosOf': [None, [], None],
    'flickr.people.getPublicGroups': [None, [], None],
    'flickr.people.getPublicPhotos': ['GFLPhotoList', ['user_id'], None],
    'flickr.people.getUploadStatus': [None, [], None],
    'flickr.photos.addTags': [None, [], None],
    'flickr.photos.comments.addComment': [None, [], None],
    'flickr.photos.comments.deleteComment': [None, [], None],
    'flickr.photos.comments.editComment': [None, [], None],
    'flickr.photos.comments.getList': [None, [], None],
    'flickr.photos.comments.getRecentForContacts': [None, [], None],
    'flickr.photos.delete': [None, ['photo_id'], None],
    'flickr.photos.geo.batchCorrectLocation': [None, [], None],
    'flickr.photos.geo.correctLocation': [None, [], None],
    'flickr.photos.geo.getLocation': [None, [], None],
    'flickr.photos.geo.getPerms': [None, [], None],
    'flickr.photos.geo.photosForLocation': [None, [], None],
    'flickr.photos.geo.removeLocation': [None, [], None],
    'flickr.photos.geo.setContext': [None, [], None],
    'flickr.photos.geo.setLocation': [None, [], None],
    'flickr.photos.geo.setPerms': [None, [], None],
    'flickr.photos.getAllContexts': [None, [], None],
    'flickr.photos.getContactsPhotos': ['GFLPhotoList', [], None],
    'flickr.photos.getContactsPublicPhotos': ['GFLPhotoList', [], None],
    'flickr.photos.getContext': [None, [], None],
    'flickr.photos.getCounts': [None, [], None],
    'flickr.photos.getExif': [None, [], None],
    'flickr.photos.getFavorites': [None, [], None],
    'flickr.photos.getInfo': [None, [], None],
    'flickr.photos.getNotInSet': [None, [], None],
    'flickr.photos.getPerms': [None, [], None],
    'flickr.photos.getRecent': [None, [], None],
    'flickr.photos.getSizes': [None, [], None],
    'flickr.photos.getUntagged': [None, [], None],
    'flickr.photos.getWithGeoData': [None, [], None],
    'flickr.photos.getWithoutGeoData': [None, [], None],
    'flickr.photos.licenses.getInfo': [None, [], None],
    'flickr.photos.licenses.setLicense': [None, [], None],
    'flickr.photos.notes.add': [None, [], None],
    'flickr.photos.notes.delete': [None, [], None],
    'flickr.photos.notes.edit': [None, [], None],
    'flickr.photos.people.add': [None, [], None],
    'flickr.photos.people.delete': [None, [], None],
    'flickr.photos.people.deleteCoords': [None, [], None],
    'flickr.photos.people.editCoords': [None, [], None],
    'flickr.photos.people.getList': [None, [], None],
    'flickr.photos.recentlyUpdated': [None, [], None],
    'flickr.photos.removeTag': [None, [], None],
    'flickr.photos.search': ['GFLPhotoList', [], None],
    'flickr.photos.setContentType': [None, [], None],
    'flickr.photos.setDates': [None, [], None],
    'flickr.photos.setMeta': [None, [], None],
    'flickr.photos.setPerms': [None, [], None],
    'flickr.photos.setSafetyLevel': [None, [], None],
    'flickr.photos.setTags': [None, [], None],
    'flickr.photos.transform.rotate': [None, [], None],
    'flickr.photos.upload.checkTickets': [None, [], None],
    'flickr.photosets.addPhoto': [None, [], None],
    'flickr.photosets.comments.addComment': [None, [], None],
    'flickr.photosets.comments.deleteComment': [None, [], None],
    'flickr.photosets.comments.editComment': [None, [], None],
    'flickr.photosets.comments.getList': [None, [], None],
    'flickr.photosets.create': [None, [], None],
    'flickr.photosets.delete': [None, [], None],
    'flickr.photosets.editMeta': [None, [], None],
    'flickr.photosets.editPhotos': [None, [], None],
    'flickr.photosets.getContext': [None, [], None],
    'flickr.photosets.getInfo': [None, [], None],
    'flickr.photosets.getList': [None, [], None],
    'flickr.photosets.getPhotos': [None, [], None],
    'flickr.photosets.orderSets': [None, [], None],
    'flickr.photosets.removePhoto': [None, [], None],
    'flickr.places.find': [None, [], None],
    'flickr.places.findByLatLon': [None, [], None],
    'flickr.places.getChildrenWithPhotosPublic': [None, [], None],
    'flickr.places.getInfo': [None, [], None],
    'flickr.places.getInfoByUrl': [None, [], None],
    'flickr.places.getPlaceTypes': [None, [], None],
    'flickr.places.getShapeHistory': [None, [], None],
    'flickr.places.getTopPlacesList': [None, [], None],
    'flickr.places.placesForBoundingBox': [None, [], None],
    'flickr.places.placesForContacts': [None, [], None],
    'flickr.places.placesForTags': [None, [], None],
    'flickr.places.placesForUser': [None, [], None],
    'flickr.places.resolvePlaceId': [None, [], None],
    'flickr.places.resolvePlaceURL': [None, [], None],
    'flickr.places.tagsForPlace': [None, [], None],
    'flickr.prefs.getContentType': [None, [], None],
    'flickr.prefs.getGeoPerms': [None, [], None],
    'flickr.prefs.getHidden': [None, [], None],
    'flickr.prefs.getPrivacy': [None, [], None],
    'flickr.prefs.getSafetyLevel': [None, [], None],
    'flickr.reflection.getMethodInfo': [None, [], None],
    'flickr.reflection.getMethods': [None, [], None],
    'flickr.stats.getCollectionDomains': [None, [], None],
    'flickr.stats.getCollectionReferrers': [None, [], None],
    'flickr.stats.getCollectionStats': [None, [], None],
    'flickr.stats.getPhotoDomains': [None, [], None],
    'flickr.stats.getPhotoReferrers': [None, [], None],
    'flickr.stats.getPhotosetDomains': [None, [], None],
    'flickr.stats.getPhotosetReferrers': [None, [], None],
    'flickr.stats.getPhotosetStats': [None, [], None],
    'flickr.stats.getPhotoStats': [None, [], None],
    'flickr.stats.getPhotostreamDomains': [None, [], None],
    'flickr.stats.getPhotostreamReferrers': [None, [], None],
    'flickr.stats.getPhotostreamStats': [None, [], None],
    'flickr.stats.getPopularPhotos': [None, [], None],
    'flickr.stats.getTotalViews': [None, [], None],
    'flickr.tags.getClusterPhotos': [None, [], None],
    'flickr.tags.getClusters': [None, [], None],
    'flickr.tags.getHotList': [None, [], None],
    'flickr.tags.getListPhoto': [None, [], None],
    'flickr.tags.getListUser': [None, [], None],
    'flickr.tags.getListUserPopular': [None, [], None],
    'flickr.tags.getListUserRaw': [None, [], None],
    'flickr.tags.getRelated': [None, [], None],
    'flickr.test.echo': [None, [], None],
    'flickr.test.login': [None, [], None],
    'flickr.test.null': [None, [], None],
    'flickr.urls.getGroup': [None, [], None],
    'flickr.urls.getUserPhotos': [None, [], None],
    'flickr.urls.getUserProfile': [None, [], None],
    'flickr.urls.lookupGallery': [None, [], None],
    'flickr.urls.lookupGroup': [None, [], None],
    'flickr.urls.lookupUser': [None, [], None],
    }

def get_text(nodelist):
    """Helper function to pull text out of XML nodes."""
    retval = ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE]) 
    return retval


def _perm_ok(perms, req_perms):
    """check if granted perms are >= requested perms"""
    if perms in ['delete', req_perms]:
        return True
    elif perms == 'write' and req_perms == 'read':
        return True
    else:
        return False


class GaeFlickrLibException(Exception):
    """Exception class for Flickr exceptions."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class GaeMetaDispatcher(object):
    def __init__(self, method = None, flickrObj = None):
        if flickrObj is None:
            raise GaeFlickrLibException("meta dispatcher needs GaeFlickrLib object")
        if method is None:
            method = "flickr"
        self.method = method
        self.flickrObj = flickrObj
    def __getattr__(self, attr):
        newmethod = self.method + "." + attr
        return GaeMetaDispatcher(method = newmethod, flickrObj = self.flickrObj)
    def __call__(self, **kargs):
        try:
            methmeta = METHODS[self.method]
        except AttributeError:
            raise GaeFlickrLibException("unknown method %s" % self.method)
        for req_param in methmeta[1]:
            if not req_param in kargs:
                raise GaeFlickrLibException, "%s method requires \
                argument %s" % [fullmethod, req_param]
        try:
            rsp = self.flickrObj.execute(self.method,
                                         args = kargs)
        except GaeFlickrLibException, message:
            if methmeta[2] is not None:
                methmeta[2](message)
            else:
                raise
        retobj = getattr(models, methmeta[0], None)
        if retobj is not None:
            return retobj(rsp)
        else:
            return rsp

class GaeFlickrLib(object):
    """Connection to Flickr API"""
    def __init__(self, api_key=None, **p):
        if api_key or API_KEY:
            self.api_key = api_key or API_KEY
        else:
            raise GaeFlickrLibException, "api_key not provided"

        if 'api_secret' in p:
            self.api_secret = p['api_secret']
        elif API_SECRET is not None:
            self.api_secret = API_SECRET
        else:
            self.api_secret = None
        if 'token' in p:
            self.token = p['token']
        else:
            self.token = None
        
    def __getattr__(self, module):
        module =  module.replace('_', '.') # backward compatibility
        return GaeMetaDispatcher(flickrObj = self, method = "flickr." + module)

    def execute(self, method, auth=None, args=None):
        """Run a Flickr method, returns rsp element from REST response.
        defaults to using authenticated call if an api_secret was given
        when GaeFlickrLib was initialized; set auth=False to do unauth'ed call.
        Manually setting auth to true without api_secret set will raise a
        GaeFlickrLibException.
        args is a dict of arguments to the method.  See Flickr's documentation.
        """
        import xml.dom.minidom
        args = args or {}
        if auth is None:
            if self.api_secret is None:
                auth = False
            else:
                auth = True
        if not 'auth_token' in args and auth and self.token is not None:
            args['auth_token'] = self.token


        args['api_key'] = self.api_key
        args['method'] = method
        
        if auth:
            if self.api_secret is None:
                raise GaeFlickrLibException, "can't use auth without secret"
            else:
                args['api_sig'] = self.sign(args)

        url = 'http://api.flickr.com/services/rest/?'
        for key, value in args.items():
            #logging.debug("args-items %s %s\n" % (key, value))
            url += urllib.quote(str(key)) + '=' + urllib.quote(str(value)) + '&'
        url = url.rstrip('&')
        logging.debug(url)
        resp = urlfetch.fetch(url)
        #logging.debug(resp.content.decode("UTF-8"))
        dom = xml.dom.minidom.parseString(resp.content)
        rsp = dom.getElementsByTagName('rsp')[0]
        if rsp.getAttribute('stat') == 'ok':
            return rsp
        else:
            err = rsp.getElementsByTagName('err')[0]
            ecode = err.getAttribute('code')
            emsg = err.getAttribute('msg')
            raise GaeFlickrLibException, "API error: %s - %s" % (ecode, emsg)

    def sign (self, args):
        """returns an API sig for the arguments in args.  

        This method is called automatically when needed by execute()
        and other methods.
        """
        
        import hashlib
        if not 'api_key' in args and self.api_key:
            args['api_key'] = self.api_key
        authstring = self.api_secret
        keylist = args.keys()
        keylist.sort()
        for key in keylist:
            authstring += str(key) + str(args[key])
        hasher = hashlib.md5()
        hasher.update(authstring)
        return str(hasher.hexdigest())

    def login_url(self, perms = 'read'):
        """returns a login URL for your application.

        set perms to 'read' (default), 'write', or 'delete'.  After
        logging in, user will be redirected by Flickr to the URL you
        set in your API key setup.
        """
        
        url = 'http://flickr.com/services/auth/?'
        pieces = {}
        pieces['api_key'] = self.api_key
        pieces['perms'] = perms
        pieces['api_sig'] = self.sign(pieces)
        pieces2 = []
        for key, val in pieces.items():
            pieces2.append("%s=%s" % (key, val))
        url = '&'.join(pieces2)
        return url



def _authed(fun, self, perms, optional, *args, **kw):
    """FlickrAuthed helper decorator"""
    logging.debug("in FlickrAuthed decorator: perms %s fun %s self %s",
                  perms, fun, self)
    logging.debug(repr(self.request.cookies))
    if 'gaeflsid' in self.request.cookies:
        authsess = memcache.get(self.request.cookies['gaeflsid'])
        if authsess is None:
            authsessobj = FlickrAuthSession.get_by_key_name(
                self.request.cookies['gaeflsid'])
            if authsessobj is not None:
                authsess = pickle.loads(str(authsessobj.tokenobj))
        if authsess is not None and _perm_ok(authsess['perms'], perms):
            self.flickr = GaeFlickrLib(api_key=API_KEY, api_secret=API_SECRET,
                                             token = str(authsess))
            return fun(self, *args, **kw)
    if not optional:
        logging.debug("no auth session; redirecting")
        self.flickr = GaeFlickrLib(api_key=API_KEY, 
                                   api_secret=API_SECRET)
        self.response.headers["Set-Cookie"] = "gaeflretpage=%s" % self.request.url
        return self.redirect(self.flickr.login_url(perms = perms))
    else:
        self.flickr = GaeFlickrLib(api_key=API_KEY, api_secret=API_SECRET)
        return fun(self, *args, **kw)
    

def FlickrAuthed(arg=None, optional=False):
    """Decorator for webapp.RequestHandler get(), put(), etc. methods
    making method call require Flickr auth session.  To use, do:

    @FlickrAuthed
    get(self):

    (will require 'read' or better permissions)

    or

    @FlickrAuthed('write') #or 'delete' or 'read'
    get(self):

    (to use specified permissions, or better)

    You can also specify optional=True to get the existing auth session but
    continue if there isn't one.

    Your handler method will then have access to the variable "self.flickr" which is
    a GaeFlickrLib object.
    
    """
    if hasattr(arg, '__call__'): #decorator, no argument
        def _wrap(self, *args, **kw):
            return _authed(arg, self, 'read', optional, *args, **kw)
        return _wrap
    else:
        def _decorate(arg2):
            def _wrap(self, *args, **kw):
                return _authed(arg2, self, arg, optional, *args, **kw)
            return _wrap
        return _decorate
                              

class FlickrAuthCallbackHandler(webapp.RequestHandler):
    def get(self):
        from uuid import uuid1

        flickr = GaeFlickrLib(api_key=API_KEY, api_secret=API_SECRET)
        frob = self.request.get('frob')
        tokenobj = flickr.auth_getToken(frob = frob)
        sessid = str(uuid1())
        self.response.headers["Set-Cookie"] = "gaeflsid=%s" % sessid
        memcache.set(sessid, tokenobj, namespace='gaeflsid')
        pto = pickle.dumps(tokenobj)
        fas = FlickrAuthSession(tokenobj = pto, key_name = sessid)
        fas.put()

        if 'gaeflretpage' in self.request.cookies:
            self.redirect(self.request.cookies['gaeflretpage'])
        else:
            self.redirect('/')
