import unittest
from mongodbshell.pager import Pager
from mongodbshell.pager import LineNumbers
import string
import random
import os

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def find(fn,s):
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
        self.assertEqual(lines[0], LineNumbers.prefix(1) +"12345")
        self.assertEqual(lines[1], LineNumbers.prefix(2) +"abcde")
        self.assertEqual(lines[2], LineNumbers.prefix(3) +"12345")

    def test_file(self):
        pager = Pager()
        name = randomString(10)
        rs=randomString(10)
        pager.output_file = name
        self.assertTrue(find(name, "# opening"))
        pager.output_file = None
        self.assertTrue(find(name, "# closing"))
        pager.output_file = name
        pager.write_file(f"{rs}\n")
        pager.close()
        self.assertTrue(find(name, rs))
        os.unlink(name)
if __name__ == '__main__':
    unittest.main()
