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
        """Run a Flickr method, returns rsp element from REST response.
        defaults to using authenticated call if an api_secret was given
        when GaeFlickrLib was initialized; set auth=False to do unauth'ed call.
        Manually setting auth to true without api_secret set will raise a
        GaeFlickrLibException.
        args is a dict of arguments to the method.  See Flickr's documentation.
        """
        import xml.dom.minidom
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
    def activity_userComments(self):
        raise NotImplementedError

    def activity_userPhotos(self):
        raise NotImplementedError

# auth
    def auth_checkToken(self):
        raise NotImplementedError

    def auth_getFrob(self):
        raise NotImplementedError

    def auth_getFullToken(self):
        raise NotImplementedError

    def auth_getToken(self, frob = None):
        """implements flickr.auth.getToken API method.  
        requires a frob (sent in callback from login URL); 
        not providing one will cause ugly crash at the moment.
        """
#        import xml.dom.minidom
        rsp = self.execute('flickr.auth.getToken', frob=frob)
#        dom = xml.dom.minidom.parseString(resp)
        token = self._getText(rsp.getElementsByTagName('token')[0].childNodes)
        return str(token)

# blogs
    def blogs_getList(self):
        raise NotImplementedError

    def blogs_postPhoto(self):
        raise NotImplementedError

# contacts
    def contacts_getList(self):
        raise NotImplementedError

    def contacts_getPublicList(self):
        raise NotImplementedError

# favorites
    def favorites_add(self):
        raise NotImplementedError

    def favorites_getList(self):
        raise NotImplementedError

    def favorites_getPublicList(self):
        raise NotImplementedError

    def favorites_remove(self):
        raise NotImplementedError

# groups
    def groups_browse(self):
        raise NotImplementedError

    def groups_getInfo(self):
        raise NotImplementedError

    def groups_search(self):
        raise NotImplementedError

# groups.pools
    def groups_pools_add(self):
        raise NotImplementedError

    def groups_pools_getContext(self):
        raise NotImplementedError

    def groups_pools_getGroups(self):
        raise NotImplementedError

    def groups_pools_getPhotos(self):
        raise NotImplementedError

    def groups_pools_remove(self):
        raise NotImplementedError

# interestingness
    def interestingness_getList(self):
        raise NotImplementedError

# machinetags
    def machinetags_getNamespaces(self):
        raise NotImplementedError

    def machinetags_getPairs(self):
        raise NotImplementedError

    def machinetags_getPredicates(self):
        raise NotImplementedError

    def machinetags_getValues(self):
        raise NotImplementedError

# people
    def people_findByEmail(self):
        raise NotImplementedError

    def people_findByUsername(self):
        raise NotImplementedError

    def people_getInfo(self):
        raise NotImplementedError

    def people_getPublicGroups(self):
        raise NotImplementedError

    def people_getPublicPhotos(self):
        raise NotImplementedError

    def people_getUploadStatus(self):
        raise NotImplementedError

# photos
    def photos_addTags(self):
        raise NotImplementedError

    def photos_delete(self):
        raise NotImplementedError
    def photos_getAllContexts(self):
        raise NotImplementedError

    def photos_getContactsPhotos(self):
        raise NotImplementedError

    def photos_getContactsPublicPhotos(self):
        raise NotImplementedError

    def photos_getContext(self):
        raise NotImplementedError

    def photos_getCounts(self):
        raise NotImplementedError

    def photos_getExif(self):
        raise NotImplementedError

    def photos_getFavorites(self):
        raise NotImplementedError

    def photos_getInfo(self):
        raise NotImplementedError

    def photos_getNotInSet(self):
        raise NotImplementedError

    def photos_getPerms(self):
        raise NotImplementedError

    def photos_getRecent(self):
        raise NotImplementedError

    def photos_getSizes(self):
        raise NotImplementedError

    def photos_getUntagged(self):
        raise NotImplementedError

    def photos_getWithGeoData(self):
        raise NotImplementedError

    def photos_getWithoutGeoData(self):
        raise NotImplementedError

    def photos_recentlyUpdated(self):
        raise NotImplementedError

    def photos_removeTag(self):
        raise NotImplementedError

    def photos_search(self):
        raise NotImplementedError

    def photos_setContentType(self):
        raise NotImplementedError

    def photos_setDates(self):
        raise NotImplementedError

    def photos_setMeta(self):
        raise NotImplementedError

    def photos_setPerms(self):
        raise NotImplementedError

    def photos_setSafetyLevel(self):
        raise NotImplementedError

    def photos_setTags(self):
        raise NotImplementedError

