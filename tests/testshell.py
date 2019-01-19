import unittest
import sys
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
import pymongo

from mongodbshell import mongo_client, Client


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
        mongo_client.drop_collection(confirm=False)
        mongo_client.drop_database(confirm=False)

    def tearDown(self):
        mongo_client.drop_collection(confirm=False)
        mongo_client.drop_database(confirm=False)

    def test_Client(self):
        with captured_output() as (out, err):
            self.assertEqual(pymongo.MongoClient(),
                             mongo_client.client)
            self.assertEqual("", err.getvalue())

    def test_ismaster(self):
        with captured_output() as (out, err):
            mongo_client.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_retrywrites(self):
        p = Client(retryWrites=True)
        with captured_output() as (out, err):
            p.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())

    def test_find_one(self):

        with captured_output() as (out, err):
            client = Client(database_name="demo",
                            collection_name="zipcodes")

            client.line_numbers = False
            client.find_one()
            self.assertTrue('AGAWAM' in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_find(self):
        with captured_output() as (out, err):
            client = Client(database_name="demo",
                          collection_name="zipcodes")
            client.pretty_print = False
            client.paginate = False
            client.line_numbers = False
            client.find(limit=50)
            self.assertEqual(len(out.getvalue().splitlines()), 50)
            self.assertTrue('01105' in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_insert_one(self):
        with captured_output() as (out, err):
            client = Client()
            now = datetime.utcnow()
            client.insert_one({"ts": now})
            self.assertTrue(client.collection.find_one({"ts": now}))
            client.delete_one({"ts": now})
            self.assertFalse(client.collection.find_one({"ts": now}))

    def test_insert_many(self):
        with captured_output() as (out, err):
            client = Client()
            many = [{"a": 1}, {"a": 1}, {"a": 3}]
            client.insert_many(many)
            self.assertTrue(client.collection.find_one({"a": 3}))
            client.delete_many({"a": 1})
            client.delete_one({"a": 3})
            self.assertFalse(client.collection.find_one({"a": 3}))


if __name__ == '__main__':
    unittest.main()
