"""Flickr API for Google App Engine"""
__version__ = "0.2"
        

from google.appengine.api import urlfetch
import logging
import urllib

def get_text(nodelist):
    """Helper function to pull text out of XML nodes
    """
    retval = ""
    for node in nodelist:
        #            logging.debug(node.nodeType)
        if node.nodeType == node.TEXT_NODE:
            retval = retval + node.data
    return retval

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

class GaeFlickrLibException(Exception):
    """Exception class"""
    pass

class GFLPhoto:
    """Information about a single Flickr photo"""
    def __init__(self, photo):
        self.data = {}
        #logging.debug("GFLPhoto __init__: " + photo.toxml())
        for key, value  in photo.attributes.items():
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

class GaeFlickrLib:
    """Connection to Flickr API"""
    def __init__(self, api_key=None, **p):
        if api_key is None:
            raise GaeFlickrLibException, "api_key not provided"
        else:
            self.api_key = api_key
            if 'api_secret' in p:
                self.api_secret = p['api_secret']
            else:
                self.api_secret = None
        
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


    def execute_json(self, method, auth=None, args=None):
        """Execute a Flickr method, using json response format"""

#        import json
        from django.utils import simplejson
        import re
        args = args or {}
        if auth is None:
            if self.api_secret is None:
                auth = False
            else:
                auth = True
        args['api_key'] = self.api_key
        args['method'] = method
        args['format'] = 'json'
        if auth:
            if self.api_secret is None:
                raise GaeFlickrLibException, "can't use auth without secret"
            else:
                args['api_sig'] = self.sign(args)

        url = 'http://api.flickr.com/services/rest/?'
        for key, value in args.items():
            logging.debug("args-items %s %s\n", key, value)
            url += urllib.quote(str(key)) + '=' + urllib.quote(str(value)) + '&'
        url = url.rstrip('&')
        logging.debug(url)
        resp = urlfetch.fetch(url)
        rejs = resp.content
        logging.debug(rejs)
        rejs2 = re.sub(r'^jsonFlickrApi\(', '', rejs)
        rejs = re.sub(r'\)$', '', rejs2)
        respdata = simplejson.loads(rejs)
        if respdata['stat'] == 'ok':
            return respdata['stat']
        else:
            ecode = respdata['err']['code']
            emsg = respdata['err']['emsg']
            raise GaeFlickrLibException, "API error: %s - %s" % (ecode, emsg)


    def sign (self, args):
        """returns an API sig for the arguments in args.  
        Note: if calling this manually, you must include your API key and 
        method in the args to get a valid signature.  This function is called
        automatically when needed by execute and other functions.
        """
        import hashlib
        authstring = self.api_secret
        keylist = args.keys()
        keylist.sort()
        for key in keylist:
            authstring += str(key) + str(args[key])
        hasher = hashlib.md5()
        hasher.update(authstring)
        return str(hasher.hexdigest())

    def login_url(self, perms = 'write'):
        """returns a login URL for your application. set perms to
        'read' (default), 'write', or 'delete'.
        After logging in, user will be redirected by Flickr to the URL you set
        in your API key setup.
        """
        url = 'http://flickr.com/services/auth/?'
        pieces = {}
        pieces['api_key'] = self.api_key
        pieces['perms'] = perms
        pieces['api_sig'] = self.sign(pieces)
        for key, val in pieces.items():
            url += key + '=' + val + '&'
        url = url.rstrip('&')
        return url


# activity
    def activity_userComments(self):
        """Not yet implemented"""
        raise NotImplementedError

    def activity_userPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError

# auth
    def auth_checkToken(self):
        """Not yet implemented"""
        raise NotImplementedError

    def auth_getFrob(self):
        """Not yet implemented"""
        raise NotImplementedError

    def auth_getFullToken(self):
        """Not yet implemented"""
        raise NotImplementedError

    def auth_getToken(self, frob = None):
        """implements flickr.auth.getToken API method.  
        requires a frob (sent in callback from login URL); 
        not providing one will cause ugly crash at the moment.
        """
        rsp = self.execute('flickr.auth.getToken', args = {'frob':frob})
        token = GFLToken(rsp)
        return token

    def auth_getToken_full(self, frob = None):
        """for backwards compatibility; deprecated"""
        logging.warning("""auth_getToken_full is deprecated;
        use auth_getToken instead""")
        return self.auth_getToken(frob)

