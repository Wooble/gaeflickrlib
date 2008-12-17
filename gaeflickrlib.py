from google.appengine.api import urlfetch
import exceptions
import logging

class GaeFlickrLibException(exceptions.Exception):
    def __init__(self):
        return
    def __str__(self):
        print "","GaeFlickrLib Error!"


class GaeFlickrLib:
    def __init__(self, api_key=None, **p):
        if api_key is None:
            raise GaeFlickrLibException, "api_key not provided"
        else:
            self.api_key = api_key
            if 'api_secret' in p:
                self.api_secret = p['api_secret']
            else:
                self.api_secret = None
        
    def execute(self, method, auth=None, **args):
        """Run a Flickr method, return raw XML content. 
        defaults to using authenticated call if an api_secret was given
        when GaeFlickrLib was initialized; set auth=False to do unauth'ed call.
        Manually setting auth to true without api_secret set will raise a
        GaeFlickrLibException.
        args is a dict of arguments to the method.  See Flickr's documentation.
        """
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
        for k, v in args.items():
            url += k + '=' + v + '&'
        url = url.rstrip('&')

        resp = urlfetch.fetch(url)
        return resp.content

    def sign (self, args):
        """returns an API sig for the arguments in args.  
        Note: if calling this manually, you must include your API key and 
        method in the args to get a valid signature.  This function is called
        automatically when needed by execute and other functions.
        """
        import hashlib
        authstring = self.api_secret
        kl = args.keys()
        kl.sort()
        for k in kl:
            authstring += str(k) + str(args[k])
        m = hashlib.md5()
        m.update(authstring)
        return str(m.hexdigest())

    def login_url(self, perms = 'read'):
        """returns a login URL for your application. set perms to 'read' (default),
        'write', or 'delete'.
        After logging in, user will be redirected by Flickr to the URL you set
        in your API key setup.
        """
        url = 'http://flickr.com/services/auth/?'
        pieces = {}
        pieces['api_key'] = self.api_key
        pieces['perms'] = perms
        pieces['api_sig'] = self.sign(pieces)
        for k,v in pieces.items():
            url += k + '=' + v + '&'
        url = url.rstrip('&')
        return url

    def _getText(self, nodelist):
        """Helper function to pull text out of XML nodes
        """
        rc = ""
        for node in nodelist:
            logging.debug(node.nodeType)
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

# activity
    def activity_userComments:
        raise NotImplementedError

    def activity_userPhotos:
        raise NotImplementedError

# auth
    def auth_checkToken:
        raise NotImplementedError

    def auth_getFrob:
        raise NotImplementedError

    def auth_getFullToken:
        raise NotImplementedError

    def auth_getToken(self, frob = None):
        """implements flickr.auth.getToken API method.  
        requires a frob (sent in callback from login URL); 
        not providing one will cause ugly crash at the moment.
        """
        import xml.dom.minidom
        resp = self.execute('flickr.auth.getToken', frob=frob)
        dom = xml.dom.minidom.parseString(resp)
        token = self._getText(dom.getElementsByTagName('token')[0].childNodes)
        return str(token)

# blogs
    def blogs_getList:
        raise NotImplementedError

    def blogs_postPhoto:
        raise NotImplementedError

# contacts
    def contacts_getList:
        raise NotImplementedError

    def contacts_getPublicList:
        raise NotImplementedError

# favorites
    def favorites_add:
        raise NotImplementedError

    def favorites_getList:
        raise NotImplementedError

    def favorites_getPublicList:
        raise NotImplementedError

    def favorites_remove:
        raise NotImplementedError

# groups
    def groups_browse:
        raise NotImplementedError

    def groups_getInfo:
        raise NotImplementedError

    def groups_search:
        raise NotImplementedError

# groups.pools
    def groups_pools_add:
        raise NotImplementedError

    def groups_pools_getContext:
        raise NotImplementedError

    def groups_pools_getGroups:
        raise NotImplementedError

    def groups_pools_getPhotos:
        raise NotImplementedError

    def groups_pools_remove:
        raise NotImplementedError

# interestingness
    def interestingness_getList:
        raise NotImplementedError

# machinetags
    def machinetags_getNamespaces:
        raise NotImplementedError

    def machinetags_getPairs:
        raise NotImplementedError

    def machinetags_getPredicates:
        raise NotImplementedError

    def machinetags_getValues:
        raise NotImplementedError

# people
    def people_findByEmail:
        raise NotImplementedError

    def people_findByUsername:
        raise NotImplementedError

    def people_getInfo:
        raise NotImplementedError

    def people_getPublicGroups:
        raise NotImplementedError

    def people_getPublicPhotos:
        raise NotImplementedError

    def people_getUploadStatus:
        raise NotImplementedError

