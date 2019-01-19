import unittest
import sys
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
import pymongo

from mongodbshell import mproxy, Proxy


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

    def setup(self):
        mproxy.drop_collection(confirm=False)
        mproxy.drop_database(confirm=False)

    def tearDown(self):
        mproxy.drop_collection(confirm=False)
        mproxy.drop_database(confirm=False)

    def test_proxy(self):
        with captured_output() as (out, err):
            mproxy.client
            self.assertEqual(pymongo.MongoClient(),
                             mproxy.client)
            self.assertEqual("", err.getvalue())

    def test_ismaster(self):
        with captured_output() as (out, err):
            mproxy.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_retrywrites(self):
        p = Proxy(retryWrites=True)
        with captured_output() as (out, err):
            p.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())

    def test_find_one(self):

        with captured_output() as (out, err):
            proxy = Proxy(database_name="demo",
                          collection_name="zipcodes")

            proxy.line_numbers = False
            proxy.find_one()
            self.assertTrue('AGAWAM' in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_find(self):
        with captured_output() as (out, err):
            proxy = Proxy(database_name="demo",
                          collection_name="zipcodes")
            proxy.pretty_print = False
            proxy.paginate = False
            proxy.line_numbers = False
            proxy.find(limit=50)
            self.assertEqual(len(out.getvalue().splitlines()), 50)
            self.assertTrue('01105' in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_insert_one(self):
        with captured_output() as (out, err):
            proxy = Proxy()
            now = datetime.utcnow()
            proxy.insert_one({"ts": now})
            self.assertTrue(proxy.collection.find_one({"ts": now}))
            proxy.delete_one({"ts": now})
            self.assertFalse(proxy.collection.find_one({"ts": now}))

    def test_insert_many(self):
        with captured_output() as (out, err):
            proxy = Proxy()
            many = [{"a": 1}, {"a": 1}, {"a": 3}]
            proxy.insert_many(many)
            self.assertTrue(proxy.collection.find_one({"a": 3}))
            proxy.delete_many({"a": 1})
            proxy.delete_one({"a": 3})
            self.assertFalse(proxy.collection.find_one({"a": 3}))
if __name__ == '__main__':
    unittest.main()
