#!/usr/bin/env python3

import pymongo
import pprint
import shutil


class Proxy:
    """
    Simple command line proxy for use in the Python shell.
    """

    def __init__(self,
                 database_name="test",
                 collection_name="test",
                 uri="mongodb://localhost:27017"):
        """
        Creat a new client object with a default database and
        collection.

        :param database_name: The name of the database to be opened
        :param collection_name: The collection name to be opened
        :param mongodb_uri: A properly formatted MongoDB URI

        >>> from mongodbshell import mproxy
        >>> mproxy.database = "demo"
        >>> mproxy.collection = "zipcodes"

        """
        self._mongodb_uri = uri
        self._client = pymongo.MongoClient(self._mongodb_uri)
        self._database_name = database_name
        self._collection_name = collection_name
        self._database = self._client[self._database_name]
        self._collection = self._database[self._collection_name]
        self._output_filename = None
        self._output_file = None

        self._line_numbers = True
        self._overlap = 1

    # def __getattr__(self, item):
    #     if item == "find":
    #         print_cursor(self.collection.find())

    @property
    def client(self):
        """
        :return: the MongoDBClient object
        """
        return self._client

    @property
    def uri(self):
        """
        :return: The URI used to create the Proxy object
        """
        return self._mongodb_uri

    @property
    def database(self):
        """
        :return: Return the default database object associated with the Proxy
        """
        return self._database

    @database.setter
    def database(self, database_name):
        """
        Set the default database for this Proxy object.
        :param database_name: A string naming the database
        """
        self._database = self.client[database_name]

    @property
    def collection(self):
        """
        :return: Return the default collection object associated with the Proxy
        database
        """
        return self._collection

    @collection.setter
    def collection(self, collection_name):
        """
        Set the default collection for the database associated with the Proxy
        object.
        :param collection_name:
        """
        self._collection = self.database[collection_name]

    @property
    def overlap(self):
        return self._overlap

    @overlap.setter
    def overlap(self, value):
        self._overlap = value

    def is_master(self):
        """
        Run the pymongo is_master command for the current server.
        :return: the is_master result doc.
        """
        result = self.database.command("ismaster")
        pprint.pprint(result)

    def find(self, *args, **kwargs):
        """
        Run the pymongo find command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        self.pager(self.collection.find(*args, **kwargs))

    def find_one(self, *args, **kwargs):
        """
        Run the pymongo find_one command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        self.pager(self.doc_to_lines(self.collection.find_one(*args, **kwargs)))

    def insert_one(self, *args, **kwargs):
        """
        Run the pymongo insert_one command against the default database and collection
        and paginate the output to the screen
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        result = self.collection.insert_one(*args, **kwargs)
        return result.inserted_id

    def insert_many(self, *args, **kwargs):
        """
        Run the pymongo insert_many command against the default database and collection
        and paginate the output to the screen
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        result = self.collection.insert_many(*args, **kwargs)
        return result.inserted_ids

    def list_database_names(self):
        """
        List all the databases on the default server.
        """
        self.pager(self.client.list_database_names())

    def _get_collections(self):
        """
        Internal function to return colletction
        """
        for db_name in self.client.list_database_names():
            db = self.client.get_database(db_name)
            for col_name in db.list_collection_names():
                size = db[col_name].g
                yield f"{db_name}.{col_name}"

    def list_collection_names(self):
        self.pager(self._get_collections())

    @property
    def line_numbers(self):
        return self._line_numbers

    @line_numbers.setter
    def line_numbers(self, state):
        self._line_numbers = state

    def dbstats(self):
        pprint.pprint(self.database.command("dbstats"))

    def collstats(self, scale=1024, verbose=False):
        """
        see https://docs.mongodb.com/v4.0/reference/command/collStats/
        :param scale: Scale at which to report sizes
        :param verbose: used for extended report on legacy MMAPV1 storage engine
        :return: JSON doc with stats
        """
        self.pager(self.doc_to_lines(self.database.command(
            {"collStats": self._collection_name,
             "scale": scale,
             "verbose": verbose})))

    @property
    def output_file(self):
        return self._output_filename

    @output_file.setter
    def output_file(self, filename):
        if not filename or filename == "":
            self._output_filename = None
            self._output_file = None
        else:
            self._output_filename = filename

    def pager(self, lines):
        try:
            _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
            line_count = 0
            if self._output_filename:
                print(f"Output is also going to '{self.output_file}'")
                self._output_file = open(self._output_filename, "a+")

            for i, l in enumerate(lines, 1):
                if self.line_numbers:
                    print(f"{i:<4} {l}")

                else:
                    print(f"{l}")
                if self._output_file:
                    self._output_file.write(f"{l}\n")
                    self._output_file.flush()
                line_count += 1
                if line_count == terminal_lines - self.overlap - 1:
                    line_count = 0
                    print("Hit Return to continue (q or quit to exit)", end="")
                    user_input = input()
                    if user_input.lower().strip() in ["q", "quit", "exit"]:
                        break

                _, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
            if self._output_file:
                self._output_file.close()
        except KeyboardInterrupt:
            print("ctrl-C...")
            if self._output_file:
                self._output_file.close()

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

    def __str__(self):
        return f"client     : '{self.uri}'\n" +\
               f"db         : '{self.database.name}'\n" +\
               f"collection : '{self.collection.name}'"

    def __repr__(self):
        return f"Proxy('{self.database.name}', '{self.collection.name}', '{self.uri}')"


