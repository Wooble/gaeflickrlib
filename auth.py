"""flickr.auth.* methods"""
from gaeflickrlib import GaeFlickrLibException

class Dispatcher(object):
    def __init__(self, flickrobj):
        self.flickrobj = flickrobj

    def __getattr__(self, method):
        methods = {'checkToken': ['GFLToken', ['auth_token']],
                   'getFrob': ['text', []],
                   'getFullToken': ['GFLToken', ['mini_token']],
                   'getToken': ['GFLToken', ['frob']]}
        if method in methods:
            def dyn_method(self, **kargs):
                methmeta = methods[method]
                fullmethod = "flickr.auth." + method
                for req_param in methmeta[1]:
                    if not req_param in kargs:
                        raise GaeFlickrLibException, "%s method requires \
                        argument %s" % [fullmethod, req_param]
                try:
                    rsp = self.flickrobj.execute(fullmethod,
                                            args = kargs)
                except GaeFlickrLibException, message:
                    if method == checkToken and str(message).find('98') != -1:
                        return False
                    else:
                        raise
                else:
                    if methmeta[0] == 'text':
                        from gaeflickrlib import get_text
                        return str(get_text(rsp.getElementsByTagName('frob')[0].childNodes))
                    elif methmeta[0] == 'GFLToken':
                        from gaeflickrlib import GFLToken
                        return GFLToken(rsp)
            return instancemethod(dyn_method, self, self.__class__)
        else:
            raise AttributeError
