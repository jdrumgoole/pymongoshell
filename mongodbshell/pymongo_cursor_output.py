import pprint
import shutil


def print_cursor(cursor, pretty_print=False):
    """
    Print a MongoDB cursor to the screen. The cursor can be any iterable
    containing JSON documents.

    :param cursor: Iterable of JSON docs.
    :param pretty_print: Use pprint to format docs.
    :return: Count of total docs written.
    """
    i = 0
    (columns, lines) = shutil.get_terminal_size(fallback=(80, 24))
    try:
        line_count = 0
        for doc, i in enumerate(cursor, 1):
            if len(str(doc)) > columns or pretty_print:
                for line in pprint.pformat(doc).splitlines():
                    print(line)
                    line_count += 1
                    if line_count == lines - 5:
                        print("Hit Return to continue")
                        _ = input()
                        line_count = 0
            else:
                print(doc)
                line_count += 1
                if line_count == lines - 5:
                    print("Hit Return to continue")
                    _ = input()
                    line_count = 0
            # screen might change dimensions during output
            (columns, lines) = shutil.get_terminal_size(fallback=(80, 24))

        return i
    except KeyboardInterrupt:
        print("Ctrl-C...")
        return i
