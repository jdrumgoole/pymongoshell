#!/usr/bin/env python3
"""
MongoDBShell
===============
a module to allow more natural interaction with MongoDB via
the Python shell. Install using `pip3` (`MongoDBShell` only supports Python 3).

``$pip3 install mongodbshell``

To use just ``from mongodbshell import mongo_client``.
This will give you a prebuilt :py:class:`~MongoDBShell.Client` object.

"""

import pymongo
import pprint
import shutil
import os


class ShellError(ValueError):
    pass


if os.platform == "Windows":
    db_name_excluded_chars = r'/\. "$*<>:|?'
else:
    db_name_excluded_chars = r'/\. "$'


class Client:
    """
    Simple command line Client proxy for use in the Python shell.
    """

    def __init__(self,
                 database_name="test",
                 collection_name="test",
                 host="mongodb://localhost:27017",
                 *args,
                 **kwargs):

        """
        Creat a new client object with a default database and
        collection.

        :param database_name: The name of the database to be opened
        :param collection_name: The collection name to be opened
        :param mongodb_uri: A properly formatted MongoDB URI
        :param *args, *kwargs : Passed through to MongoClient

        >>> from mongodbshell import Client
        >>> mproxy.database = "demo"
        >>> mproxy.collection = "zipcodes"

        """
        self._mongodb_uri = host
        self._client = pymongo.MongoClient(host=self._mongodb_uri, *args, **kwargs)
        self._database_name = database_name
        self._collection_name = collection_name
        self._database = self._client[self._database_name]
        self._collection = self._database[self._collection_name]
        self._output_filename = None
        self._output_file = None

        self._line_numbers = True
        self._pretty_print = True
        self._paginate = True

        self._overlap = 0

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
        Assign to this property to set the current default database.
        :return: Return the default database object associated with the Proxy
        """
        return self._database

    @database.setter
    def database(self, database_name):
        """
        Set the default database for this Proxy object.
        :param database_name: A string naming the database
        """
        db, dot, col = database_name.partition("")

        if db:

            self._database = self.client[database_name]
        else:
            raise ShellError(f"'{database_name}' is not a valid database name")

        if col:
            self._collection = self._database[col]

    @property
    def collection(self):
        """
        Assign to `collection` to reset the current default collection.
        Return the default collection object associated with the `Proxy` object.
        """
        return self._collection

    @collection.setter
    def collection(self, collection_name):
        """
        Set the default collection for the database associated with the Proxy
        object.
        :param collection_name:
        """

        i
        self._collection = self.database[collection_name]

    def is_master(self):
        """
        Run the pymongo is_master command for the current server.
        :return: the is_master result doc.
        """
        result = self.database.command("ismaster")
        pprint.pprint(result)

    def _cursor_to_line(self, cursor):
        for i in cursor:
            yield from self.doc_to_lines(i)

    def find(self, *args, **kwargs):
        """
        Run the pymongo find command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        self.pager(self._cursor_to_line(self.collection.find(*args, **kwargs)))

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
        and returne the inserted ID.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        result = self.collection.insert_one(*args, **kwargs)
        return result.inserted_id

    def insert_many(self, *args, **kwargs):
        """
        Run the pymongo insert_many command against the default database and collection
        and return the list of inserted IDs.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        result = self.collection.insert_many(*args, **kwargs)
        return result.inserted_ids

    def delete_one(self, *args, **kwargs):
        """
        Run the pymongo delete_one command against the default database and collection
        and return the deleted IDs.
        """
        result = self.collection.delete_one(*args, **kwargs)
        return result.raw_result

    def delete_many(self, *args, **kwargs):
        """
        Run the pymongo delete_many command against the default database and collection
        and return the deleted IDs.
        """
        result = self.collection.delete_many(*args, **kwargs)
        return result.raw_result

    def count_documents(self, filter={},  *args, **kwargs):
        """
        Count all the documents in a collection accurately
        """
        result = self.collection.count_documents(filter, *args, **kwargs)
        return result

    def list_database_names(self):
        """
        List all the databases on the default server.
        """
        self.pager(self.client.list_database_names())

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

    def _get_collections(self, db_names=None):
        """
        Internal function to return all the collections for every database.
        include a list of db_names to filter the list of collections.
        """
        if db_names:
            db_list = db_names
        else:
            db_list = self.client.list_database_names()

        for db_name in db_list:
            db = self.client.get_database(db_name)
            for col_name in db.list_collection_names():
                size = db[col_name].g
                yield f"{db_name}.{col_name}"

    def list_collection_names(self, database_name):
        self.pager(self._get_collections())

    @staticmethod
    def confirm_yes(message):
        """
        Return true if user confirms yes. A correct response
        is 'y' or 'Y'. All other chars will return false.
        :param message: A string
        :return: bool.
        """
        response = input(f"{message}[ y/Y]:")
        response.upper()
        return response == "Y"

    def drop_collection(self, confirm=True):
        if confirm and self.confirm_yes(f'Drop collection:{self._database_name}.{self._collection_name}'):
            return self._collection.drop()
        else:
            return self._collection.drop()

    def drop_database(self, confirm=True):
        if confirm and self.confirm_yes(f'Drop database:{self._database_name}'):
            return self._client.drop_database(self.database)
        else:
            return self._client.drop_database(self.database)

    @property
    def overlap(self):
        """
        Get and set the line_numbers boolean
        :return: `line_numbers` (True|False)
        """
        return self._overlap

    @overlap.setter
    def overlap(self, value):
        self._overlap = value

    @property
    def line_numbers(self):
        """
        Get and set the line_numbers boolean
        :return: `line_numbers` (True|False)
        """
        return self._line_numbers

    @line_numbers.setter
    def line_numbers(self, state):
        self._line_numbers = state

    @property
    def pretty_print(self):
        """
        Get and set the pretty print boolean
        :return: `pretty_print` (True|False)
        """
        return self._pretty_print

    @pretty_print.setter
    def pretty_print(self, state):
        self._pretty_print = state

    @property
    def paginate(self):
        return self._paginate

    @paginate.setter
    def paginate(self, state):
        """
        :param state: True, turn on pagination
        :return:
        """
        self._paginate = state

    @property
    def output_file(self):
        """
        :return: The name of the output file
        """
        return self._output_filename

    @output_file.setter
    def output_file(self, filename):
        """

        :param filename: file to output `pager` output to.
        :return:
        """
        if not filename or filename == "":
            self._output_filename = None
            self._output_file = None
        else:
            self._output_filename = filename

    def pager(self, lines):
        """
        Pager is a function that outputs lines to a terminal. It uses
        `shutil.get_terminal_size` to determine the height of the terminal.
        It expects an iterator that returns a line at a time and those lines
        should be terminated by a valid newline sequence.

        Behaviour is controlled by a number of external class properties.

        `paginate` : Is on by default and triggers pagination. Without `paginate`
        all output is written straight to the screen.

        `output_file` : By assigning a name to this property we can ensure that
        all output is sent to the corresponding file. Prompts are not output.

        `pretty_print` : If this is set (default is on) then all output is
        pretty printed with `pprint`. If it is off then the output is just
        written to the screen.

        `overlap` : The number of lines to overlap between one page and the
        next.

        :param lines:
        :return:
        """
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
                    if self.paginate:
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

    def doc_to_lines(self, doc, format_func=None):
        if format_func:
            for l in format_func(doc).splitlines():
                yield l
        elif self.pretty_print:
            for l in pprint.pformat(doc).splitlines():
                yield l
        else:
            for l in str(doc).splitlines():
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
        return f"mongodbshell.Client('{self.database.name}', '{self.collection.name}', '{self.uri}')"


mongo_client = Client()
