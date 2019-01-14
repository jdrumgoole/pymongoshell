import unittest
from mongodbshell import Client

class TestShell(unittest.TestCase):

    def test_client(self):
        c=Client()
        self.assertTrue(c.is_master())


if __name__ == '__main__':
    unittest.main()
