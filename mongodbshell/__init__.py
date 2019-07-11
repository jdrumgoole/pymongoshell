#!/usr/bin/env python3
"""
MongoDBShell
===============

Author : joe@joedrumgoole.com

Follow me on twitter like `@jdrumgoole <https://twitter.com/jdrumgoole>`_. for
updates on this package.

`MongoDBShell <https://pypi.org/project/mongodbshell/>`_ is a module that
provides more natural interaction with MongoDB via the Python shell.
Install using `pip3` (`MongoDBShell` only supports Python 3).

``$pip3 install mongodbshell``

To use::

    >>> import mongodbshell
    >>> client = mongodbshell.MongoDB()
    >>> client.collection="test.test"
    >>> client
    mongodbshell.MongoDB('test', 'test', 'mongodb://localhost:27017')
    >>> client.insert_one({"msg" : "MongoDBShell is great"})
    ObjectId('5cb30cfa72a4ae3b105afa1c')
    >>> client.find_one()
    1    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> client.line_numbers = 0
    >>> client.find_one()
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> # note the line number is no longer present
    >>> client.output_file="output.txt" # send all output to this file
    >>> client.find_one()
    Output is also going to 'output.txt'
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>> print(open("output.txt").read(), end="")
    {'_id': ObjectId('5cb30cfa72a4ae3b105afa1c'), 'msg': 'MongoDBShell is great'}
    >>>

This will give you a prebuilt :py:class:`~MongoDBShell.MongoDB` object.

"""

import pymongo
import pprint
import shutil
import sys


class ShellError(ValueError):
    pass


if sys.platform == "Windows":
    db_name_excluded_chars = r'/\. "$*<>:|?'
else:
    db_name_excluded_chars = r'/\. "$'


class MongoDBShellError(ValueError):
    pass

