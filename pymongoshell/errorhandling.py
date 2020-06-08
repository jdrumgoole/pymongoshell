import sys
import pprint


from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, \
    AutoReconnect, BulkWriteError, DuplicateKeyError


class CollectionNotSetError(ValueError):
    pass


class ShellError(ValueError):
    pass


class MongoDBShellError(ValueError):
    pass

def compliant_decorator(decorator):
    """
    This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @compliant_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.
    """
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make compliant_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


def print_to_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#
# decorator to handle exceptions
#

def args_to_string(*args, **kwargs):
    args_list = ""
    for i, arg in enumerate(args):
        if callable(arg):
            args_list = f"{args_list}{arg}" #{arg.__name__} ()"
        else:
            args_list = f"{args_list}{arg}"
        if len(args) > 1 and (i+1) < len(args):
            args_list = f"{args_list}, "

    kwarg_list = ",".join([f"'{x}'={y}" for x, y in kwargs.items()])

    if args_list and kwarg_list:
        return f"{args_list}, {kwarg_list}"
    elif args_list:
        return f"{args_list}"
    elif kwarg_list:
        return f"{kwarg_list}"
    else:
        return ""


# def error_func(error):
#     def director(func):
#         def inner_error(*args, **kwargs):
#             print(f"Error func: {func.__name__} {error}")
#             if args:
#                 print(f"{args}")
#             if kwargs:
#                 print(f"{kwargs}")
#         return inner_error
#
#     return director


def handle_exceptions(arg):
    def director(func):
        def function_wrapper(*args, **kwargs):
            label = arg or ""
            arg_string = args_to_string(*args, **kwargs)

            source = f"{label}({arg_string})"
            function_wrapper.__name__ = func.__name__
            #source = ""
            try:
                #print(f"arg_string:{arg_string}")
                return func(*args, **kwargs)
            except AttributeError as e:
                print_to_err(f"CLI AttributeError: {func.__name__} is not a valid operation")
               # return error_func(f"AttributeError (he): {func.__name__} is not a valid operation")
            except TypeError as e:
                print_to_err(f"CLI TypeError: '{source}' {e}")
            except ServerSelectionTimeoutError as e:
                print_to_err(f"CLI ServerSelectionTimeoutError: {label} {e}")
                print_to_err(f"CLI Do you have a mongod server running?")
            except AutoReconnect as e:
                print_to_err(f"CLI AutoReconnect error: {source} {e}")
            except BulkWriteError as e:
                print_to_err(f"CLI BulkWriteError: {source} {e}")
                err_str = pprint.pformat(e)
                print_to_err(err_str)
            except DuplicateKeyError as e:
                print_to_err(f"CLI DuplicateKeyError: {source}")
                err_str = pprint.pformat(e.details)
                print_to_err(err_str)
            except OperationFailure as e:
                print_to_err(f"CLI OperationsFailure:{source}")
                print_to_err(e.code)
                print_to_err(e.details)
            except MongoDBShellError as e:
                print_to_err(f"CLI MongoDBShellError: {e}")
            except CollectionNotSetError as e:
                print_to_err(f"CLI CollectionNotSetError: you must set a default collection")
            except Exception as e:
                print_to_err(f"CLI Exception: {source} {e}")

        function_wrapper.__name__ = func.__name__
        return function_wrapper

    return director

@handle_exceptions("test")
def test_errorhandling(dummy_arg):
    print(f"dummy arg: {dummy_arg}")
    raise TypeError

class TestErrorClass:

    def __init__(self):
        self.dummy_func("test in init")
        pass

    @handle_exceptions("dummy_func")
    def dummy_func(self, x):
        print(f"x={x}")

if __name__ == "__main__":
    x=1
    y=2
    z=[x,y]
    w=args_to_string
    a = TestErrorClass()
    print(args_to_string(x,y,z,w, blah="splah"))
    print(args_to_string())
    test_errorhandling("func test")
    a.dummy_func("class test")
    a.dummy_func(a)
