import unittest
import pymongo

from mongodbshell import mproxy, Proxy

import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestShell(unittest.TestCase):

    def test_ismaster(self):
        with captured_output() as (out, err):
            mproxy.client
            self.assertEqual(pymongo.MongoClient(),
                             mproxy.client)
            self.assertEqual("", err.getvalue())

        with captured_output() as (out, err):
            mproxy.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_find(self):

        with captured_output() as (out, err):
            atlas_proxy = Proxy(uri="mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true",
                                database_name="demo",
                                collection_name="zipcodes")

            atlas_proxy.find_one()


if __name__ == '__main__':
    unittest.main()
