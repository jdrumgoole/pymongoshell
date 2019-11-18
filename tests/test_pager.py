import unittest
from mongodbshell.pager import Pager
from mongodbshell.pager import LineNumbers

class TestPager(unittest.TestCase):

    def test_pager(self):
        pager = Pager(line_number=1)
        lines = pager.to_lines("aaa")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], LineNumbers.prefix(1) + "aaa")
        lines = pager.to_lines("")
        self.assertEqual(len(lines), 0)

        lines = pager.to_lines("12345abcde12345", width=5)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], LineNumbers.prefix(1))


        lines = pager.to_lines("12345abcde12345", 10)
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], LineNumbers.prefix(1) +"12345")
        self.assertEqual(lines[1], LineNumbers.prefix(2) +"abcde")
        self.assertEqual(lines[2], LineNumbers.prefix(3) +"12345")

if __name__ == '__main__':
    unittest.main()
