import os
from distutils.core import setup
 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
README = read('README.rst')
 
setup(
    name = "update-ip",
    version = "0.1",
    url = 'http://github.com/bkonkle/update_ip',
    license = 'BSD',
    description = "An extensible dynamic IP updater.",
    long_description = README,
    author = 'Brandon Konkle',
    author_email = 'brandon.konkle@gmail.com',
    packages = [
        'update_ip',
        'update_ip.services',
    ],
    scripts=['update_ip/update-ip'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ]
)
