#!/usr/bin/env python3
import pymongo
import pprint
import shutil
import code
import argparse


class MongoDBClient(object):
    """
    Simple command line proxy for use in the Python shell.
    """

    def __init__(self,
                 database_name="test",
                 collection_name="test",
                 mongodb_uri="mongodb://localhost:27017"):
        self.mongodb_uri = mongodb_uri
        self.client = pymongo.MongoClient(mongodb_uri)
        self.database = database_name
        self.collection = collection_name

    # def __getattr__(self, item):
    #     if item == "find":
    #         print_cursor(self.collection.find())

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, value):
        self._database = self.client[value]

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = self.database[value]

    def is_master(self):
        pprint.pprint(self.database.command("ismaster"))

    def find(self, *args, **kwargs):
        print_cursor(self.collection.find(*args, **kwargs))

    def list_database_names(self):
        pager(self.client.list_database_names())

    def list_collection_names(self):
        pager(self.database.list_collection_names())

    def list_databases(self):
        print_cursor(self.client.list_databases(),
                     format_func=lambda l: l["name"])

    def __str__(self):
        return f"client     : {self.mongodb_uri}\n" +\
               f"db         : '{self.database.name}'\n" +\
               f"collection : '{self.collection.name}'\n"

    def __repr__(self):
        return f"Proxy('{self.database.name}', '{self.collection.name}', '{self.mongodb_uri}')"


def pager(lines, overlap=1):
    try:
        _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
        line_count = 0
        for i, l in enumerate(lines, 1):
            print(l)
            line_count += 1
            if line_count == terminal_lines - overlap - 1:
                line_count = 0
                print("Hit Return to continue (q or quit to exit)", end="")
                user_input = input()
                if user_input.lower().strip() in ["q", "quit", "exit"]:
                    break

            _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
    except KeyboardInterrupt:
        pass


def doc_format(doc):
    pprint.pformat(doc)


def doc_to_lines(doc, format_func=None):
    if format_func:
        for l in format_func(doc).splitlines():
            yield l
    else:
        for l in pprint.pformat(doc).splitlines():
            yield l


def cursor_to_lines(cursor, format_func=None):
    for doc in cursor:
        yield from doc_to_lines(doc, format_func)


def print_cursor(cursor, overlap=3, format_func=None):
    return pager(cursor_to_lines(cursor, format_func), overlap)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--uri", default="mongodb://localhost:27017/MUGS",
                        help="URI for connecting to MongoDB, [default: %(default)s]")
    parser.add_argument("--database",
                        default="test",
                        help="Database to connect to, default: %(default)s]")
    parser.add_argument("--collection",
                        default="test",
                        help="collection to connect to, default: %(default)s]")

    args = parser.parse_args()
    proxy = MongoDBClient(database_name=args.database,
                          collection_name=args.collection,
                          mongodb_uri=args.uri)
    client = proxy.client
    db = proxy.database
    collection = proxy.collection
    find = proxy.find


    banner = ('\n'
              'The MongoDB Python Shell, use the \'proxy\' object as a wrapper for the client.\n'
              'We also have wrapper objects for the follow objects:\n'
              '\n'
              'client      : proxy.client\n'
              'database    : proxy.database\n'
              'collection  : proxy.collection\n'
              'find        : proxy.find\n'
              '    ')
    print(banner)
    print(proxy)
