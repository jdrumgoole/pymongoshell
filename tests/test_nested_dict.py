'''
Created on 3 May 2017

@author: jdrumgoole
'''
import unittest

from mongodb_utils.nested_dict import Nested_Dict

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass

    def test_create(self):
        d = Nested_Dict()
        self.assertEqual( len( d ) , 0 )
        self.assertFalse( d.has_key( "hello"))
        
    def test_insert_simple(self):
        d = Nested_Dict()
        d.set_value( "hello", "world")
        self.assertTrue( d.has_key( "hello"))
        self.assertEqual( d.get_value( "hello" ), "world" )
        
    def test_key_error( self ):
        d = Nested_Dict()
        self.assertRaises( KeyError, d.get_value, "Bingo" )
          
    def test_set_value(self):
        d = Nested_Dict()
        d.set_value( "a", "b")
        self.assertEqual( d.get_value( "a"), "b")
         
    def test_set_value_nested(self):
        x = Nested_Dict()
        
        x.set_value( "member.name", "Joe Drumgoole")
        self.assertEqual( x.get_value( "member"), { "name" : "Joe Drumgoole" })
        name = x.get_value( "member.name")
        self.assertEqual( name,"Joe Drumgoole")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()