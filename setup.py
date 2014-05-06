try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='gaeflickrlib',
      version='0.6',
      packages=['gaeflickrlib'],
      author='Geoffrey Spear',
      author_email='geoffspear@gmail.com',
      url='http://www.geoffreyspear.com/gaeflickrlib/index.html',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      description='Flickr API kit for Google App Engine',
      keywords=['flickr', 'google-app-engine', 'gae', 'appengine'],
      install_requires=['oauth2'],
      test_suite='gaeflickrlib.test',
      )
