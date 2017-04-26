'''
Created on 14 Dec 2016

@author: jdrumgoole
'''
import unittest

from batchwriter import DocTransform
class Test(unittest.TestCase):


    def test_DocTransform(self):
        
        x = DocTransform()
        a={}
        y =x( a )
        self.assertEqual( y, a )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDocxform']
    unittest.main()