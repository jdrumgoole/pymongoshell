import unittest
from mongodbshell import mproxy

class TestShell(unittest.TestCase):

    def test_client(self):
        self.assertTrue(c.is_master())


if __name__ == '__main__':
    unittest.main()
