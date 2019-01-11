"""
Created on 3 May 2017

@author: jdrumgoole

"""

import unittest

from mongodbutils.nesteddict import NestedDict


class TestNestedDict(unittest.TestCase):

    def test_in(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertTrue("a" in x)
        self.assertTrue("a.b" in x)
        self.assertTrue("a" in x)
        self.assertFalse("z" in x)
        self.assertFalse("a.z" in x)

    def test_getitem(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertEqual(x['a'], {"b": 1})
        self.assertEqual(x['a.b'], 1)
        x = NestedDict({'a': {'b': [1, 2, 3]}})
        self.assertEqual(x['a.b'], [1, 2, 3])
        self.assertRaises(KeyError, x.__getitem__, "w.z")

    def test_setitem(self):
        x = NestedDict({"a": {"b": 1}})
        x['c'] = 2
        self.assertEqual(x['c'], 2)
        x['a.b'] = 3
        self.assertEqual(x['a.b'], 3)

    def test_delitem(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertEqual(x.get('a'), {"b": 1})
        del x['a.b']
        self.assertTrue('a' in x)
        x = NestedDict({"a": {"b": 1}})
        del x['a']
        self.assertFalse('a.b' in x)
        self.assertFalse('a' in x)

    def test_get(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertEqual(x.get('a'), {"b": 1})
        self.assertEqual(x.get('z'), None)
        self.assertEqual(x.get('z', 20), 20)
        self.assertEqual(x.get('a.b'), 1)

    def test_has_key(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertTrue(x.has_key('a'))
        self.assertTrue(x.has_key('a.b'))
        self.assertFalse(x.has_key('z'))

    def test_pop(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertEqual(x.pop('a.b'), 1)
        self.assertFalse("a.b" in x)
        self.assertTrue('a' in x)
        self.assertEqual(x.pop('x.z', 20), 20)

    def test_popitem(self):
        x = NestedDict({"a": {"b": 1}})
        self.assertEqual(x.popitem('a.b'), ('a.b', 1))
        self.assertRaises(KeyError, x.popitem, "x.y")


# class Test(unittest.TestCase):
#
#     def test_create(self):
#         d = Nested_Dict()
#         self.assertEqual( len( d ) , 0 )
#         self.assertFalse( d.has_key("hello"))
#
#     def test_insert_simple(self):
#         d = Nested_Dict()
#         d.set_value( "hello", "world")
#         self.assertTrue( d.has_key( "hello"))
#         self.assertEqual( d.get_value("hello"), "world")
#
#     def test_key_error( self ):
#         d = Nested_Dict()
#         self.assertRaises(KeyError, d.get_value, "Bingo")
#
#     def test_set_value(self):
#         d = Nested_Dict()
#         d.set_value( "a", "b")
#         self.assertEqual( d.get_value( "a"), "b")
#
#     def test_set_value_nested(self):
#         x = Nested_Dict()
#
#         x.set_value( "member.name", "Joe Drumgoole")
#         self.assertEqual( x.get_value( "member"), { "name" : "Joe Drumgoole" })
#         name = x.get_value( "member.name")
#         self.assertEqual( name,"Joe Drumgoole")
#
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