# photos.comments(self):
    def photos_comments_addComment(self):
        raise NotImplementedError

    def photos_comments_deleteComment(self):
        raise NotImplementedError

    def photos_comments_editComment(self):
        raise NotImplementedError

    def photos_comments_getList(self):
        raise NotImplementedError

# photos.geo(self):
    def photos_geo_batchCorrectLocation(self):
        raise NotImplementedError
    def photos_geo_correctLocation(self):
        raise NotImplementedError
    def photos_geo_getLocation(self):
        raise NotImplementedError
    def photos_geo_getPerms(self):
        raise NotImplementedError
    def photos_geo_photosForLocation(self):
        raise NotImplementedError
    def photos_geo_removeLocation(self):
        raise NotImplementedError
    def photos_geo_setContext(self):
        raise NotImplementedError
    def photos_geo_setLocation(self):
        raise NotImplementedError
    def photos_geo_setPerms(self):
        raise NotImplementedError

# photos.licenses
    def photos_licenses_getInfo(self):
        raise NotImplementedError
    def photos_licenses_setLicense(self):
        raise NotImplementedError

# photos.notes
    def photos_notes_add(self):
        raise NotImplementedError
    def photos_notes_delete(self):
        raise NotImplementedError
    def photos_notes_edit(self):
        raise NotImplementedError

# photos.transform
    def photos_transform_rotate(self):
        raise NotImplementedError

# photos.upload
    def photos_upload_checkTickets(self):
        raise NotImplementedError

# photosets

    def photosets_addPhoto(self):
        raise NotImplementedError
    def photosets_create(self):
        raise NotImplementedError
    def photosets_delete(self):
        raise NotImplementedError
    def photosets_editMeta(self):
        raise NotImplementedError
    def photosets_editPhotos(self):
        raise NotImplementedError
    def photosets_getContext(self):
        raise NotImplementedError
    def photosets_getInfo(self):
        raise NotImplementedError
    def photosets_getList(self):
        raise NotImplementedError
    def photosets_getPhotos(self):
        raise NotImplementedError
    def photosets_orderSets(self):
        raise NotImplementedError
    def photosets_removePhoto(self):
        raise NotImplementedError

# photosets.comments
    def photosets_comments_addComment(self):
        raise NotImplementedError
    def photosets_comments_deleteComment(self):
        raise NotImplementedError
    def photosets_comments_editComment(self):
        raise NotImplementedError
    def photosets_comments_getList(self):
        raise NotImplementedError

# places
    def places_find(self):
        raise NotImplementedError
    def places_findByLatLon(self):
        raise NotImplementedError
    def places_getChildrenWithPhotosPublic(self):
        raise NotImplementedError
    def places_getInfo(self):
        raise NotImplementedError
    def places_getInfoByUrl(self):
        raise NotImplementedError
    def places_getPlaceTypes(self):
        raise NotImplementedError
    def places_placesForBoundingBox(self):
        raise NotImplementedError
    def places_placesForContacts(self):
        raise NotImplementedError
    def places_placesForTags(self):
        raise NotImplementedError
    def places_placesForUser(self):
        raise NotImplementedError
    def places_resolvePlaceId(self):
        raise NotImplementedError
    def places_resolvePlaceURL(self):
        raise NotImplementedError

# prefs
    def prefs_getContentType(self):
        raise NotImplementedError
    def prefs_getGeoPerms(self):
        raise NotImplementedError
    def prefs_getHidden(self):
        raise NotImplementedError
    def prefs_getPrivacy(self):
        raise NotImplementedError
    def prefs_getSafetyLevel(self):
        raise NotImplementedError

#reflection

    def reflection_getMethodInfo(self):
        raise NotImplementedError
    def reflection_getMethods(self):
        raise NotImplementedError

#tags

    def tags_getClusterPhotos(self):
        raise NotImplementedError
    def tags_getClusters(self):
        raise NotImplementedError
    def tags_getHotList(self):
        raise NotImplementedError
    def tags_getListPhoto(self):
        raise NotImplementedError
    def tags_getListUser(self):
        raise NotImplementedError
    def tags_getListUserPopular(self):
        raise NotImplementedError
    def tags_getListUserRaw(self):
        raise NotImplementedError
    def tags_getRelated(self):
        raise NotImplementedError

#test

    def test_echo(self):
        raise NotImplementedError
    def test_login(self):
        raise NotImplementedError
    def test_null(self):
        raise NotImplementedError

#urls

    def urls_getGroup(self):
        raise NotImplementedError
    def urls_getUserPhotos(self):
        raise NotImplementedError
    def urls_getUserProfile(self):
        raise NotImplementedError
    def urls_lookupGroup(self):
        raise NotImplementedError
    def urls_lookupUser(self):
        raise NotImplementedError
