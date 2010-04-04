"""flickr.favorites.* methods"""
from gaeflickrlib import GaeFlickrLibException
import new

class Dispatcher(object):
    def __init__(self, flickrobj):
        self.flickrobj = flickrobj

    def __getattr__(self, method):
        methods = {'add': [None, ['photo_id']],
                   'getList': ['GFLPhotoList', []],
                   'getPublicList': ['GFLPhotoList', ['user_id']],
                   'remove': [None, ['photo_id']]}
                   
        if method in methods:
            def dyn_method(self, **kargs):
                methmeta = methods[method]
                fullmethod = "flickr.auth." + method
                for req_param in methmeta[1]:
                    if not req_param in kargs:
                        raise GaeFlickrLibException, "%s method requires \
                        argument %s" % [fullmethod, req_param]
                rsp = self.flickrobj.execute(fullmethod,
                                             args = kargs)
                if methmeta[0] == None:
                    return True
                elif methmeta[0] == 'GFLPhotoList':
                    from gaeflickrlib import GFLPhotoList
                    return GFLPhotoList(rsp)
            return new.instancemethod(dyn_method, self, self.__class__)
        else:
            raise AttributeError
