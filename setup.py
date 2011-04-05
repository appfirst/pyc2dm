from distutils.core import setup
import sys

sys.path.append('pyc2dm')
import pyc2dm


setup(name='pyc2dm',
    version='0.9',
    author='Andrew Carman',
    author_email='andrew@appfirst.com',
    url='https://github.com/appfirst/pyc2dm',
    # download_url='https://sourceforge.net/projects/py-googlemaps/files/',
    description='Python client for the Android C2DM service for sending push notifications to phones.',
    long_description=pyc2dm.C2DM.__doc__,
    package_dir={'': 'pyc2dm'},
    py_modules=['pyc2dm'],
    provides=['pyc2dm'],
    keywords='android c2dm push-notification application',
    license='General Public License v3',
    classifiers=['Development Status :: 3 - Alpha',
               'Intended Audience :: Developers',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2.6',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Topic :: Internet',
               'Topic :: Internet :: WWW/HTTP',
               'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
               'Topic :: Software Development :: Libraries :: Python Modules',
              ],
    )
