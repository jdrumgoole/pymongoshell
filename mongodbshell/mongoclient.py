'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

#import pprint
import pymongo
import pymongo.uri_parser

from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, AutoReconnect
import pprint
import sys
from mongodbshell.pager import Pager, FileNotOpenError
from mongodbshell.version import VERSION


class ShellError(ValueError):
    pass


if sys.platform == "Windows":
    db_name_excluded_chars = r'/\. "$*<>:|?'
else:
    db_name_excluded_chars = r'/\. "$'


class MongoDBShellError(ValueError):
    pass


#
# decorator to handle exceptions
#
def handle_exceptions(func):
    def function_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TypeError as e:
            print(f"Error: {e}")
        except ServerSelectionTimeoutError as e:
            print(f"ServerSelectionTimeoutError: {e}")
        except AutoReconnect as e:
            print(f"AutoReconnect error: {e}")
    return function_wrapper


class MongoClient:
    """
    Simple command line MongoDB proxy for use in the Python shell.
    """

    def __init__(self,
                 banner=True,
                 database_name="test",
                 collection_name="test",
                 host="mongodb://localhost:27017",
                 serverSelectionTimeoutMS:int=5000,
                 *args,
                 **kwargs):

        """
        Creat a new client object with a default database and
        collection.

        :param database_name: The name of the database to be opened
        :param collection_name: The collection name to be opened
        :param mongodb_uri: A properly formatted MongoDB URI
        :param *args, *kwargs : Passed through to MongoClient

        >>> from mongodbshell import MongoClient
        >>> client = MongoClient()
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
        self._banner = banner
        self._mongodb_uri = host
        self._client = pymongo.MongoClient(host=self._mongodb_uri, serverSelectionTimeoutMS=serverSelectionTimeoutMS, *args, **kwargs)
        self._uri_dict = pymongo.uri_parser.parse_uri(self._mongodb_uri)
        '''
        {
            'nodelist': <list of (host, port) tuples>,
            'username': <username> or None,
            'password': <password> or None,
            'database': <database name> or None,
            'collection': <collection name> or None,
            'options': <dict of MongoDB URI options>,
            'fqdn': <fqdn of the MongoDB+SRV URI> or None
        }
        '''
        self._username = self._uri_dict['username']
        self._password = self._uri_dict['password']
        self._database_name = self._uri_dict['database']
        self._collection_name = self._uri_dict['collection']
        self._options = self._uri_dict['options']
        self._fqdn = self._uri_dict['fqdn']

        if self._database_name is None:
            self._database_name = database_name
        if self._collection_name is None:
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
        self._pager = Pager()

        self._overlap = 0
        if self._banner:
            self.shell_version()
            print(f"Using collection '{self.collection_name}'")
            print(f"Server selection timeout set to {serverSelectionTimeoutMS/1000} seconds")

    @staticmethod
    def shell_version():
        print(f"mongodbshell {VERSION}")

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
        if database_name and MongoClient.valid_mongodb_name(database_name):
            self._database = self.client[database_name]
        else:
            raise ShellError(f"'{database_name}' is not a valid database name")

    @property
    def database_name(self):
        """
        :return: The name of the default database
        """
        return self._database_name

    @handle_exceptions
    def _set_collection(self, name:str):
        '''
        Set a collection name. The name parameter can be a bare
        collection name or it can specify a database in the format
        "<database_name>.<collection_name>".
        :param name: The collection name
        :return: The mongodb collection object
        '''
        if "." in name:
            database_name, _, collection_name = name.partition(".")
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
        return f"{self._database_name}.{self._collection_name}"

    @collection.setter
    @handle_exceptions
    def collection(self, db_collection_name):
        """
        Set the default collection for the database associated with the `MongoDB`
        object. The user can specify a database and a collection by using a dot
        notation <database_name.collection_name>.
        :param db_collection_name: the name of the database and collection
        """

        col = self._set_collection(db_collection_name)
        # print(f"Now using collection '{self.collection_name}'")
        if self._database.list_collection_names() is None:
            print("Info: You have specified an empty collection '{db_collection_name}'")
        return col

    def is_master(self):
        """
        Run the pymongo is_master command for the current server.
        :return: the is_master result doc.
        """
        return self._pager.paginate_doc(self.database.command("ismaster"))

    def _cursor_to_line(self, cursor):
        for i in cursor:
            yield from self.dict_to_lines(i)

    @handle_exceptions
    def find(self, *args, **kwargs):
        """
        Run the pymongo find command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")

        self.print_cursor(self.collection.find(*args, **kwargs))

    @handle_exceptions
    def find_explain(self, *args, **kwargs):

        explain_doc = self.collection.find(*args, **kwargs).explain()
        self._pager.paginate_doc(explain_doc)

    @handle_exceptions
    def find_one(self, *args, **kwargs):
        """
        Run the pymongo find_one command against the default database and collection
        and paginate the output to the screen.
        """
        # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
        self._pager.paginate_doc(self.collection.find_one(*args, **kwargs))

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

    def update_one(self, *args, **kwargs):
        """
        Run the pymongo update_one against the default database and collection
        and return the upserted ID.

        :param args:
        :param kwargs:
        :return: updateResult
        """
        result = self.collection.update_one(*args, **kwargs)
        return result.modified_count

    def update_many(self, *args, **kwargs):
        """
        Run the pymongo update_many against the default database and collection
        and return the list of upserted IDs.

        :param args:
        :param kwargs:
        :return: upsertedResult.
        """

        result = self.collection.update_many(*args, **kwargs)

        return result.modified_count

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

    def count_documents(self, filter:dict=None, *args, **kwargs):
        """
        Count all the documents in a collection accurately
        """
        if filter is None:
            filter = {}
        result = self.collection.count_documents(filter, *args, **kwargs)
        return result

    def aggregate(self,pipeline, session=None, **kwargs):
        """
        Run the aggregation pipeline
        """
        self.print_cursor(self.collection.aggregate(pipeline, session, **kwargs))

    def rename(self, new_name, **kwargs):
        if not self.valid_mongodb_name(new_name):
            print( f"{new_name} cannot be used as a collection name")
            return None

        old_name = self._collection.name
        db_name = self._collection.database.name
        self._collection.rename(new_name, **kwargs)
        print(f"renamed collection '{db_name}.{old_name}' to '{db_name}.{new_name}'")

    def list_database_names(self):
        """
        List all the databases on the default server.
        """
        self._pager.paginate_lines(self.client.list_database_names())

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

        if self._collection_name in self.database.list_collection_names():
            stats = self.database.command({"collStats": self._collection_name,
                                           "scale": scale,
                                           "verbose": verbose})
            self._pager.paginate_doc(stats)
        else:
            print(f"'{self.collection_name}'is not a valid collection")

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
                yield f"{db_name}.{col_name}"

    def list_collection_names(self,database_name=None):
        if database_name:
            self._pager.paginate_lines(self._get_collections([database_name]))
        else:
            self._pager.paginate_lines(self._get_collections())

    @property
    def lcols(self):
        """
        Shorthand for list_collection_names
        """
        self.list_collection_names()

    @property
    def ldbs(self):
        """
        Shorthand for list_database_names()
        """
        self.list_database_names()

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

    def command(self, *args, **kwargs, ):
        try:
            self._pager.paginate_doc(self.database.command(*args, **kwargs))
        except OperationFailure as e:
            print(f"Error: {e}")

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
        return self.pager.pretty_print

    @pretty_print.setter
    def pretty_print(self, state):
        self._pager.pretty_print = state

    @property
    def paginate(self):
        return self._pager.paginate

    @paginate.setter
    def paginate(self, state):
        """
        :param state: True, turn on pagination
        :return:
        """
        self._pager.paginate = state

    @property
    def output_file(self):
        """
        :return: The name of the output file
        """
        return self._pager.output_file

    @output_file.setter
    def output_file(self, filename):
        """

        :param filename: file to output `pager` output to.
        :return:
        """
        self._pager.output_file = filename

    def write_file(self,s):
        try:
            self._pager.write_file(s)
        except FileNotOpenError:
            print("before writing create a file by assigning a name to 'output_file' e.g.")
            print(">> x=MongoClient()")
            print(">> x.output_file='operations.log'")
            print(">> x.write('hello')")

    def cursor_to_lines(self, cursor:pymongo.cursor, format_func=None):
        """
        Take a cursor that returns a list of docs and returns a
        generator yield each line of each doc a line at a time.
        :param cursor: A mongod cursor yielding docs (dictonaries)
        :param format_func: A customisable format function
        :return: a generator yielding a line at a time
        """
        for doc in cursor:
            yield from self._pager.dict_to_lines(doc, format_func)

    def print_cursor(self,  cursor, format_func=None):
        return self._pager.paginate_lines(self.cursor_to_lines(cursor, format_func))


    def __str__(self):
        return f"client     : '{self.uri}'\n" +\
               f"db         : '{self.database.name}'\n" +\
               f"collection : '{self.collection.name}'"

    def __repr__(self):
        return f"mongodbshell.MongoClient(banner={self._banner},\n" \
               f"                         database_name='{self._database_name}',\n" \
               f"                         collection_name='{self._collection_name}',\n" \
               f"                         host= '{self._mongodb_uri}')"


    def __del__(self):
        self._pager.close()
