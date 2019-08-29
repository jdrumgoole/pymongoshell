import unittest
import sys
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
import pymongo

from mongodbshell import client
from mongodbshell.cli import CLI, ShellError, MongoDBShellError


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
        client.drop_collection(confirm=False)
        client.drop_database(confirm=False)

    def tearDown(self):
        client.drop_collection(confirm=False)
        client.drop_database(confirm=False)

    def test_Client(self):
        with captured_output() as (out, err):
            self.assertEqual(pymongo.MongoClient(),
                             client.client)
            self.assertEqual("", err.getvalue())

    def test_ismaster(self):
        with captured_output() as (out, err):
            client.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_retrywrites(self):
        p = CLI(retryWrites=True)
        with captured_output() as (out, err):
            p.is_master()
            self.assertTrue("{'ismaster': True," in out.getvalue())

    def test_find_one(self):
        with captured_output() as (out, err):
            client = CLI(database_name="demo",
                         collection_name="zipcodes")

            client.line_numbers = False
            client.find_one()
            self.assertTrue('AGAWAM' in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_find(self):
        with captured_output() as (out, err):
            client = CLI(database_name="demo",
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
            client = CLI()
            now = datetime.utcnow()
            client.insert_one({"ts": now})
            self.assertTrue(client.collection.find_one({"ts": now}))
            client.delete_one({"ts": now})
            self.assertFalse(client.collection.find_one({"ts": now}))

    def test_insert_many(self):
        with captured_output() as (out, err):
            client = CLI()
            many = [{"a": 1}, {"a": 1}, {"a": 3}]
            client.insert_many(many)
            self.assertTrue(client.collection.find_one({"a": 3}))
            client.delete_many({"a": 1})
            client.delete_one({"a": 3})
            self.assertFalse(client.collection.find_one({"a": 3}))

    def test_aggregate(self):
        with captured_output() as (out, err):
            client = CLI()
            client.insert_many([{"a": 1}, {"a": 1}, {"a": 3}])
            doc = client.collection.find_one({"a": 3})
            client.aggregate([{"$match": {"a": 3}}])
            self.assertTrue(str(doc["_id"]) in out.getvalue())

    def test_database(self):
        client = CLI()
        client.database = "test"
        client.collection = "jdrumgoole"
        client.insert_one({"this is": "a test"})
        doc = client.collection.find_one({"this is": "a test"})

        self.assertTrue(isinstance(doc, dict))
        del doc["_id"]
        self.assertEqual(doc, {"this is": "a test"})
        client.drop_collection(confirm=False)

        client = CLI()
        client.collection = "test.jdrumgoole"
        self.assertEqual(client.collection_name, "jdrumgoole")
        self.assertEqual(client.database_name, "test")
        self.assertEqual(client.collection.name, "jdrumgoole")
        self.assertEqual(client.database.name, "test")

        client = CLI()
        client.database = "test"
        client.collection = "jdrumgoole"
        self.assertEqual(client.collection_name, "jdrumgoole")
        self.assertEqual(client.database_name, "test")
        self.assertEqual(client.collection.name, "jdrumgoole")
        self.assertEqual(client.database.name, "test")

    @staticmethod
    def set_collection(client, name):
        client.collection = name
        return client

    def test_collection_property(self):
        client = CLI()
        client.collection = "newdb.jdrumgoole"
        self.assertEqual(client.collection.name, "jdrumgoole")
        self.assertEqual(client.database.name, "newdb")
        client.collection = "test.test"
        self.assertEqual(client.collection.name, "test")
        self.assertEqual(client.database.name, "test")
        client.collection.insert_one({"this is": "a test"})
        doc = client.collection.find_one({"this is": "a test"})

        self.assertTrue(isinstance(doc, dict))
        del doc["_id"]
        self.assertEqual(doc, {"this is": "a test"})
        client.drop_collection(confirm=False)

        self.assertRaises(ShellError, TestShell.set_collection, client, "new$db.jdrumgoole")
        self.assertRaises(ShellError, TestShell.set_collection, client, "newdb.jdr$umgoole")


if __name__ == '__main__':
    unittest.main()
