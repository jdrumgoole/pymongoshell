import unittest
import sys
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
import pymongo

from pymongoshell.mongoclient import MongoClient

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
        with captured_output() as (out, err):
            self._c = MongoClient(banner=False)
            self._c.collection = "testshell.test"

    def tearDown(self):
        with captured_output() as (out, err):
            self._c.drop_collection(confirm=False)

    def test_Client(self):
        with captured_output() as (out, err):
            c = MongoClient(banner=False)
        self.assertEqual("", err.getvalue())

    def test_ismaster(self):
        with captured_output() as (out, err):
            self._c.is_master()
        self.assertEqual("", err.getvalue(), err.getvalue())
        self.assertTrue("'ismaster': True," in out.getvalue(), out.getvalue())


    def test_retrywrites(self):
        with captured_output() as (out, err):
            self._c.is_master()
        self.assertTrue("'ismaster': True," in out.getvalue(), out.getvalue())


    def test_find_one(self):
        with captured_output() as (out, err):
            c = MongoClient(banner=False, host="mongodb+srv://readonly:readonly@demodata.rgl39.mongodb.net/test?retryWrites=true&w=majority")
            c.collection = "demo.zipcodes"

        self.assertTrue("zipcodes" in c.database.list_collection_names())
        with captured_output() as (out, err):
            c.line_numbers = False
            c.find_one()

        self.assertTrue('PALMER' in out.getvalue())
        self.assertEqual("", err.getvalue())

    def test_find(self):
        with captured_output() as (out, err):
            c = MongoClient(banner=False, host="mongodb+srv://readonly:readonly@demodata.rgl39.mongodb.net/test?retryWrites=true&w=majority")
            c.collection = "demo.zipcodes"
            c.pretty_print = False
            c.paginate = False
            c.line_numbers = False
            c.find(limit=50)

        #print(out.getvalue())
        self.assertEqual(len(out.getvalue().splitlines()), 51) # error line
        self.assertTrue('01069' in out.getvalue())
        self.assertTrue('01970' in out.getvalue())
        self.assertEqual("", err.getvalue())

    def test_line_numbers(self):
        with captured_output() as (out, err):
            c = MongoClient(banner=False, host="mongodb+srv://readonly:readonly@demodata.rgl39.mongodb.net/test?retryWrites=true&w=majority")
            c.collection = "demo.zipcodes"
            c.pretty_print = False
            c.paginate = False
            c.line_numbers = False
            c.find(limit=2)

        for i in out.getvalue().splitlines()[1:]:
            # print(i)
            self.assertTrue(i.startswith("{"))

        with captured_output() as (out, err):
            c.line_numbers = True
            c.find(limit=2)

        counter = 0
        for i in out.getvalue().splitlines():
            # print(i)
            counter = counter + 1
            self.assertTrue(i.startswith(str(counter)))

    def test_insert_one(self):
        with captured_output() as (out, err):
            now = datetime.utcnow()
            self._c.insert_one({"ts": now})
            doc = self._c.collection.find_one({"ts": now})
            self.assertTrue(self._c.collection.find_one({"ts": now}))
            id_str = str(doc["_id"])
        self.assertTrue(id_str in out.getvalue(), out.getvalue())
        self.assertTrue("Inserted:" in out.getvalue(), out.getvalue())

        with captured_output() as (out, err):
            self._c.insert_one(doc)
        self.assertTrue("DuplicateKeyError" in err.getvalue(), err.getvalue())
        self._c.drop_collection(confirm=False)

    def test_insert_many(self):
        with captured_output() as (out, err):
            many = [{"a": 1}, {"a": 1}, {"a": 3}]
            self._c.insert_many(many)
            self.assertTrue(self._c.collection.find_one({"a": 3}))
            self._c.delete_many({"a": 1})
            self._c.delete_one({"a": 3})
            self.assertFalse(self._c.collection.find_one({"a": 3}))
        self._c.drop_collection(confirm=False)

    def test_update_one(self):

        with captured_output() as (out, err):
            self._c.insert_many( [{"a": 1}, {"a": 1}, {"a": 3}])
            orig_doc = self._c.collection.find_one({"a":1})
            self._c.update_one( {"a":1}, {"$inc" : {"a" :1}})
            mod_doc = self._c.collection.find_one({"a":2})
            self.assertEqual(orig_doc["_id"],mod_doc["_id"])
        self.assertTrue("'nModified': 1" in out.getvalue())
        self._c.drop_collection(confirm=False)

    def test_update_many(self):
        with captured_output() as (out, err):
            self._c.collection.insert_many( [{"a": 1}, {"a": 1}, {"a": 3}])
            orig_doc = self._c.collection.find_one({"a":1})
            modified_count = self._c.update_many( {"a":1}, {"$inc" : {"a" :1}})
            mod_docs = list(self._c.collection.find({"a":2}))
            self.assertEqual(orig_doc["_id"],mod_docs[0]["_id"])
            self.assertTrue("'nModified': 2" in out.getvalue())
        self._c.drop_collection(confirm=False)

    def test_aggregate(self):
        with captured_output() as (out, err):
            self._c.insert_many([{"a": 1}, {"a": 1}, {"a": 3}])
            doc = self._c.collection.find_one({"a": 3})
            self._c.aggregate([{"$match": {"a": 3}}])
            self.assertTrue(str(doc["_id"]) in out.getvalue())
        self._c.drop_collection(confirm=False)

    def test_drop_database(self):
        with captured_output() as (out, err):
            self._c.collection = "dropme.test"
            self._c.insert_one({"dummy":"data"})
            self._c.drop_database(confirm=False)

        self.assertTrue("dropped database: 'dropme'" in out.getvalue())

    def test_database_collection_assign(self):
        client = MongoClient(banner=False)
        with captured_output() as (out, err):
            client.collection = "test.jdrumgoole"
        self.assertEqual(client.collection_name, "test.jdrumgoole")
        self.assertEqual(client.database_name, "test")
        client.drop_collection(confirm=False)


    @staticmethod
    def set_collection(client, name):
        client.collection = name
        return client

    def test_exceptions(self):
        with captured_output() as (out, err):
            self._c.collection = "new$db.jdrumgoole"
        self.assertTrue("MongoDBShellError: 'new$db' is not a valid database name" in err.getvalue(), err.getvalue())
        with captured_output() as (out, err):
            self._c.collection = "newdb.jdr$umgoole"
        self.assertTrue( "MongoDBShellError: 'jdr$umgoole' is not a valid collection name" in err.getvalue(), err.getvalue())

    def test_database_url(self):
        with captured_output() as (out, err):
            c=MongoClient(host="mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19")
            #c.collection="statistics"
            c.collection="covid19.statistics"
        self.assertEqual(c.database_name, "covid19")
        self.assertEqual(c.collection_name, "covid19.statistics")

    def test_output(self):
        with captured_output() as (out, err):
            c = MongoClient(banner=False, host="mongodb+srv://readonly:readonly@demodata.rgl39.mongodb.net/test?retryWrites=true&w=majority")
            c.collection = "demo.zipcodes"
            c.output_file = "test_output.txt"
            c.paginate=False
            c.find(limit=10)
if __name__ == '__main__':
    unittest.main()
