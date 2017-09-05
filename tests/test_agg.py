'''
Created on 21 Mar 2017

@author: jdrumgoole
'''
import os
import unittest
from datetime import  datetime
#import pprint

from mongodb_utils.agg import Agg, CursorFormatter
from mongodb_utils.mongodb import MongoDB

class Test(unittest.TestCase):

    def setUp(self):
        self._mdb = MongoDB( uri="mongodb://localhost:27017/testgg" )
        self._col = self._mdb.collection( "testgg" )
        for i in range( 50 ):
            self._col.insert_one( { "member" : { "name" : "Joe Drumgoole%s" % i,
                                                 "id"   : i,
                                                 "ts"   : datetime.utcnow() }})
        self._agg = Agg( self._col )
        self._formatter = None
        
        

        
    def tearDown(self): 
        self._mdb.drop_database()

    def testFormatter(self):
        self._agg.addMatch( { "member.name" : "Joe Drumgoole0" })
        #print( "agg: %s" % self._agg )
        self._agg.addProject( { "member.name" : 1,
                                "member.id" : 1,
                                "_id" : 0,
                                "member.ts" :1
                             })

        filename="JoeDrumgoole"
        ext = "json"
        self._formatter = CursorFormatter( self._agg, filename=filename, formatter=ext)
        self._formatter.output( fieldNames=[ "member.name", "member.id", "member.ts"], datemap=[ "member.ts"] )

        self.assertTrue( os.path.isfile( filename ))
        os.unlink( filename )
        
    def test_create_view(self):
        pass
    
    def testFieldMapper(self):
        
        doc = { "a" : "b"}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a' ])
        self.assertTrue( "a" in newdoc )
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f" }
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c' ])
        self.assertTrue("a" in newdoc )
        self.assertTrue("c" in  newdoc ) 
        self.assertFalse( "e" in newdoc )
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x"}}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( "a" in newdoc )
        self.assertTrue( "c" in newdoc )
        self.assertTrue( "z" in newdoc )
        self.assertTrue( "w" in newdoc[ "z"] )
        self.assertFalse( "e" in newdoc )
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w"])
        self.assertTrue( "a" in newdoc )
        self.assertTrue( "c" in newdoc)
        self.assertTrue( "z" in newdoc)
        self.assertTrue( "w" in newdoc["z"] )
        self.assertFalse( "e" in newdoc)
        self.assertFalse( "y" in newdoc[ 'z' ] )
        
        doc = { "a" : "b", 
                "c" : "d", 
                "e" : "f",
                "z" : { "w" : "x",
                        "y" : "p" },
                "g" : { "h" : "i",
                        "j" : "k" }}
        
        newdoc = CursorFormatter.fieldMapper( doc , [ 'a', 'c', "z.w", "g.j"])
        self.assertTrue( "a" in newdoc)
        self.assertTrue( "c" in newdoc)
        self.assertTrue( "z" in newdoc)
        self.assertTrue( "w" in newdoc["z"] )
        self.assertFalse( "e" in newdoc)
        self.assertFalse("y" in newdoc[ 'z' ] )
        self.assertTrue( "g" in newdoc)
        self.assertTrue( "j" in newdoc['g'] )
        self.assertFalse( "h" in newdoc['g'] )
        
        
    def test_dateMapField(self):
        
        test_doc = { "a" : 1, "b" : datetime.utcnow()}
        #pprint.pprint( test_doc )
        _ = CursorFormatter.dateMapField(test_doc, "b" )
        #pprint.pprint( new_doc )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
