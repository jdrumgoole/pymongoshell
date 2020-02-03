import shutil
import pprint


class QuitPaginateException(Exception):
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
    def line_numbers(self):
        return self._line_numbers

    @line_numbers.setter
    def line_number(self, line_number: int):
        """
        :type line_numbers: int
        """
        self._line_number = line_number

    @staticmethod
    def prefix(number):
        """

        :param number: If None return an empty prefix
        :return: a prefix string
        """
        if number:
            return f'{number:<3}: '
        else:
            return ""

    def line_number(self, s):
        """
        Take a string and return a prefixed string and the new string size
        :param s: string to have a prefix added
        :return: (size, prefixed string)
        """
        if self._line_number:
            p = LineNumbers.prefix(self._line_number)
            x = f"{p}{s}"
            return len(p), x

        else:
            return 0, s


class Pager:
    """
    Provide paginating services allow content to be paginated
    using shutil to determine screen dimensions
    """

    def __init__(self,
                 paginate: bool = True,
                 paginate_prompt: str ="Hit Return to continue (q or quit to exit)",
                 output_filename: str = None,
                 line_numbers: bool= True ):
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
        self._line_numbers = line_numbers
        self._paginate_prompt = paginate_prompt

        assert type(paginate_prompt) is str

    @property
    def line_numbers(self):
        return self._line_numbers

    def prefix(self, number):
        return LineNumbers.prefix(number)

    def split_lines(self, line: str, width: int = 80, line_number:int=0) -> list:
        """
        Take a line and split into separate lines at width boundaries
        also if self.line_numbers > 0 then add the defined line number prefix
        to each line.

        :param line: A string of input
        :param width: the size of the terminal in columns
        :param line_numbers: Start incrementing line numbers from this number.
        :return: A list of strings split at width boundaries from line
        """
        lines: list = []
        prefix = self.prefix(line_number)
        prefix_size = len(prefix)

        while len(line) + prefix_size > width:

            if prefix_size < width:
                segment: str = prefix + line[0:width - prefix_size]
                lines.append(segment)
                line: str = line[width - prefix_size:]

                if line_number:
                    line_number = line_number + 1
                    prefix = self.prefix(line_number)
                    prefix_size = len(prefix)
            else:
                segment: str = self.prefix(line_number)[0:width]
                lines.append(segment)
                line: str = ""

        if len(line) > 0:
            lines.append(self.prefix(line_number) + line)

        return lines

    def paginate_lines(self, lines: list):
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
        :return: paginated output
        """
        try:

            if self._output_filename:
                self._output_file = open(self._output_filename, "a+")

            output_lines =[]
            prompt_lines = []
            residue_lines = []
            if self._line_numbers:
                line_number = 1
            else:
                line_number = 0

            for l in lines:
                if self._output_file:
                    self._output_file.write(f"{l}\n")
                    self._output_file.flush()

                if self._paginate:
                    terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
                    prompt_lines = self.split_lines(self._paginate_prompt,
                                                    terminal_columns)  # No line numbers

                    additional_lines = residue_lines + self.split_lines(l, terminal_columns, line_number)
                    #print(f"{additional_lines}")
                    line_number = line_number + len(additional_lines)
                    buffer_length = len(output_lines) + len(additional_lines)
                    terminal_lines = terminal_lines - len(prompt_lines)  # leave room to output prompt

                    if buffer_length < terminal_lines:
                        output_lines.extend(additional_lines)
                        continue
                    if buffer_length == terminal_lines:
                        output_lines.extend(additional_lines)
                    elif buffer_length > terminal_lines:
                        residue = buffer_length - terminal_lines
                        output_lines.extend(additional_lines[0:residue])
                        residue_lines = additional_lines[residue:]

                    for data in output_lines:
                        print(f"{data}")
                    for i, prompt in enumerate(prompt_lines, 1):
                        if i == len(prompt_lines):
                            print(f"{prompt}", end="")
                        else:
                            print(f"{prompt}")
                        user_input = input()
                        if user_input.lower().strip() in ["q", "quit", "exit"]:
                            raise QuitPaginateException
                    output_lines = []
                else:
                    for line in additional_lines:
                        print(f"{line}")
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