# blogs
    def blogs_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def blogs_getServices(self):
        """Not yet implemented"""
        raise NotImplementedError

    def blogs_postPhoto(self):
        """Not yet implemented"""
        raise NotImplementedError

# collections


    def collections_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError

    def collections_getTree(self):
        """Not yet implemented"""
        raise NotImplementedError

# commons

    def commons_getInstitutions(self):
        """Not yet implemented"""
        raise NotImplementedError

# contacts
    def contacts_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def contacts_getListRecentlyUploaded(self):
        """Not yet implemented"""
        raise NotImplementedError

    def contacts_getPublicList(self):
        """Not yet implemented"""
        raise NotImplementedError

# favorites
    def favorites_add(self):
        """Not yet implemented"""
        raise NotImplementedError

    def favorites_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def favorites_getPublicList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def favorites_remove(self):
        """Not yet implemented"""
        raise NotImplementedError

# galleries
    def galleries_addPhoto(self):
        """Not yet implemented"""
        raise NotImplementedError

    def galleries_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def galleries_getListForPhoto(self):
        """Not yet implemented"""
        raise NotImplementedError


# groups
    def groups_browse(self):
        """Not yet implemented"""
        raise NotImplementedError

    def groups_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError

    def groups_search(self):
        """Not yet implemented"""
        raise NotImplementedError

# groups.pools
    def groups_pools_add(self):
        """Not yet implemented"""
        raise NotImplementedError

    def groups_pools_getContext(self):
        """Not yet implemented"""
        raise NotImplementedError

    def groups_pools_getGroups(self):
        """Not yet implemented"""
        raise NotImplementedError

    def groups_pools_getPhotos(self, **args):
        """get photos in a group pool"""
        if not 'group_id' in args:
            raise GaeFlickrLibException, "flickr.groups.pools.getPhotos \
            requires group_id"
        else:
            rsp = self.execute('flickr.groups.pools.getPhotos', args=args)
            plist = GFLPhotoList(rsp)
            return plist

    def groups_pools_remove(self, **args):
        """Remove a photo from a flickr group"""
        if not 'group_id' in args:
            raise GaeFlickrLibException, "flickr.groups.pools.remove requires \
            group_id"
        elif not 'photo_id' in args:
            raise GaeFlickrLibException, "flickr.groups.pools.remove requires \
            photo_id"
        else:
            rsp = self.execute('flickr.groups.pools.remove', args=args)
            return rsp


# interestingness
    def interestingness_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

# machinetags
    def machinetags_getNamespaces(self):
        """Not yet implemented"""
        raise NotImplementedError

    def machinetags_getPairs(self):
        """Not yet implemented"""
        raise NotImplementedError

    def machinetags_getPredicates(self):
        """Not yet implemented"""
        raise NotImplementedError

    def machinetags_getRecentValues(self):
        """Not yet implemented"""
        raise NotImplementedError

    def machinetags_getValues(self):
        """Not yet implemented"""
        raise NotImplementedError

# people
    def people_findByEmail(self):
        """Not yet implemented"""
        raise NotImplementedError

    def people_findByUsername(self):
        """Not yet implemented"""
        raise NotImplementedError

    def people_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError

    def people_getPhotosOf(self):
        """Not yet implemented"""
        raise NotImplementedError

    def people_getPublicGroups(self):
        """Not yet implemented"""
        raise NotImplementedError

    def people_getPublicPhotos(self, user_id = None, **args):
        """get a user's public photos"""
        if user_id is None:
            raise GaeFlickrLibException, "user_id not provided"
        else:
            args['user_id'] = user_id
#            for k, v in args.items():
#                logging.debug("%s %s\n"%(k, v))

#            rsp = self.execute_json('flickr.people.getPublicPhotos', args=args)
            rsp = self.execute('flickr.people.getPublicPhotos', args=args)
            
