import shutil
import pprint
from datetime import datetime

import pymongo


class QuitPaginateException(Exception):
    pass


class PaginationError(Exception):
    pass


class FileNotOpenError(Exception):
    pass


class LineNumbers:
    """
    Prepend line numbers to a string.
    """

    def __init__(self, start: int = 0):
        """
        Take a string '<x>' and return an string prefixed by a line number
        of the form '<start> : <x>'. Where start is greater than one. if start
        is 0 (zero) then LineNumbers just returns the input string unaltered.

        :param start:
        """
        self._line_number = start

    @property
    def line_number(self):
        return self._line_number

    @line_number.setter
    def line_number(self, line_number: int):
        """
        :type line_number: int
        """
        self._line_number = line_number

    @staticmethod
    def prefix():
        """

        :param number: If None return an empty prefix
        :return: a prefix string
        """
        if self._line_number == 0:
            return ""
        else:
            return f'{self._line_number:<3}: '


    def add_line_number(self, s):
        """
        Take a string and return a prefixed string and the new string size
        :param s: string to have a prefix added
        :return: (size of prefix, prefixed string)
        """
        p = LineNumbers.prefix(self._line_number)
        return len(p), f"{p}{s}"

    def inc_line_number(self,s):
        len_p, s = self.add_line_number(s)
        self._line_number = self._line_number + 1
        return len_p, s


