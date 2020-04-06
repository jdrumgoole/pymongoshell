import unittest
import sys
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
import pymongo


from mongodbshell.mongoclient import MongoClient, ShellError


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

    def setUp(self):
        self._client = MongoClient(banner=False)


    def tearDown(self):
        pass

    def test_Client(self):
        with captured_output() as (out, err):
            self.assertEqual(pymongo.MongoClient(),
                             self._client.client)
            self.assertEqual("", err.getvalue())

    def test_ismaster(self):
        with captured_output() as (out, err):
            self._client.is_master()
            self.assertTrue("'ismaster': True," in out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_retrywrites(self):
        p = MongoClient(banner=False, retryWrites=True)
        with captured_output() as (out, err):
            p.is_master()
            self.assertTrue("'ismaster': True," in out.getvalue())

    def test_find_one(self):
        client = MongoClient(banner=False,
                             database_name="demo",
                             collection_name="zipcodes")
        if "zipcodes" in client.client["demo"].list_collection_names():
            with captured_output() as (out, err):
                client.line_numbers = False
                client.find_one()

            self.assertTrue('AGAWAM' in out.getvalue())
            self.assertEqual("", err.getvalue())
        else:
            print("Test ignored: Download zipcodes database by run make get_zipcode_data")

    def test_find(self):
        client = MongoClient(banner=False,
                             database_name="demo",
                             collection_name="zipcodes")
        with captured_output() as (out, err):
            client.pretty_print = False
            client.paginate = False
            client.line_numbers = False
            client.paginate = False
            client.pretty_print =False
            client.find(limit=50)
        self.assertEqual(len(out.getvalue().splitlines()), 50)
        self.assertTrue('01105' in out.getvalue())
        self.assertEqual("", err.getvalue())

    def test_insert_one(self):
        with captured_output() as (out, err):
            now = datetime.utcnow()
            self._client.insert_one({"ts": now})
            doc = self._client.collection.find_one({"ts": now})
            self.assertTrue(self._client.collection.find_one({"ts": now}))
            id_str = str(doc["_id"])
        self.assertTrue(id_str in out.getvalue())
        self.assertTrue("True" in out.getvalue())

        with captured_output() as (out, err):
            self._client.insert_one(doc)
        self.assertTrue("DuplicateKeyError" in err.getvalue(), err.getvalue())
        self._client.drop_collection(confirm=False)

    def test_insert_many(self):
        with captured_output() as (out, err):
            many = [{"a": 1}, {"a": 1}, {"a": 3}]
            self._client.insert_many(many)
            self.assertTrue(self._client.collection.find_one({"a": 3}))
            self._client.delete_many({"a": 1})
            self._client.delete_one({"a": 3})
            self.assertFalse(self._client.collection.find_one({"a": 3}))
        self._client.drop_collection(confirm=False)

    def test_update_one(self):

        with captured_output() as (out, err):
            self._client.collection.insert_many( [{"a": 1}, {"a": 1}, {"a": 3}])
            orig_doc = self._client.collection.find_one({"a":1})
            modified_count = self._client.update_one( {"a":1}, {"$inc" : {"a" :1}})
            mod_doc = self._client.collection.find_one({"a":2})
            self.assertEqual(orig_doc["_id"],mod_doc["_id"])
            self.assertEqual(modified_count, 1)
        self._client.drop_collection(confirm=False)

    def test_update_many(self):

        with captured_output() as (out, err):
            self._client.collection.insert_many( [{"a": 1}, {"a": 1}, {"a": 3}])
            orig_doc = self._client.collection.find_one({"a":1})
            modified_count = self._client.update_many( {"a":1}, {"$inc" : {"a" :1}})
            mod_docs = list(self._client.collection.find({"a":2}))
            self.assertEqual(orig_doc["_id"],mod_docs[0]["_id"])
            self.assertEqual(modified_count, 2)
        self._client.drop_collection(confirm=False)

    def test_aggregate(self):
        with captured_output() as (out, err):
            self._client.insert_many([{"a": 1}, {"a": 1}, {"a": 3}])
            doc = self._client.collection.find_one({"a": 3})
            self._client.aggregate([{"$match": {"a": 3}}])
            self.assertTrue(str(doc["_id"]) in out.getvalue())
        self._client.drop_collection(confirm=False)

    def test_database(self):
        client = MongoClient(banner=False)
        client.database = "test"
        client.collection = "jdrumgoole"
        client.insert_one({"this is": "a test"})
        doc = client.collection.find_one({"this is": "a test"})

        self.assertTrue(isinstance(doc, dict))
        del doc["_id"]
        self.assertEqual(doc, {"this is": "a test"})
        client.drop_collection(confirm=False)

        client = MongoClient(banner=False)
        client.collection = "test.jdrumgoole"
        self.assertEqual(client.collection_name, "test.jdrumgoole")
        self.assertEqual(client.database_name, "test")
        client.drop_collection(confirm=False)

        client = MongoClient(banner=False)
        client.database = "test"
        client.collection = "test.jdrumgoole"
        self.assertEqual(client.collection_name, "test.jdrumgoole")
        self.assertEqual(client.database_name, "test")
        self.assertEqual(client.collection.name, "jdrumgoole") #note its .name
        self.assertEqual(client.database.name, "test")
        client.drop_database(confirm=False)

    @staticmethod
    def set_collection(client, name):
        client.collection = name
        return client

    def test_collection_property(self):
        client = MongoClient(banner=False)
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

        client.drop_database(confirm=False)

    def test_getattr(self):
        ascending = self._client.ASCENDING
        print(ascending)

if __name__ == '__main__':
    unittest.main()