#            logging.debug(rsp)
            plist = GFLPhotoList(rsp)
            logging.debug(plist)
            if plist:
                return plist
            else:
                raise GaeFlickrLibException, "no photo list"

    def people_getUploadStatus(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos
    def photos_addTags(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_delete(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getAllContexts(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getContactsPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getContactsPublicPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getContext(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getCounts(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getExif(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getFavorites(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getInfo(self, **args):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getNotInSet(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getPerms(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getRecent(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getSizes(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getUntagged(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getWithGeoData(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_getWithoutGeoData(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_recentlyUpdated(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_removeTag(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_search(self, **args):
        """Search for a photo"""
        if args is None:
            raise GaeFlickrLibException, "search requires parameters"
        else:
            rsp = self.execute('flickr.photos.search', args=args)
            plist = GFLPhotoList(rsp)
            return plist


    def photos_setContentType(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_setDates(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_setMeta(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_setPerms(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_setSafetyLevel(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_setTags(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.comments(self):
    def photos_comments_addComment(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_comments_deleteComment(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_comments_editComment(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_comments_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_comments_getRecentForContacts(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.geo(self):
    def photos_geo_batchCorrectLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_correctLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_getLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_getPerms(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_photosForLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_removeLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_setContext(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_setLocation(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_geo_setPerms(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.licenses
    def photos_licenses_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photos_licenses_setLicense(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.notes
    def photos_notes_add(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photos_notes_delete(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photos_notes_edit(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.people
    def photos_people_add(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_people_delete(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_people_deleteCoords(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_people_editCoords(self):
        """Not yet implemented"""
        raise NotImplementedError

    def photos_people_getList(self):
        """Not yet implemented"""
        raise NotImplementedError


# photos.transform
    def photos_transform_rotate(self):
        """Not yet implemented"""
        raise NotImplementedError

# photos.upload
    def photos_upload_checkTickets(self):
        """Not yet implemented"""
        raise NotImplementedError

# photosets

    def photosets_addPhoto(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_create(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_delete(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_editMeta(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_editPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_getContext(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_getList(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_getPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_orderSets(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_removePhoto(self):
        """Not yet implemented"""
        raise NotImplementedError

# photosets.comments
    def photosets_comments_addComment(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_comments_deleteComment(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_comments_editComment(self):
        """Not yet implemented"""
        raise NotImplementedError
    def photosets_comments_getList(self):
        """Not yet implemented"""
        raise NotImplementedError

# places
    def places_find(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_findByLatLon(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getChildrenWithPhotosPublic(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getInfo(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getInfoByUrl(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getPlaceTypes(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getShapeHistory(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_getTopPlacesList(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_placesForBoundingBox(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_placesForContacts(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_placesForTags(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_placesForUser(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_resolvePlaceId(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_resolvePlaceURL(self):
        """Not yet implemented"""
        raise NotImplementedError
    def places_tagsForPlace(self):
        """Not yet implemented"""
        raise NotImplementedError

# prefs
    def prefs_getContentType(self):
        """Not yet implemented"""
        raise NotImplementedError
    def prefs_getGeoPerms(self):
        """Not yet implemented"""
        raise NotImplementedError
    def prefs_getHidden(self):
        """Not yet implemented"""
        raise NotImplementedError
    def prefs_getPrivacy(self):
        """Not yet implemented"""
        raise NotImplementedError
    def prefs_getSafetyLevel(self):
        """Not yet implemented"""
        raise NotImplementedError

#reflection

    def reflection_getMethodInfo(self):
        """Not yet implemented"""
        raise NotImplementedError
    def reflection_getMethods(self):
        """Not yet implemented"""
        raise NotImplementedError

#tags

    def tags_getClusterPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getClusters(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getHotList(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getListPhoto(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getListUser(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getListUserPopular(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getListUserRaw(self):
        """Not yet implemented"""
        raise NotImplementedError
    def tags_getRelated(self):
        """Not yet implemented"""
        raise NotImplementedError

#test

    def test_echo(self):
        """Not yet implemented"""
        raise NotImplementedError
    def test_login(self):
        """Not yet implemented"""
        raise NotImplementedError
    def test_null(self):
        """Not yet implemented"""
        raise NotImplementedError

#urls

    def urls_getGroup(self):
        """Not yet implemented"""
        raise NotImplementedError
    def urls_getUserPhotos(self):
        """Not yet implemented"""
        raise NotImplementedError
    def urls_getUserProfile(self):
        """Not yet implemented"""
        raise NotImplementedError
    def urls_lookupGroup(self):
        """Not yet implemented"""
        raise NotImplementedError
    def urls_lookupUser(self):
        """Not yet implemented"""
        raise NotImplementedError
