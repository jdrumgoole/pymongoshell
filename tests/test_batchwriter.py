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
        pass
    
    def _write(self, buf, loopSize ):
        
        bw = BatchWriter( self._c )
        writer = bw.bulkWrite( buf )
        for i in range( loopSize ) :
            print( { "v" : i } )
            writer.send( { "v" : i })
        
        cursor  = self._c.find()
        count = 0
        for i in cursor:
            print( "i : %s" % i )
            self.assertTrue( i[ "v"] == count  )
            count = count + 1 
                
        #self._db.drop_collection( "bwtest")
        return bw.written()
        
    def test_write(self):
        
        written = self._write( 1, 1)
        self.assertEqual( written, 1 )

        written = self._write( 2, 1)
        self.assertEqual( written, 0 )
        
        written = self._write( 10, 50 )
        self.assertEqual( written, 50 )
        
        written = self._write( 50, 50 )
        self.assertEqual( written, 50 )
        
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