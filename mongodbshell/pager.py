import shutil
import pprint


class QuitPaginateException(Exception):
    pass


class LineNumbers:

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
        if number:
            return f'{number:<3}: '
        else:
            return ""

    def line_number(self, s):
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
                 line_number: int = 1):
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
        self._line_numbers = line_number
        self._paginate_prompt = paginate_prompt

        assert type(paginate_prompt) is str

    def to_lines(self, line: str, width: int = 80, line_numbers: int = 0) -> list:
        """
        Take a line and split into separate lines at width boundaries
        also if self.line_numbers > 0 then at the defined line number prefix
        to each line.

        :param line: A string of input
        :param width: the size of the terminal in columns
        :param line_numbers: Add line_numbers if greater than 0.
        :return: A list of strings split at width boundaries from line
        """
        lines: list = []
        prefix = ""
        prefix_size = 0

        prefix_size = len(LineNumbers.prefix(line_numbers))

        while len(line) + prefix_size > width:

            if prefix_size < width:
                segment: str = LineNumbers.prefix(line_numbers) + line[0:width - prefix_size]
                lines.append(segment)
                line: str = line[width - prefix_size:]

                if line_numbers:
                    line_numbers = line_numbers + 1
                    prefix_size = LineNumbers.prefix(line_numbers)
            else:
                segment: str = prefix[0:width]
                lines.append(segment)
                line: str = ""

        if len(line) > 0:
            lines.append(prefix + line)

        return lines

    def page_lines(self, lines: list):
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

        `overlap` : The number of lines to overlap between one page and the
        next.

        :param lines:
        :return: paginated output
        """
        try:

            if self._output_filename:
                self._output_file = open(self._output_filename, "a+")

            terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))

            output_lines =[]
            prompt_lines = self.to_lines(self._paginate_prompt, terminal_columns, line_numbers=0)  # No line numbers

            line_counter = 1
            for l in lines:
                if self._output_file:
                    self._output_file.write(f"{l}\n")
                    self._output_file.flush()

                terminal_columns, terminal_lines = shutil.get_terminal_size(fallback=(80, 24))
                additional_lines = self.to_lines(l, terminal_columns, line_numbers=line_counter)
                line_counter = line_counter + len(additional_lines)
                buffer_length = len(output_lines) + len(additional_lines)

                if buffer_length == terminal_lines:
                    output_lines.extend(additional_lines)
                    for i in output_lines:
                        print(f"a{i}")
                        if self._paginate:
                            print(output_lines[0], end="")
                            user_input = input()
                            if user_input.lower().strip() in ["q", "quit", "exit"]:
                                raise QuitPaginateException
                    output_lines = []
                elif buffer_length > terminal_columns:
                    residue = buffer_length - terminal_columns
                    output_lines.extend(additional_lines[0:residue])
                    for i in output_lines:
                        print(f"b{i}")
                        if user_input.lower().strip() in ["q", "quit", "exit"]:
                            raise QuitPaginateException
                        output_lines = additional_lines[residue:]

                else:
                    output_lines.extend(additional_lines)

            for i in output_lines:
                print(f"a{i}")

            # if self._paginate:
            #         user_input = input()
            #         if user_input.lower().strip() in ["q", "quit", "exit"]:
            #             raise QuitPaginateException

        except QuitPaginateException:
            pass

        except KeyboardInterrupt:
            print("ctrl-C...")
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
