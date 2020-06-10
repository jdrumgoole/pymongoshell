"""
MongoClient
====================================
Create a MongoClient proxy with command line
friendly API calls.

"""

# import pprint
import pymongo
import pymongo.uri_parser

import pprint
import sys
from pymongoshell.pager import Pager, FileNotOpenError
from pymongoshell.version import VERSION

from pymongoshell.errorhandling import handle_exceptions, MongoDBShellError, CollectionNotSetError

if sys.platform == "Windows":
    db_name_excluded_chars = r'/\. "$*<>:|?'
else:
    db_name_excluded_chars = r'/\. "$'


class HandleResults:

    def __init__(self, pager: Pager):
        self._pager = Pager()

    def is_result_type(self, result):
        return type(result) in [pymongo.results.InsertOneResult,
                                pymongo.results.InsertManyResult,
                                pymongo.results.UpdateResult,
                                pymongo.results.DeleteResult,
                                pymongo.results.BulkWriteResult
                                ]

    def handle(self, result):
        """
        result is a pymongo result Type.
        """
        if type(result) is pymongo.results.InsertOneResult:
            self.handle_InsertOneResult(result)
        elif type(result) is pymongo.results.InsertManyResult:
            self.handle_InsertManyResult(result)
        elif type(result) is pymongo.results.UpdateResult:
            self.handle_UpdateResult(result)
        elif type(result) is pymongo.results.DeleteResult:
            self.handle_DeleteResult(result)
        elif type(result) is pymongo.results.BulkWriteResult:
            self.handle_BulkWriteResult(result)
        else:
            raise TypeError(result)

    def handle_InsertOneResult(self, result: pymongo.results.InsertOneResult):
        print(f"Inserted: {result.inserted_id}")

    def handle_InsertManyResult(self, result: pymongo.results.InsertManyResult):
        doc = pprint.pformat(result.inserted_ids)
        self._pager.paginate_lines(doc.splitlines())

    def handle_UpdateResult(self, result: pymongo.results.UpdateResult):
        self._pager.paginate_doc(result.raw_result)

    def handle_DeleteResult(self, result: pymongo.results.DeleteResult):
        self._pager.paginate_doc(result.raw_result)

    def handle_BulkWriteResult(self, result: pymongo.results.BulkWriteResult):
        doc = pprint.pformat(result.bulk_api_result)
        self._pager.paginate_doc(doc)


