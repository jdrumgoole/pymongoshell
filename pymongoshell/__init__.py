#!/usr/bin/env python3
"""
MongoDBShell
===============
`MongoDBShell <https://pypi.org/project/mongodbshell/>`_ is a module that
provides more natural interaction with MongoDB via the Python shell.
Install using `pip3` (`MongoDBShell` only supports Python 3).

``$pip3 install mongodbshell``

To use::

    >>> import pymongoshell
    >>> client = pymongoshell.MongoClient() # assumes a local mongod running on port 27017
    >>> client
    mongodbshell.MongoDB('test', 'test', 'mongodb://localhost:27017')
    >>> client.insert_one({"msg" : "MongoDBShell is great"})
    ObjectId('5cb30cfa72a4ae3b105afa1c')
    >>> client.find_one()
    1    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> client.line_numbers = 0
    >>> client.find_one()
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> # note the line number is no longer present
    >>> client.output_file="output.txt" # send all output to this file
    >>> client.find_one()
    Output is also going to 'output.txt'
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> print(open("output.txt").read(), end="")
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>>

This will give you a prebuilt :py:class:`~MongoDBShell.MongoClient` object.

Author : joe@joedrumgoole.com

Follow me on twitter `@jdrumgoole <https://twitter.com/jdrumgoole>`_. for
updates on this package.
"""

from pymongoshell.mongoclient import MongoClient
