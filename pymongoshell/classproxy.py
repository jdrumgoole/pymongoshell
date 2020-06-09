class ClassProxy:

    def __init__(self, class_object):
        self.__class_object = class_object

    def __getattr__(self, name, *args, **kwargs):
        '''
        Call __getattr__ if we specify members that don't exist. The
        goal here is to pass any function not directly implemented
        by this class straight up to pymongo.Collection.

        Here we intercept the function lookup invoked of the
        pymongoshell.MongoClient object and use it to invoke the
        pymongo.Collection class directly. The nested inner function
        is required to capture the parameters correctly.

        :param name: the method or property that doesn't exist.
        :param args: args passed in by invoker
        :param kwargs: kwargs passed in by invoker
        :return: Results of call target method
        '''


        op = self.__class_object.has_attr(self._collection, name)
        if col_op is None:
            self._collection=self.collection.__getattr__(name)
            self._collection_name = name
            print(f"Setting default database and collection to: {self.collection_name}")
        else:
            def make_invoker(invoker):
                if callable(invoker):
                    @handle_exceptions(col_op.__name__)
                    def inner_func(*args, **kwargs):
                        #print(f"inner func({args}, {kwargs})")
                        result = invoker(*args, **kwargs)
                        if type(result) in [pymongo.command_cursor.CommandCursor, pymongo.cursor.Cursor]:
                            self.print_cursor(result)
                        elif self._handle_result.is_result_type(result):
                            self._handle_result.handle(result)
                        elif type(result) is dict:
                            self._pager.paginate_doc(result)

                        else:
                            #(f"type result: {type(result)}")
                            #print(f"result: {result}")
                            return result
                        inner_func.__name__ = col_op.__name__
                    #print(f"inner_func.__name__ : {inner_func.__name__}")
                    return inner_func
                else:
                    return invoker
            #print(f"make_invoker.__name__ : {make_invoker.__name__}")
            return make_invoker(col_op)


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
