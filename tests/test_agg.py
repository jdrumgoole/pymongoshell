'''
Created on 21 Mar 2017

@author: jdrumgoole
'''
import os
import unittest
import datetime
#import pprint

from mongodb_utils.agg import Agg, CursorFormatter
from mongodb_utils.mongodb import MongoDB

class Test(unittest.TestCase):

    def setUp(self):
        self._mdb = MongoDB( uri="mongodb://localhost:27017/test" )
        self._agg = Agg( self._mdb.collection( "test"))
        self._formatter = None

        
    def tearDown(self): 
        pass

    def testFormatter(self):
        self._agg.addMatch( { "batchID" : 47, "member.name" : "Joe Drumgoole" })
        #print( "agg: %s" % self._agg )
        self._agg.addProject( { "member.name" : 1,
                                "_id" : 0,
                                "member.joined" : 1,
                                "member.city" : 1,
                             })

        filename="JoeDrumgoole"
        ext = "json"
        self._formatter = CursorFormatter( self._agg, filename=filename, formatter=ext)
        self._formatter.output( fieldNames=[ "member.member_name", "member.join_time", "member.city"], datemap=[ "member.join_time"] )

        self.assertTrue( os.path.isfile( filename ))
        os.unlink( filename )
        
    def test_create_view(self):
        pass
    
    def testFieldMapper(self):
        
        doc = { "a" : "b"}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a' ])
        self.assertTrue( newdoc.has_key( "a" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f" }
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c' ])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" )) 
        self.assertFalse( newdoc.has_key( "e" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x"}}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        self.assertFalse( newdoc[ 'z' ].has_key( "y" ))
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" },
                "g" : { "h" : "i",
                        "j" : "k" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w", "g.j"])
        self.assertTrue( newdoc.has_key( "a" ))
        self.assertTrue( newdoc.has_key( "c" ))
        self.assertTrue( newdoc.has_key( "z" ))
        self.assertTrue( newdoc["z"].has_key( "w" ))
        self.assertFalse( newdoc.has_key( "e" ))
        self.assertFalse( newdoc[ 'z' ].has_key( "y" ))
        self.assertTrue( newdoc.has_key( "g" ))
        self.assertTrue( newdoc['g'].has_key( "j"))
        self.assertFalse( newdoc['g'].has_key( "h"))
        
        
    def test_dateMapField(self):
        
        test_doc = { "a" : 1, "b" : datetime.datetime.now()}
        #pprint.pprint( test_doc )
        _ = CursorFormatter.dateMapField(test_doc, "b" )
        #pprint.pprint( new_doc )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()