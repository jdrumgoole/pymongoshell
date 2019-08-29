import unittest
from mongodbshell.pager import Pager


class TestPager(unittest.TestCase):
    def test_pager(self):
        pager = Pager(line_number=1)
        self.assertEqual(pager.line_numbers, 1)
        lines = pager.to_lines("aaa")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0],pager.prefix(pager.line_numbers) + "aaa")
        lines = pager.to_lines("")
        self.assertEqual(len(lines), 0)

        lines = pager.to_lines("12345abcde12345", 5)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], pager.prefix(1))


        lines = pager.to_lines("12345abcde12345", 10)
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], pager.prefix(pager.line_numbers)+"12345")
        self.assertEqual(lines[1], pager.prefix(pager.line_numbers)+"abcde")
        self.assertEqual(lines[2], pager.prefix(pager.line_numbers)+"12345")

if __name__ == '__main__':
    unittest.main()