# photos
    def photos_addTags:
        raise NotImplementedError

    def photos_delete:
        raise NotImplementedError
    def photos_getAllContexts:
        raise NotImplementedError

    def photos_getContactsPhotos:
        raise NotImplementedError

    def photos_getContactsPublicPhotos:
        raise NotImplementedError

    def photos_getContext:
        raise NotImplementedError

    def photos_getCounts:
        raise NotImplementedError

    def photos_getExif:
        raise NotImplementedError

    def photos_getFavorites:
        raise NotImplementedError

    def photos_getInfo:
        raise NotImplementedError

    def photos_getNotInSet:
        raise NotImplementedError

    def photos_getPerms:
        raise NotImplementedError

    def photos_getRecent:
        raise NotImplementedError

    def photos_getSizes:
        raise NotImplementedError

    def photos_getUntagged:
        raise NotImplementedError

    def photos_getWithGeoData:
        raise NotImplementedError

    def photos_getWithoutGeoData:
        raise NotImplementedError

    def photos_recentlyUpdated:
        raise NotImplementedError

    def photos_removeTag:
        raise NotImplementedError

    def photos_search:
        raise NotImplementedError

    def photos_setContentType:
        raise NotImplementedError

    def photos_setDates:
        raise NotImplementedError

    def photos_setMeta:
        raise NotImplementedError

    def photos_setPerms:
        raise NotImplementedError

    def photos_setSafetyLevel:
        raise NotImplementedError

    def photos_setTags:
        raise NotImplementedError

# photos.comments:
    def photos_comments_addComment:
        raise NotImplementedError

    def photos_comments_deleteComment:
        raise NotImplementedError

    def photos_comments_editComment:
        raise NotImplementedError

    def photos_comments_getList:
        raise NotImplementedError

# photos.geo:
    def photos_geo_batchCorrectLocation:
        raise NotImplementedError
    def photos_geo_correctLocation:
        raise NotImplementedError
    def photos_geo_getLocation:
        raise NotImplementedError
    def photos_geo_getPerms:
        raise NotImplementedError
    def photos_geo_photosForLocation:
        raise NotImplementedError
    def photos_geo_removeLocation:
        raise NotImplementedError
    def photos_geo_setContext:
        raise NotImplementedError
    def photos_geo_setLocation:
        raise NotImplementedError
    def photos_geo_setPerms:
        raise NotImplementedError

# photos.licenses
    def photos_licenses_getInfo:
        raise NotImplementedError
    def photos_licenses_setLicense:
        raise NotImplementedError

# photos.notes
    def photos_notes_add:
        raise NotImplementedError
    def photos_notes_delete:
        raise NotImplementedError
    def photos_notes_edit:
        raise NotImplementedError

# photos.transform
    def photos_transform_rotate:
        raise NotImplementedError

# photos.upload
    def photos_upload_checkTickets:
        raise NotImplementedError

# photosets

    def photosets_addPhoto:
        raise NotImplementedError
    def photosets_create:
        raise NotImplementedError
    def photosets_delete:
        raise NotImplementedError
    def photosets_editMeta:
        raise NotImplementedError
    def photosets_editPhotos:
        raise NotImplementedError
    def photosets_getContext:
        raise NotImplementedError
    def photosets_getInfo:
        raise NotImplementedError
    def photosets_getList:
        raise NotImplementedError
    def photosets_getPhotos:
        raise NotImplementedError
    def photosets_orderSets:
        raise NotImplementedError
    def photosets_removePhoto:
        raise NotImplementedError

# photosets.comments
    def photosets_comments_addComment:
        raise NotImplementedError
    def photosets_comments_deleteComment:
        raise NotImplementedError
    def photosets_comments_editComment:
        raise NotImplementedError
    def photosets_comments_getList:
        raise NotImplementedError

# places
    def places_find:
        raise NotImplementedError
    def places_findByLatLon:
        raise NotImplementedError
    def places_getChildrenWithPhotosPublic:
        raise NotImplementedError
    def places_getInfo:
        raise NotImplementedError
    def places_getInfoByUrl:
        raise NotImplementedError
    def places_getPlaceTypes:
        raise NotImplementedError
    def places_placesForBoundingBox:
        raise NotImplementedError
    def places_placesForContacts:
        raise NotImplementedError
    def places_placesForTags:
        raise NotImplementedError
    def places_placesForUser:
        raise NotImplementedError
    def places_resolvePlaceId:
        raise NotImplementedError
    def places_resolvePlaceURL:
        raise NotImplementedError

# prefs
    def prefs_getContentType:
        raise NotImplementedError
    def prefs_getGeoPerms:
        raise NotImplementedError
    def prefs_getHidden:
        raise NotImplementedError
    def prefs_getPrivacy:
        raise NotImplementedError
    def prefs_getSafetyLevel:
        raise NotImplementedError

#reflection

    def reflection_getMethodInfo:
        raise NotImplementedError
    def reflection_getMethods:
        raise NotImplementedError

#tags

    def tags_getClusterPhotos:
        raise NotImplementedError
    def tags_getClusters:
        raise NotImplementedError
    def tags_getHotList:
        raise NotImplementedError
    def tags_getListPhoto:
        raise NotImplementedError
    def tags_getListUser:
        raise NotImplementedError
    def tags_getListUserPopular:
        raise NotImplementedError
    def tags_getListUserRaw:
        raise NotImplementedError
    def tags_getRelated:
        raise NotImplementedError

#test

    def test_echo:
        raise NotImplementedError
    def test_login:
        raise NotImplementedError
    def test_null:
        raise NotImplementedError

#urls

    def urls_getGroup:
        raise NotImplementedError
    def urls_getUserPhotos:
        raise NotImplementedError
    def urls_getUserProfile:
        raise NotImplementedError
    def urls_lookupGroup:
        raise NotImplementedError
    def urls_lookupUser:
        raise NotImplementedError