class Pager:
    """
    Provide paginating services allow content to be paginated
    using shutil to determine screen dimensions
    """

    def __init__(self,
                 paginate: bool = True,
                 paginate_prompt: str = "Hit Return to continue (q or quit to exit)",
                 output_filename: str = None,
                 line_numbers: bool = True,
                 pretty_print: bool = True):
        """

        :param paginate: paginate at terminal boundaries
        :param output_filename: send output to file as well
        :param line_number: if 0 no line numbers are emitted. If 1 or more
        start line_numbers from that point and auto increment with
        line_number function.

        """
        self._paginate = paginate
        self._output_filename = output_filename
        self._output_file = None
        self._line_numbers = True
        self._line_count = LineNumbers()
        self._paginate_prompt = paginate_prompt
        self._pretty_print = pretty_print

        assert type(paginate_prompt) is str

    @property
    def line_numbers(self):
        return self._line_numbers

    def line_numbers(self, state):
        self._line_numbers = state

    def prefix(self, number):
        if self._line_numbers:
            return LineNumbers.prefix(number)
        else:
            return 0

    @property
    def output_file(self):
        return self._output_filename

    @output_file.setter
    def output_file(self, name):
        self.open(name)

    @property
    def paginate(self):
        return self._paginate

    @paginate.setter
    def paginate(self, state):
        self._paginate = state

    @property
    def pretty_print(self):
        return self._pretty_print

    @pretty_print.setter
    def pretty_print(self, state):
        self._pretty_print = state

    def close(self):
        if self._output_file and not self._output_file.closed:
            self._output_file.write(f"# closing '{self._output_filename}' {datetime.utcnow()}\n")
            self._output_file.close()
            self._output_file = None

    def open(self, name):
        self.close()
        if name:
            self._output_file = open(name, "w+")
            self._output_filename = name
            self._output_file.write(f"# opening '{name}' {datetime.utcnow()}\n")
            self._output_file.flush()
        self._output_filename = name

    def write_file(self, s):
        if self._output_file:
            self._output_file.write(s)
            self._output_file.flush()
        else:
            raise FileNotOpenError()

    @staticmethod
    def make_numbers_column(line_number):
        """
        make a column of numbers all of the same width. The width is determined
        by the largest number + 1 space + 1 colon.
        :param line_number: The line number to start counting at
        :return: an array of strings line_number .. screen height.
        """
        terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
        terminal_lines = terminal_lines -1 # prompt line to continue
        original_lines = []
        padded_lines = []
        prefix_width = 4
        max_prefix_width = 0
        for i in range(terminal_lines):
            s = str(line_number)
            original_lines.append(s)
            prefix_width = len(s) + 1 # space and ':'
            if prefix_width > max_prefix_width:
                max_prefix_width = prefix_width
            line_number = line_number + 1
        for i in original_lines:
            spaces = " " * (max_prefix_width - len(i))
            padded_lines.append(f"{i}{spaces}:")

        return line_number, padded_lines

    def line_to_box(self, line: str, width: int = 80) -> list:
        """
        Take a line and split into separate lines at width boundaries
        also if self.line_numbers > 0 then add the defined line number prefix
        to each line.

        :param line: A string of input
        :param width: the size of the terminal in columns
        :param line_number: Start incrementing line numbers from this number.
        :return: A list of strings split at width boundaries from line
        """
        lines: list = []

        while len(line) > width:
            line_number = line_number + 1
            segment: str = line[0:width]
            lines.append(segment)
            line: str = line[width:]

        if len(line) > 0:
            lines.append(line)

        return lines

    def line_to_paragraph(self, line: str, width: int = 80, line_number: int = 0) -> list:
        """
        Take a line and split into separate lines at width boundaries
        also if self.line_numbers > 0 then add the defined line number prefix
        to each line.

        :param line: A string of input
        :param width: the size of the terminal in columns
        :param line_number: Start incrementing line numbers from this number.
        :return: A list of strings split at width boundaries from line
        """
        lines: list = []
        prefix = self.prefix(line_number)

        while len(prefix) + len(line) > width:
            line_number = line_number + 1
            if len(prefix) < width:
                segment: str = prefix + line[0:width - prefix_size]
                lines.append(segment)
                line: str = line[width - prefix_size:]
                prefix = self.prefix(line_number)
            else:
                segment: str = self.prefix(line_number)[0:width]
                lines.append(segment)
                line: str = ""

        if len(line) > 0:
            line_number = line_number + 1
            lines.append(self.prefix(line_number) + line)

        return lines


    # if self._paginate:
    #         user_input = input()
    #         if user_input.lower().strip() in ["q", "quit", "exit"]:
    #             raise QuitPaginateException

    def paginate_lines(self, lines: list,
                       default_terminal_lines: int = None,
                       default_terminal_cols: int = None):
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


        :param lines:
        :param default_terminal_lines: Use this to determine the screen length for testing
        if None then use shutil.get_terminal_size().
        :param default_terminal_cols: terminal_cols: Use this to determine the screen width for testing
        if None then use shutil.get_terminal_size().
        :return: paginated output
        """
        try:
            if self._output_filename:
                self._output_file = open(self._output_filename, "a+")

            output_lines = []
            prompt_lines = []
            overflow_lines = []
            line_number = 1
            line_number_strs = None

            for l in lines:
                # a line can be less than terminal width  - line number width. Just output it.
                # a line can be more than terminal width - line number width. Output the line number
                # and the line[0:terminal_width - line_number_width].
                if self._output_file:
                    self._output_file.write(f"{l}\n")
                    self._output_file.flush()

                if self._paginate:
                    terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
                    baseline_number = line_number
                    line_number, line_number_strs = Pager.make_numbers_column(baseline_number)
                    line_number_width = len(line_number_strs[-1:])
                    if default_terminal_cols:
                        terminal_columns = default_terminal_cols
                    if default_terminal_lines:
                        terminal_lines = default_terminal_lines
                    terminal_columns = terminal_columns - 1  # subtract one because we force a newline if we fill the
                    # column which messes up the formatting

                    if terminal_lines < 2:
                        raise PaginationError("Only 1 display line for output, I need at least two")

                    # is the pagination prompt wider than the screen? If it is then we need to
                    # fold it into a number of lines. This will be subtracted from the available
                    # vertical display real estate.
                    # We calculate the prompt size first so we know how many lines are left from
                    # program output. Probably not a good idea to make your prompt longer than
                    # 80 columns.
                    prompt_lines = self.line_to_box(self._paginate_prompt,
                                                    terminal_columns - line_number_width)

                    multi_line = overflow_lines + self.line_to_box(l, terminal_columns - line_number_width)
                    overflow_lines = []
                    # print(f"{multi_line}")
                    #line_number = line_number + len(multi_line)
                    buffer_length = len(output_lines) + len(multi_line)
                    terminal_lines = terminal_lines - len(prompt_lines)  # leave room to output prompt

                    if buffer_length < terminal_lines:
                        output_lines.extend(multi_line)
                        line_number = baseline_number # We are still building the screen so we need to calculate from 0.
                        line_number_strs = []
                        continue
                    if buffer_length == terminal_lines:
                        output_lines.extend(multi_line)
                    elif buffer_length > terminal_lines:
                        overflow = buffer_length - terminal_lines
                        output_lines.extend(multi_line[0:overflow])
                        overflow_lines = multi_line[overflow:]

                    for line_no, s in zip(line_number_strs, output_lines):
                        print(f"{line_no}{s}")

                    #
                    # Output potentially multi-line prompt string.
                    #
                    for i, line_counter in enumerate(prompt_lines, 1):
                        if i == len(prompt_lines):
                            print(f"{line_counter}", end="")
                        else:
                            print(f"{line_counter}")
                    user_input = input()
                    if user_input.lower().strip() in ["q", "quit", "exit"]:
                        raise QuitPaginateException
                    output_lines = []
                else:
                    print(l)
            # if self._paginate:
            #         user_input = input()
            #         if user_input.lower().strip() in ["q", "quit", "exit"]:
            #             raise QuitPaginateException

            for i in output_lines:
                print(f"{i}")

        except QuitPaginateException:
            pass

        except KeyboardInterrupt:
            print("ctrl-C...")
        finally:
            if self._output_file:
                self._output_file.close()

    def dict_to_lines(self, d, format_func=None):
        """
        Generator that converts a doc to a sequence of lines.
        :param d: A dictionary
        :param format_func: customisable formatter defaults to pformat
        :return: a generator yielding a line at a time
        """
        if format_func:
            for l in format_func(d).splitlines():
                yield l
        elif self._pretty_print:
            for l in pprint.pformat(d).splitlines():
                yield l
        else:
            for l in str(d).splitlines():
                yield l


    @staticmethod
    def list_to_line(l):
        open_bracket = "["
        close_bracket = "]"
        for i, elem in enumerate(l):
            if i == 0:
                elem = open_bracket + elem
            if i == (len(l) - 1):
                elem = elem + close_bracket
            yield elem

    def paginate_doc(self, doc):
        return self.paginate_lines(self.dict_to_lines(doc))

    def __del__(self):
        # if self._output_file:
        #     print(f"__del__ file closed: {self._output_file.closed}")
        # else:
        #     print("__del__ output_file is None")
        self.close()

    def cursor_to_lines(self, cursor: pymongo.cursor, format_func=None):
        """
        Take a cursor that returns a list of docs and returns a
        generator yield each line of each doc a line at a time.

        :param cursor: A mongodb cursor yielding docs (dictionaries)
        :param format_func: A customisable format function, expects and returns a doc
        :return: a generator yielding a line at a time
        """
        for doc in cursor:
            yield from self.dict_to_lines(doc, format_func)

    def print_cursor(self,  cursor, format_func=None):
        return self.paginate_lines(self.cursor_to_lines(cursor, format_func))
