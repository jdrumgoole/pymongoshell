"""
Created on 22 Nov 2016

@author: jdrumgoole
"""

from pprint import pprint


def coroutine(func):
    """
    A decorator to start a generator with a send operation. You need
    an initial `next()` to get started.
    :param func: generator function
    :return: generator function
    """
    def start( *args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


def print_count( iterator, printfunc=None ):
    count = 0
    for i in iterator :
        count = count + 1
        if printfunc is None:
            pprint(i)
        else:
            printfunc(i)
    print(f"Total: {count}")
