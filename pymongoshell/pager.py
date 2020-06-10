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

    def prefix(self):
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

    def inc_line_number(self, s):
        len_p, s = self.add_line_number(s)
        self._line_number = self._line_number + 1
        return len_p, s

    def __str__(self):
        return f"{self.prefix()}"

    def __repr__(self):
        return f"LineNumber({self._line_number})"


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
            return LineNumbers(number).prefix()
        else:
            return ""

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
    def indented_number(line_number):
        return f"{line_number} : "

    @staticmethod
    def make_numbers_column(line_number, default_cols=None, default_lines=None):
        """
        make a column of numbers all of the same width. The width is determined
        by the largest number + 1 space + 1 colon.
        :param line_number: The line number to start counting at
        :return: an array of strings line_number .. screen height.
        """
        terminal_columns, terminal_lines = Pager.get_terminal_cols_lines(default_cols, default_lines)
        terminal_lines = terminal_lines - 1  # prompt line to continue
        original_lines = []
        padded_lines = []
        prefix_width = 4
        max_prefix_width = 0
        for i in range(terminal_lines):
            s = str(line_number)
            original_lines.append(s)
            prefix_width = len(s) + 1  # space and ':'
            if prefix_width > max_prefix_width:
                max_prefix_width = prefix_width
            line_number = line_number + 1
        for i in original_lines:
            spaces = " " * (max_prefix_width - len(i))
            padded_lines.append(f"{i}{spaces}: ")

        return padded_lines

    def line_to_box(self, line: str, width: int = 80) -> list:
        """
        Take a line and split into separate lines at width boundaries making
        a box of line * width dimensions

        :param line: A string of input
        :param width: the size of the terminal in columns
        :return: A list of strings split at width boundaries from line
        """
        lines: list = []
        while len(line) > width:
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
            if len(prefix) < width:
                segment: str = prefix + line[0:width - len(prefix)]
                lines.append(segment)
                line: str = line[width - len(prefix):]
                line_number = line_number + 1
                prefix = self.prefix(line_number)
            else:
                segment: str = self.prefix(line_number)[0:width]
                lines.append(segment)
                line: str = ""
        if len(line) > 0:
            lines.append(self.prefix(line_number) + line)

        return lines

    @staticmethod
    def get_terminal_cols_lines(default_columns=None, default_lines=None):
        terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))

        if default_lines:
            terminal_lines = default_lines
        if default_columns:
            terminal_columns = default_columns

        return terminal_columns, terminal_lines

    @staticmethod
    def input_prompt(prompt_lines):
        for i, line_counter in enumerate(prompt_lines, 1):
            if i == len(prompt_lines):
                print(f"{line_counter}", end="")
            else:
                print(f"{line_counter}")
        user_input = input()
        if user_input.lower().strip() in ["q", "quit", "exit"]:
            raise QuitPaginateException

    def make_page(self,
                  lines: list,
                  terminal_columns: int = None,
                  terminal_lines: int = None):

        residue_lines = []

        if terminal_lines < 2:
            raise PaginationError("Only 1 display line for output, I need at least two")

        # number_prefix_width = len(Pager.indented_number(line_number + len(terminal_lines)))
        # is the pagination prompt wider than the screen? If it is then we need to
        # fold it into a number of lines. This will be subtracted from the available
        # vertical display real estate.
        # We calculate the prompt size first so we know how many lines are left from
        # program output. Probably not a good idea to make your prompt longer than
        # 80 columns.

        output_lines = []
        remaining_page_lines = terminal_lines
        lines_consumed = 0

        for l in lines:
            # a line can be less than terminal width  - line number width. Just output it.
            # a line can be more than terminal width - line number width. Output the line number
            # and the line[0:terminal_width - line_number_width].
            if self._output_file:
                self._output_file.write(f"{l}\n")
                self._output_file.flush()

            multi_lines = self.line_to_box(l, terminal_columns)
            lines_consumed = lines_consumed + 1
            remaining_page_lines = remaining_page_lines - len(multi_lines)
            if remaining_page_lines == 0:  # filled the page
                output_lines.extend(multi_lines)
                break
            elif remaining_page_lines > 0:  # still have space on the page
                output_lines.extend(multi_lines)
            elif remaining_page_lines < 0:  # overrun the end of the page
                output_lines.extend(multi_lines[0:remaining_page_lines])
                residue_lines = multi_lines[remaining_page_lines:]
                break

        input_lines_remaining = lines[lines_consumed:]
        residue_lines.extend(input_lines_remaining)

        return output_lines, residue_lines

    @staticmethod
    def line_chunker(lines, chunk_size=24):
        chunk = []
        for l in lines:
            chunk.append(l)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

    def paginate_lines(self, lines,
                       default_terminal_cols: int = None,
                       default_terminal_lines: int = None):
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

            line_number = 1
            residual_lines = []
            terminal_columns, terminal_lines = Pager.get_terminal_cols_lines(default_terminal_cols,
                                                                             default_terminal_lines)
            for page_lines in Pager.line_chunker(lines, terminal_lines):
                if self._paginate:
                    residual_lines.extend(page_lines)
                    page_lines = residual_lines
                    terminal_columns, terminal_lines = Pager.get_terminal_cols_lines(default_terminal_cols,
                                                                                     default_terminal_lines)
                    prompt_lines = self.line_to_box(self._paginate_prompt,
                                                    terminal_columns)
                    if self.line_numbers:
                        number_prefix_width = len(Pager.indented_number(line_number + terminal_lines))
                    else:
                        number_prefix_width = 0

                    output_lines, residual_lines = self.make_page(page_lines,
                                                                  terminal_columns - number_prefix_width,
                                                                  terminal_lines - len(prompt_lines))
                    if self.line_numbers:
                        line_number_column = Pager.make_numbers_column(line_number,
                                                                       default_terminal_cols,
                                                                       default_terminal_lines)

                        for number, line in zip(line_number_column, output_lines):
                            print(f"{number}{line}")
                            line_number = line_number + 1
                    else:
                        for line in output_lines:
                            print(f"{line}")
                            line_number = line_number + 1

                    if len(output_lines) == (terminal_lines - len(prompt_lines)):
                        Pager.input_prompt(prompt_lines)
                else:
                    for l in page_lines:
                        if self.line_numbers:
                            print(f"{line_number} : {l}")
                            line_number = line_number + 1
                        else:
                            print(l)
                        if self.output_file:
                            self._output_file.write(f"{l}\n")
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
    def list_to_line_gen(l: list):
        open_bracket = "["
        close_bracket = "]"
        for i, elem in enumerate(l):
            if i == 0:
                elem = f"{open_bracket}{elem},"
            if i == (len(l) - 1):
                elem = f"{elem}{close_bracket}"
            yield f"{elem},"

    @staticmethod
    def list_to_lines(l: list):
        open_bracket = "["
        close_bracket = "]"
        result = []
        for i, elem in enumerate(l):
            if i == 0:
                result.append(f"{open_bracket}{elem},")
            elif i == (len(l) - 1):
                result.append(f"{elem}{close_bracket}")
            else:
                result.append(f"{elem},")
        if len(result) == 0:
            return [str(result)]
        else:
            return result

    def paginate_list(self, l):
        return self.paginate_lines(Pager.list_to_lines(l))

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

    def print_cursor(self, cursor, format_func=None):
        return self.paginate_lines(self.cursor_to_lines(cursor, format_func))
