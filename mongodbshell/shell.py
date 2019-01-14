#!/usr/bin/env python3

import pymongo
import pprint
import shutil


class Client:
    """
    Simple command line proxy for use in the Python shell.
    """

    def __init__(self,
                 database_name="test",
                 collection_name="test",
                 mongodb_uri="mongodb://localhost:27017"):
        self.mongodb_uri = mongodb_uri
        self.client = pymongo.MongoClient(mongodb_uri)
        self.database_name = database_name
        self.collection_name = collection_name
        self.database = database_name
        self.collection = collection_name

        self._line_numbers = True
        self._overlap = 1

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

    @property
    def overlap(self):
        return self._overlap

    @overlap.setter
    def overlap(self, value):
        self._overlap = value

    @collection.setter
    def collection(self, value):
        self._collection = self.database[value]

    def is_master(self):
        result = self.database.command("ismaster")
        pprint.pprint(result)
        return result

    def find(self, *args, **kwargs):
        print(f"database.collection: '{self.database_name}.{self.collection_name}'")
        self.print_cursor(self.collection.find(*args, **kwargs))

    def list_database_names(self):
        self.pager(self.client.list_database_names())

    def list_collection_names(self):
        self.pager(self.database.list_collection_names())

    def list_databases(self):
        self.print_cursor(self.client.list_databases(),
                          format_func=lambda l: l["name"])

    def __str__(self):
        return f"client     : {self.mongodb_uri}\n" +\
               f"db         : '{self.database.name}'\n" +\
               f"collection : '{self.collection.name}'\n"

    def __repr__(self):
        return f"Proxy('{self.database.name}', '{self.collection.name}', '{self.mongodb_uri}')"

    @property
    def line_numbers(self):
        return self._line_numbers

    @line_numbers.setter
    def line_numbers(self, state):
        self._line_numbers = state

    def pager(self, lines):
        try:
            _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
            line_count = 0
            for i, l in enumerate(lines, 1):
                if self.line_numbers:
                    print(f"{i}. {l}")
                else:
                    print(f"{l}")
                line_count += 1
                if line_count == terminal_lines - self.overlap - 1:
                    line_count = 0
                    print("Hit Return to continue (q or quit to exit)", end="")
                    user_input = input()
                    if user_input.lower().strip() in ["q", "quit", "exit"]:
                        break

                _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
        except KeyboardInterrupt:
            pass

        @staticmethod
        def doc_format(doc):
            pprint.pformat(doc)

    @staticmethod
    def doc_to_lines(doc, format_func=None):
        if format_func:
            for l in format_func(doc).splitlines():
                yield l
        else:
            for l in pprint.pformat(doc).splitlines():
                yield l

    def cursor_to_lines(self, cursor, format_func=None):
        for doc in cursor:
            yield from self.doc_to_lines(doc, format_func)

    def print_cursor(self,  cursor, format_func=None):
        return self.pager(self.cursor_to_lines(cursor, format_func))