class MongoDB:
    """
    Simple command line MongoDB proxy for use in the Python shell.
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

        >>> from mongodbshell import MongoDB
        >>> client = MongoDB()
        >>> client.database = "demo"
        >>> client.collection = "zipcodes"
        >>> client.collection = "demo.zipcodes"
        >>> client.collection = "db$.test"
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/Users/jdrumgoole/GIT/mongodbshell/mongodbshell/__init__.py", line 152, in collection
            else:
        mongodbshell.ShellError: 'db$' is not a valid database name
        >>>

        """
        self._mongodb_uri = host
        self._client = pymongo.MongoClient(host=self._mongodb_uri, *args, **kwargs)
        self._database_name = database_name
        self._collection_name = collection_name
        self._database = self._client[self._database_name]
        self._set_collection(collection_name)
        #
        # self._collection = self._database[self._collection_name]
        self._output_filename = None
        self._output_file = None

        self._line_numbers = True
        self._pretty_print = True
        self._paginate = True

        self._overlap = 0

    @staticmethod
    def valid_mongodb_name(name):
        """
        Check that the name for a database has no illegal
        characters
        :param name: the name of the database
        :return: True if the name is valid
        """

        for char in db_name_excluded_chars:
            if char in name:
                return None

        return name

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
        if database_name and MongoDB.valid_mongodb_name(database_name):
            self._database = self.client[database_name]
        else:
            raise ShellError(f"'{database_name}' is not a valid database name")

    @property
    def database_name(self):
        """
        :return: The name of the default database
        """
        return self._database_name

    def _set_collection(self, name):
        if "." in name:
            database_name, dot, collection_name = name.partition(".")
            if self.valid_mongodb_name(database_name):
                if self.valid_mongodb_name(collection_name):
                    self._database = self._client[database_name]
                    self._database_name = database_name
                    self._collection = self._database[collection_name]
                    self._collection_name = collection_name

                else:
                    raise ShellError(f"'{collection_name}' is not a valid collection name")
            else:
                raise ShellError(f"'{database_name}' is not a valid database name")
        else:
            if self.valid_mongodb_name(name):
                self._collection = self._database[name]
                self._collection_name = name
            else:
                raise ShellError(f"'{name}' is not a valid collection name")

        return self._collection

    @property
    def collection(self):
        """
        Assign to `collection` to reset the current default collection.
        Return the default collection object associated with the `MongoDB` object.
        """
        return self._collection

    @property
    def collection_name(self):
        """
        :return: The name of the default collection
        """
        return self._collection_name

    @collection.setter
    def collection(self, db_collection_name):
        """
        Set the default collection for the database associated with the `MongoDB`
        object. The user can specify a database and a collection by using a dot
        notation <database_name.collection_name>.
        :param db_collection_name: the name of the database and collection
        """

        col = self._set_collection(db_collection_name)
        print(col)
        return col

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
        self.print_cursor(self.collection.find(*args, **kwargs))

    def find_explain(self, *args, **kwargs):

        self.print_doc(self.collection.find(*args, **kwargs).explain()["executionStats"])

    def find_one(self, *args, **kwargs):
        """
        Run the pymongo find_one command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        self.print_doc(self.collection.find_one(*args, **kwargs))

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

    def aggregate(self,pipeline, session=None, **kwargs):
        """
        Run the aggregation pipeline
        """
        self.print_cursor(self.collection.aggregate(pipeline, session, **kwargs))

    def list_database_names(self):
        """
        List all the databases on the default server.
        """
        self.pager(self.client.list_database_names())

    def dbstats(self):
        """
        Run dbstats command for database
        See https://docs.mongodb.com/manual/reference/method/db.stats/
        """
        pprint.pprint(self.database.command("dbstats"))

    def collstats(self, scale=1024, verbose=False):
        """
        Run collection stats for collection.
        see https://docs.mongodb.com/manual/reference/command/collStats/

        :param scale: Scale at which to report sizes
        :param verbose: used for extended report on legacy MMAPV1 storage engine
        :return: JSON doc with stats
        """
        self.print_doc(self.database.command(
                            {"collStats": self._collection_name,
                             "scale": scale,
                             "verbose": verbose}))

    # def __getattr__(self, item):
    #     if hasattr(self._collection, item):
    #         return getattr(self.collection, item)
    #     else:
    #         raise MongoDBShellError(f"No such item {item} in PyMongo collection object")

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

    def list_collection_names(self,database_name=None):
        if database_name:
            self.pager(self._get_collections([database_name]))
        else:
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

    def create_index(self, name):
        self._collection.create_index(name)

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

    def paginate_doc(self, doc):
        """

        :param doc: a dictionary of data
        :return:
        """
    def pager(self, lines):
        """
        Outputs lines to a terminal. It uses
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
        :return: paginated output
        """
        try:

            line_count = 0

            if self._output_filename:
                print(f"Output is also going to '{self.output_file}'")
                self._output_file = open(self._output_filename, "a+")

            terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
            lines_left = terminal_lines
            for i, l in enumerate(lines, 1):

                line_residue = 0
                if self.line_numbers:
                    output_line = f"{i:<4} {l}"
                else:
                    output_line = l

                line_overflow = int(len(output_line) / terminal_columns)
                if line_overflow:
                    line_residue = len(output_line) % terminal_columns

                if line_overflow >= 1:
                    lines_left = lines_left - line_overflow
                else:
                    lines_left = lines_left - 1

                if line_residue > 1:
                    lines_left = lines_left - 1

                # line_count = line_count + 1

                print(output_line)

                if self._output_file:
                    self._output_file.write(f"{l}\n")
                    self._output_file.flush()

                #print(lines_left)
                if (lines_left - self.overlap - 1) <= 0:  # -1 to leave room for prompt

                    if self.paginate:
                        print("Hit Return to continue (q or quit to exit)", end="")

                        user_input = input()
                        if user_input.lower().strip() in ["q", "quit", "exit"]:
                            break

                        terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
                        lines_left = terminal_lines
            # end for

            if self._output_file:
                self._output_file.close()
        except KeyboardInterrupt:
            print("ctrl-C...")
            if self._output_file:
                self._output_file.close()

    def doc_to_lines(self, doc, format_func=None):
        """
        Generator that converts a doc to a sequence of lines.
        :param doc: A dictionary
        :param format_func: customisable formatter defaults to pformat
        :return: a generator yielding a line at a time
        """
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
        """
        Take a cursor that returns a list of docs and returns a
        generator yield each line of each doc a line at a time.
        :param cursor: A mongod cursor yielding docs (dictonaries)
        :param format_func: A customisable format function
        :return: a generator yielding a line at a time
        """
        for doc in cursor:
            yield from self.doc_to_lines(doc, format_func)

    def print_cursor(self,  cursor, format_func=None):
        return self.pager(self.cursor_to_lines(cursor, format_func))

    def print_doc(self, doc, format_func=None):
        return self.pager(self.doc_to_lines(doc, format_func))

    def __str__(self):
        return f"client     : '{self.uri}'\n" +\
               f"db         : '{self.database.name}'\n" +\
               f"collection : '{self.collection.name}'"

    def __repr__(self):
        return f"mongodbshell.MongoDB('{self.database.name}', '{self.collection.name}', '{self.uri}')"


client = MongoDB()
