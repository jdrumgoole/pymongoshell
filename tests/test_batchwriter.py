'''
Created on 13 Dec 2016

@author: jdrumgoole
'''
import unittest
import pymongo

from mongodb_utils.batchwriter import BatchWriter

class Test(unittest.TestCase):

    def setUp(self):
        self._client = pymongo.MongoClient()
        self._db = self._client[ "bwtest"]
        self._c = self._db[ "bwtest" ]
        self._db.drop_collection( "bwtest")


    def tearDown(self):
        #self._client.drop_database( "bwtest")
        self._db.drop_collection( "bwtest")
    
    @staticmethod
    def _feedback( doc ):
        print( "send( %s )" % doc )
        
    def _write(self, write_limit, doc_count ):
        
        bw = BatchWriter( self._c ) #feedback=Test._feedback )
        writer = bw.bulkWrite( write_limit )
        for i in range( doc_count ) :
            #print( { "v" : i } )
            writer.send( { "v" : i })
        
        writer.close()
        cursor  = self._c.find()
        count = 0
        for i in cursor:
            self.assertEqual( i[ "v"], count  )
            count = count + 1 
                

        return bw.written()
        
    def test_write(self):
        self._db.drop_collection( "bwtest")
        written = self._write( 1, 1)
        self.assertEqual( written, self._c.count() )
        self._db.drop_collection( "bwtest")

        written = self._write( 2, 1)
        self.assertEqual( written, 1 )
        self.assertEqual( self._c.count(), 1 )
        self._db.drop_collection( "bwtest")
        
        written = self._write( 2, 2 )
        self.assertEqual( written, 2 )
        self.assertEqual( self._c.count(), 2 )
        self._db.drop_collection( "bwtest")
        
        written = self._write( 10, 50 )
        self.assertEqual( written, 50 )
        self.assertEqual( self._c.count(), 50 )
        self._db.drop_collection( "bwtest")
        
        written = self._write( 50, 50 )
        self.assertEqual( written, 50 )
        self.assertEqual( self._c.count(), 50 )
        self._db.drop_collection( "bwtest")
        
#         bw = BatchWriter( self._c )
#         writer = bw.bulkWrite( 50 )
#         totalInserted = 0 
#         for i in range( 50 ) :
#             r = writer.send( { "v" : i })
#             if r is not None :
#                 print( r )
#                 totalInserted =r[ 'nInserted' ] + totalInserted
#         
#         self.assertEqual( totalInserted, 5000 )
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()