class MongoClient:
    """
    Simple command line MongoDB proxy for use in the Python shell.
    """

    def __init__(self,
                 banner: str = True,
                 host: str = "mongodb://localhost:27017",
                 serverSelectionTimeoutMS: int = 5000,
                 *args: object,
                 **kwargs: object) -> object:

        """
        Creat a new client object with a default database and
        collection.

        :param database_name: The name of the database to be opened
        :param collection_name: The collection name to be opened
        :param mongodb_uri: A properly formatted MongoDB URI
        :param *args, *kwargs : Passed through to MongoClient

        >>> import pymongoshell
        >>> c = pymongoshell.MongoClient()
        pymongoshell 1.1.0b7
        Server requests set to timeout after 5.0 seconds
        >>> c
        pymongoshell.MongoClient(banner=True,
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
        # pymongoshell 1.1.0b5
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
        client = pymongo.MongoClient(host=self._mongodb_uri, serverSelectionTimeoutMS=serverSelectionTimeoutMS, *args,
                                     **kwargs)
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

        if "fqdn" in self._uri_dict:  # older versions of PyMongo don't support fqdn.
            object.__setattr__(self, "_fqdn", self._uri_dict['fqdn'])
            self._fqdn = self._uri_dict['fqdn']
        else:
            object.__setattr__(self, "_fqdn", None)

        # # if we don't parse a database out of the URL lets see if we got one
        # # from the __init__ parameters.
        # if self._database_name is None:
        #     self._database_name = database_name
        # if self._collection_name is None:
        #     self._collection_name = collection_name

        object.__setattr__(self, "_collection", None)
        object.__setattr__(self, "_database", None)

        object.__setattr__(self, "_result", None)

        if self._database_name:
            object.__setattr__(self, "_database", self._client[self._database_name])
        else:
            self._database_name = "test"
            self._database = self._client[self._database_name]

        if self._collection_name:
            self._set_collection(self._collection_name)
        else:
            self._set_collection("test")
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

        object.__setattr__(self, "_handle_result", HandleResults(self._pager))
        object.__setattr__(self, "_overlap", 0)
        self._overlap = 0

        if self._banner:
            self.shell_version()
            if not self._collection_name:
                print(f"Please set a default collection by assigning one to .collection")
            print(f"Server requests set to timeout after {serverSelectionTimeoutMS / 1000} seconds")

    @staticmethod
    def shell_version():
        print(f"pymongoshell {VERSION}")

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
            raise MongoDBShellError(f"'{database_name}' is not a valid database name")

    @property
    def database_name(self):
        """
        :return: The name of the default database
        """
        return self._database_name

    def parse_full_name(self, name):
        """
        Take in a name in potential x.y format. Validate that the components
        are valid database and/or collection names
        :param name: A collection name in bare format or db_name.col_name format
        :return: database_name, collection_name
        """
        if "." in name:
            collection_name: str
            database_name: str
            database_name, _, collection_name = name.partition(".")
            if self.valid_mongodb_name(database_name):
                self._database_name = database_name
                if self.valid_mongodb_name(collection_name):
                    self._collection_name = collection_name
                    return self._database_name, self._collection_name
                else:
                    raise MongoDBShellError(f"'{collection_name}' is not a valid collection name")
            else:
                raise MongoDBShellError(f"'{database_name}' is not a valid database name")
        else:
            if self.valid_mongodb_name(name):
                self._collection_name = name
                return self._database_name, self._collection_name
            else:
                raise MongoDBShellError(f"'{name}' is not a valid collection name")

    # @handle_exceptions("_set_collection")
    def _set_collection(self, name: str):
        '''
        Set a collection name. The name parameter can be a bare
        collection name or it can specify a database in the format
        "<database_name>.<collection_name>".
        :param name: The collection name
        :return: The mongodb collection object
        '''

        self._database_name, self._collection_name = self.parse_full_name(name)
        self._database = self._client[self._database_name]
        self._collection = self._database[self._collection_name]
        return self._collection

    @property
    def collection(self):
        """
        Assign to `collection` to reset the current default collection.
        Return the default collection object associated with the `MongoDB` object.
        """
        if self._collection:
            return self._collection
        else:
            return None

    @property
    def collection_name(self):
        """
        :return: The name of the default collection
        """
        if self._database_name is None:
            return ""
        elif self._collection_name is None:
            return f"{self._database_name}"
        else:
            return f"{self._database_name}.{self._collection_name}"

    @collection.setter
    @handle_exceptions("collection.setter")
    def collection(self, db_collection_name):
        """
        Set the default collection for the database associated with the `MongoDB`
        object. The user can specify a database and a collection by using a dot
        notation <database_name.collection_name>.
        :param db_collection_name: the name of the database and collection
        """

        self._set_collection(db_collection_name)
        print(f"Now using collection '{self.collection_name}'")
        if self._database.list_collection_names() is None:
            print("Info: You have specified an empty database '{self._database}'")
        return self

    @handle_exceptions("is_master")
    def is_master(self):
        """
        Run the pymongo is_master command for the current server.
        :return: the is_master result doc.
        """
        return self._pager.paginate_doc(self._database.command("ismaster"))

    def count_documents(self, filter=None, *args, **kwargs):
        filter_arg = filter or {}
        return self.collection.count_documents(filter=filter_arg, *args, *kwargs)


    def rename(self, new_name, **kwargs):
        if not self.valid_mongodb_name(new_name):
            print(f"{new_name} cannot be used as a collection name")
            return None

        old_name = self._collection.name
        db_name = self._collection.database.name
        self._collection.rename(new_name, **kwargs)
        print(f"renamed collection '{db_name}.{old_name}' to '{db_name}.{new_name}'")

    def command(self, cmd):
        result = self._database.command(cmd)
        self._pager.paginate_doc(result)

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

    def list_collection_names(self, database_name=None):
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
        response = input(f"{message} [y/Y]: ")
        response.upper()
        return response == "Y"

    # def command(self, *args, **kwargs, ):
    #     try:
    #         self._pager.paginate_doc(self.database.command(*args, **kwargs))
    #     except OperationFailure as e:
    #         print(f"Error: {e}")

    # def create_index(self, name):
    #     name = self._collection.create_index(name)
    #     print(f"Created index: '{name}'")

    @handle_exceptions("drop_collections")
    def drop_collection(self, confirm=True):
        if confirm and self.confirm_yes(f"Drop collection: '{self._database_name}.{self._collection_name}'"):
            return self._collection.drop()
        else:
            return self._collection.drop()

    def drop_database(self, confirm=True):
        if confirm and self.confirm_yes(f"Drop database: '{self._database_name}'"):
            result = self._client.drop_database(self.database)
        else:
            result = self._client.drop_database(self.database)
        print(f"dropped database: '{self._database_name}'")

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
        self._line_numbers = state

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

    def write_file(self, s):
        try:
            self._pager.write_file(s)
        except FileNotOpenError:
            print("before writing create a file by assigning a name to 'output_file' e.g.")
            print(">> x=MongoClient()")
            print(">> x.output_file='operations.log'")
            print(">> x.write('hello')")

    def __str__(self):
        if self._client:
            client_str = f"'{self.uri}'"
        else:
            client_str = "No client created"

        if self._database_name:
            db_str = f"'{self.database_name}'"
        else:
            db_str = "no database set"

        if self._collection_name:
            col_str = f"'{self.collection_name}'"
        else:
            col_str = "no client set"

        return f"client     : {client_str}\n" + \
               f"db         : {db_str}\n" + \
               f"collection : {col_str}"

    def __repr__(self):
        return f"pymongoshell.MongoClient(banner={self._banner},\n" \
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

    def process_result(self, result):
        if result is None:
            print("None")
        elif type(result) in [pymongo.command_cursor.CommandCursor, pymongo.cursor.Cursor]:
            self._pager.print_cursor(result)
        elif self._handle_result.is_result_type(result):
            self._handle_result.handle(result)
        elif type(result) is dict:
            self._pager.paginate_doc(result)
        elif type(result) is list:
            self._pager.paginate_list(result)
        else:
            print(result)

        self._result = result

    @property
    def result(self):
        return self._result

    def interceptor(self, func):
        @handle_exceptions(func.__name__)
        def inner_func(*args, **kwargs):
            inner_func.__name__ = func.__name__
            # print(f"{func.__name__}({args}, {kwargs})")
            result = func(*args, **kwargs)
            self.process_result(result)
        inner_func.__name__ = func.__name__
        # print(f"inner_func.__name__ : {inner_func.__name__}")
        return inner_func


    def __getattr__(self, item):
        if self._collection is None:
            return self._set_collection(item)
        else:
            db_name, col_name = self.parse_full_name(item)
            # print(f"item:{item}")
            # print(f"col_name:{col_name}")
            func = self.has_attr(self._collection, col_name)
            if callable(func):
                return self.interceptor(func)
            else:
                self._collection = self._set_collection(item)
                return self

    # #@handle_exceptions("__get_attr__")
    # def __getattr__(self, name, *args, **kwargs):
    #     '''
    #     Call __getattr__ if we specify members that don't exist. The
    #     goal here is to pass any function not directly implemented
    #     by this class straight up to pymongo.Collection.
    #
    #     Here we intercept the function lookup invoked of the
    #     pymongoshell.MongoClient object and use it to invoke the
    #     pymongo.Collection class directly. The nested inner function
    #     is required to capture the parameters correctly.
    #
    #     :param name: the method or property that doesn't exist.
    #     :param args: args passed in by invoker
    #     :param kwargs: kwargs passed in by invoker
    #     :return: Results of call target method
    #     '''
    #
    #     if self._collection is None:
    #         raise CollectionNotSetError
    #     col_op = MongoClient.has_attr(self._collection, name)
    #     print(f"has_attr result: {col_op}")
    #     if col_op is None:
    #         if self.valid_mongodb_name(name):
    #             self._collection = self.collection.__getattr__(name)
    #             self._collection_name = name
    #             print(f"Setting default database and collection to: {self.collection_name}")
    #         else:
    #             return MongoClient.error(f"'{name}' is not a valid argument")
    #     else:
    #         def make_invoker(invoker):
    #             if callable(invoker):
    #                 #@handle_exceptions(col_op.__name__)
    #                 def inner_func(*args, **kwargs):
    #                     inner_func.__name__ = invoker.__name__
    #                     print(f"{invoker.__name__}({args}, {kwargs})")
    #                     result = invoker(*args, **kwargs)
    #                     if type(result) in [pymongo.command_cursor.CommandCursor, pymongo.cursor.Cursor]:
    #                         self._pager.print_cursor(result)
    #                     elif self._handle_result.is_type(result):
    #                         self._handle_result.handle(result)
    #                     elif type(result) is dict:
    #                         self._pager.paginate_doc(result)
    #
    #                     else:
    #                         # (f"type result: {type(result)}")
    #                         # print(f"result: {result}")
    #                         return result
    #
    #                 inner_func.__name__ = invoker.__name__
    #                 print(f"inner_func.__name__ : {inner_func.__name__}")
    #                 return inner_func
    #             else:
    #                 return invoker
    #
    #         # print(f"make_invoker.__name__ : {make_invoker.__name__}")
    #         return make_invoker(col_op)

    # def __setattr__(self, name, value):
    #     '''
    #     We override __setattr__ to allow us to assign objects that already
    #     exist. This stops someone creating arbitrary class members. We only
    #     users to reference existing fields for the purposes of assignment.
    #     :param name:
    #     :param value:
    #     :return:
    #     '''
    #     if hasattr(self, name):
    #         object.__setattr__(self, name, value)
    #     else:
    #         print("Cannot set name '{name}'on object of type '{self.__class__.__name__}'")

    def __del__(self):
        self._pager.close()

    def __getitem__(self, name):
        self._set_collection(name)
        return self

    def __call__(self, *args, **kwargs):
        """This is only here so that some API misusages are easier to debug.
        """
        raise TypeError("'Collection' object is not callable. If you meant to "
                        "call the '%s' method on a 'Collection' object it is "
                        "failing because no such method exists." %
                        self._collection_name)


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    oc = pymongo.MongoClient()
    db = oc["dbtest"]
    col = db["coltest"]

    c = MongoClient()
    c.collection = "test.test"
    c.is_master()
    d1 = {"name": "Heracles"}
    d2 = {"name": "Orpheus"}
    d3 = {"name": "Jason"}
    d4 = {"name": "Odysseus"}
    d5 = {"name": "Achilles"}
    d6 = {"name": "Menelaeus"}
    c.insert_one(d1)
    c.insert_many([d2, d3, d4, d5])
    c.drop_collection(confirm=False)

    p1 = {"name": "Joe Drumgoole",
          "social": ["twitter", "instagram", "linkedin"],
          "mobile": "+353 87xxxxxxx",
          "email": "Joe.Drumgoole@mongodb.com"}
    p2 = {"name": "Hercules Mulligan",
          "social": ["twitter", "linkedin"],
          "mobile": "+1 12345678",
          "email": "Hercules.Mulligan@example.com"}
    p3 = {"name": "Aaron Burr",
          "social": ["instagram"],
          "mobile": "+1 67891011",
          "email": "Aaron.Burr@example.com"}
    c.insert_many([p1, p2, p3])
    c.count_documents()
    c.count_documents({"name": "Joe Drumgoole"})
    c.create_index("social")
    c.drop_index("social_1")
    c.update_one({"name": "Joe Drumgoole"}, {"$set": {"age": 35}})
    c.update_one({"name": "Joe Drumgoole"}, {"$set": {"age": 35}})
    c.update_many({"social": "twitter"}, {"$set": {"followers": 1000}})
    c = MongoClient(
        host="mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority")
    try:
        c.find(1)  # force an error
    except TypeError:
        pass

    c.bongo  # make a collection
    try:
        c.bongospongo()  # call an invalid method
    except TypeError:
        pass

    #
    c = MongoClient()
    c.ldbs
    c.collection = "dummy.data"
    c.insert_one({"name": "Joe Drumgoole"})
    c.ldbs
    c.drop_database(confirm=False)
    c.ldbs

