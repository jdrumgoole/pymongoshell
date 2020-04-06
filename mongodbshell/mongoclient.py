"""
MongoClient
====================================
Create a MongoClient proxy with command line
friendly API calls.

"""

#import pprint
import pymongo
import pymongo.uri_parser

from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, \
    AutoReconnect, BulkWriteError, DuplicateKeyError
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


def print_to_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


#
# decorator to handle exceptions
#
def handle_exceptions(func):
    def function_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as e:
            print_to_err(f"Error: {e}")
        except ServerSelectionTimeoutError as e:
            print_to_err(f"ServerSelectionTimeoutError: {e}")
        except AutoReconnect as e:
            print_to_err(f"AutoReconnect error: {e}")
        except BulkWriteError as e:
            print_to_err(f"BulkWriteError: {e}")
            err_str = pprint.pformat(e)
            pprint.pprint(e.details, stream=sys.stderr)
        except DuplicateKeyError as e:
            print_to_err(f"DuplicateKeyError:")
            err_str = pprint.pformat(e.details)
            print_to_err(err_str)
        except OperationFailure as e:
            print_to_err(f"OperationsFailure: {e}")
            print_to_err(e.code)
            print_to_err(e.details)
    return function_wrapper

class ErrorReporter:
    '''
    THis class is needed so we capture the name of the class reference
    that was invalid. it is used by MongoClient.__setattr__.
    '''

    def __init__(self, name):
        self._name = name

    def error_msg(self, *args, **kwargs):
        print(f"Error: '{self._name}' is not a property or function call in"
              f"pymongo.Collection, pymongo.Database or pymongo.MongoClient")


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

        >>> import mongodbshell
        >>> c = mongodbshell.MongoClient()
        mongodbshell 1.1.0b5
        Using collection 'test.test'
        Server selection timeout set to 5.0 seconds
        >>> c
        mongodbshell.MongoClient(banner=True,
                                 database_name='test',
                                 collection_name='test',
                                 host= 'mongodb://localhost:27017')

        Access the internal MongoClient object:

        >>> c.client
        MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True, serverselectiontimeoutms=5000)
        >>>

        """

        # We use __setattr__ so that we can protect against someone mistakenly typing a field
        # wrong and the class just adding that field. For example you might want
        # to define a different collection by saying
        # >>> c=MongoClient()
        # mongodbshell 1.1.0b5
        # Using collection 'test.test'
        # Server selection timeout set to 5.0 seconds
        # >>> c.collection="demo.zipcodes"
        # Without protection you might inadvertently say
        # >>> c.collections="demo.zipcodes" # note the plural.
        # With us trapping that with __setattr__ Python would just
        # add another member to the class. The overhead of _setattr__
        # protection is we must use the extended form to add members
        # in the first place.

        object.__setattr__(self, "_banner", banner)
        object.__setattr__(self, "_mongodb_uri", host)
        client = pymongo.MongoClient(host=self._mongodb_uri, serverSelectionTimeoutMS=serverSelectionTimeoutMS, *args, **kwargs)
        object.__setattr__(self, "_client", client)
        uri_dict = pymongo.uri_parser.parse_uri(self._mongodb_uri)
        object.__setattr__(self, "_uri_dict", uri_dict)
        '''
        The dict returned by parse_uri. 
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

        object.__setattr__(self, "_username", self._uri_dict['username'])
        object.__setattr__(self, "_password", self._uri_dict['password'])
        object.__setattr__(self, "_database_name", self._uri_dict['database'])
        object.__setattr__(self, "_collection_name", self._uri_dict['collection'])
        object.__setattr__(self, "_options", self._uri_dict['options'])

        if "fqdn" in self._uri_dict: # older versions of PyMongo don't support fqdn.
            object.__setattr__(self, "_fqdn", self._uri_dict['fqdn'])
            self._fqdn = self._uri_dict['fqdn']
        else:
            object.__setattr__(self, "_fqdn", None)

        if self._database_name is None:
            self._database_name = database_name
        if self._collection_name is None:
            self._collection_name = collection_name

        object.__setattr__(self, "_database", self._client[self._database_name])
        object.__setattr__(self, "_collection", None)
        self._set_collection(collection_name)
        #
        # self._collection = self._database[self._collection_name]
        object.__setattr__(self, "_output_filename", None)
        object.__setattr__(self, "_output_file", None)
        object.__setattr__(self, "_line_numbers", True)
        object.__setattr__(self, "_paginate", True)
        object.__setattr__(self, "_pretty_print", True)
        object.__setattr__(self, "_pager", Pager(line_numbers=self._line_numbers,
                                                 pretty_print=self._pretty_print,
                                                 paginate=self._paginate))

        object.__setattr__(self, "_overlap", 0)
        self._overlap = 0

        if self._banner:
            self.shell_version()
            print(f"Using collection '{self.collection_name}'")
            print(f"Server requests set to timeout after {serverSelectionTimeoutMS/1000} seconds")

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
        return self._pager.paginate_doc(self.command("ismaster"))

    # @handle_exceptions
    # def find(self, *args, **kwargs):
    #     """
    #     Run the pymongo find command against the default database and collection
    #     and paginate the output to the screen.
    #     """
    #     # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
    #
    #     self.print_cursor(self.collection.find(*args, **kwargs))

    # @handle_exceptions
    # def find_explain(self, *args, **kwargs):
    #
    #     explain_doc = self.collection.find(*args, **kwargs).explain()
    #     self._pager.paginate_doc(explain_doc)
    #
    # @handle_exceptions
    # def find_one(self, *args, **kwargs):
    #     """
    #     Run the pymongo find_one command against the default database and collection
    #     and paginate the output to the screen.
    #     """
    #     # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
    #     self._pager.paginate_doc(self.collection.find_one(*args, **kwargs))

    # @handle_exceptions
    # def insert_one(self, *args, **kwargs):
    #     """
    #     Run the pymongo insert_one command against the default database and collection
    #     and returne the inserted ID.
    #     """
    #     # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
    #     result = self.collection.insert_one(*args, **kwargs)
    #     print(f"Inserted Id: {result.inserted_id} acknowledged: {result.acknowledged}")
    #
    # @handle_exceptions
    # def insert_many(self, *args, **kwargs):
    #     """
    #     Run the pymongo insert_many command against the default database and collection
    #     and return the list of inserted IDs.
    #     """
    #     # print(f"database.collection: '{self.database.name}.{self.collection.name}'")
    #     result = self.collection.insert_many(*args, **kwargs)
    #     self._pager.paginate_lines(pprint.pformat(result.inserted_ids).splitlines())
    #
    # def update_one(self, *args, **kwargs):
    #     """
    #     Run the pymongo update_one against the default database and collection
    #     and return the upserted ID.
    #
    #     :param args:
    #     :param kwargs:
    #     :return: updateResult
    #     """
    #     result = self.collection.update_one(*args, **kwargs)
    #     return result
    #
    # def update_many(self, *args, **kwargs):
    #     """
    #     Run the pymongo update_many against the default database and collection
    #     and return the list of upserted IDs.
    #
    #     :param args:
    #     :param kwargs:
    #     :return: upsertedResult.
    #     """
    #
    #     result = self.collection.update_many(*args, **kwargs)
    #
    #     return result
    #
    # def delete_one(self, *args, **kwargs):
    #     """
    #     Run the pymongo delete_one command against the default database and collection
    #     and return the deleted IDs.
    #     """
    #     result = self.collection.delete_one(*args, **kwargs)
    #     return result
    # def delete_many(self, *args, **kwargs):
    #     """
    #     Run the pymongo delete_many command against the default database and collection
    #     and return the deleted IDs.
    #     """
    #     result = self.collection.delete_many(*args, **kwargs)
    #     return result
    #
    # def count_documents(self, filter:dict=None, *args, **kwargs):
    #     """
    #     Count all the documents in a collection accurately
    #     """
    #     if filter is None:
    #         filter = {}
    #     result = self.collection.count_documents(filter, *args, **kwargs)
    #     return result
    #
    # def aggregate(self,pipeline, session=None, **kwargs):
    #     """
    #     Run the aggregation pipeline
    #     """
    #     self.print_cursor(self.collection.aggregate(pipeline, session, **kwargs))

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

    def coll_stats(self, scale=1024, verbose=False):
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
        self._pager.line_numbers = state


    @property
    def pretty_print(self):
        """
        Get and set the pretty print boolean

        :return: `pretty_print` (True|False)
        """
        return self._pager.pretty_print

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
        :param format_func: A customisable format function, expects and returns a doc
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


    @staticmethod
    def has_attr(col, name):
        '''
        Can't use the built in hasattr to check if name is a member
        of a collection object as built hasattr uses getattr and in
        the Collection object getattr is overwritten to allow collections
        to be generated by specifying col.<name>.

        :param col: a pymongo.Collection object
        :param name: a candidate name
        :return: the specified object or None
        '''

        if name in dir(col):
            return getattr(col, name)
        else:
            return None


    def __getattr__(self, name, *args, **kwargs):
        '''
        Call __getattr__ if we specify members that don't exist. The
        goal here is to pass any function not directly implemented
        by this class straight up to pymongo.Collection.

        Here we intercept the function lookup invoked of the
        mongodbshell.MongoClient object and use it to invoke the
        pymongo.Collection class directly. The nested inner function
        is required to capture the parameters correctly.

        :param name: the method or property that doesn't exist.
        :param args: args passed in by invoker
        :param kwargs: kwargs passed in by invoker
        :return: Results of call target method
        '''
        if MongoClient.has_attr(self.collection, name):
            attr = getattr(self.collection, name)
        elif MongoClient.has_attr(self.database, name):
            attr = getattr(self.database, name)
        elif MongoClient.has_attr(self.client, name):
            attr = getattr(self.client, name)
        else:
            reporter = ErrorReporter(name)
            attr = reporter.error_msg

        def make_invoker(invoker):
            @handle_exceptions
            def inner_func(*args, **kwargs):
                result = invoker(*args, **kwargs)
                if type(result) in [pymongo.command_cursor.CommandCursor, pymongo.cursor.Cursor]:
                    self.print_cursor(result)
                elif type(result) is dict:
                    self._pager.paginate_doc(result)
                else:
                    return result
            return inner_func

        if callable(attr):
            #print(f"{attr} is callable")
            return make_invoker(attr)
        else:
            print(f"returning {attr}")
            return attr

    def __setattr__(self, name, value):
        '''
        We override __setattr__ to allow us to assign objects that already
        exist. This stops someone creating arbitrary class members.
        :param name:
        :param value:
        :return:
        '''
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            print("Cannot set name '{name}'on object of type '{self.__class__.__name__}'")

    def __del__(self):
        self._pager.close()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
