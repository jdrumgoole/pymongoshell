import unittest
from contextlib import contextmanager
import string
import random
import os
from io import StringIO
import sys
from pymongoshell.pager import Pager
from pymongoshell.pager import LineNumbers


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def randomString(string_length: int = 10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))


def find(fn: str, s: str):
    with open(fn) as my_file:
        return s in my_file.read()


class TestPager(unittest.TestCase):

    def test_pager(self):
        pager = Pager(line_numbers=True)
        lines = pager.line_to_paragraph("aaa", line_number=1)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], LineNumbers.prefix(1) + "aaa")
        lines = pager.line_to_paragraph("")
        self.assertEqual(len(lines), 0)

        lines = pager.line_to_paragraph("12345abcde12345", width=5, line_number=1)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], LineNumbers.prefix(1))

        lines = pager.line_to_paragraph("12345abcde12345", 10, line_number=1)
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], LineNumbers.prefix(1) + "12345")
        self.assertEqual(lines[1], LineNumbers.prefix(2) + "abcde")
        self.assertEqual(lines[2], LineNumbers.prefix(3) + "12345")

    def test_file(self):
        pager = Pager()
        name = randomString(10)
        rs = randomString(10)
        pager.output_file = name
        self.assertTrue(find(name, "# opening"))
        pager.output_file = None
        self.assertTrue(find(name, "# closing"))
        pager.output_file = name
        pager.write_file(f"{rs}\n")
        pager.close()
        self.assertTrue(find(name, rs))
        os.unlink(name)

    def test_paginate(self):
        line = '12345678901234567890'  # len(line) = 20
        lines_in = [line for _ in range(3)]
        assert len(line) == 20
        pager = Pager()
        #print("lines in")
        #print(lines_in)
        with captured_output() as (out, err):
            pager.paginate_lines(lines_in, default_terminal_cols=20, default_terminal_lines=24)

        # print("out.getvalue()")
        # print(f"{out.getvalue().splitlines()}")

        test_output = "1  : 12345678901234\n" \
                      "2  : 567890\n" \
                      "3  : 12345678901234\n" \
                      "4  : 567890\n" \
                      "5  : 12345678901234\n" \
                      "6  : 567890\n"

        # print("test_output")
        # print(f"{test_output.splitlines()}")

        self.assertEqual(len(out.getvalue()), len(test_output))
        self.assertEqual(out.getvalue(), test_output, out.getvalue())

    def test_list_to_line(self):
        pager = Pager()
        l = pager.list_to_line([1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()
