'''
Created on 30 Sep 2016

@author: jdrumgoole
'''
from setuptools import setup
import os

pyfiles = [ f for f in os.listdir( "." ) if f.endswith( ".py" ) ]

def readme():
    with open('README.md') as f:
        return f.read()
    
setup(
    name = "mongodb_utils",
    version = "0.1",
    
    author = "Joe Drumgoole",
    author_email = "joe@joedrumgoole.com",
    description = "MongoDB Utils",
    long_description = readme(),
    license = "AGPL",
    keywords = "Meetup MUGS MongoDB API",
    url = "https://github.com/jdrumgoole/MUGAlyser",
    
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',


        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7' ],
   
    install_requires = [ "pymongo", "nose" ],
       
    packages = [ "mongodb_utils"],
    
    scripts  = [],

    test_suite='nose.collector',
    tests_require=['nose'],
)