#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
README = read('README')
 
setup(
    name = "update-ip",
    version = "0.2",
    url = 'http://github.com/bkonkle/update-ip',
    license = 'BSD',
    description = "An extensible dynamic IP updater.",
    long_description = README,
    author = 'Brandon Konkle',
    author_email = 'brandon.konkle@gmail.com',
    packages = [
        'update_ip',
        'update_ip.services',
        'update_ip.ip_getters',
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
