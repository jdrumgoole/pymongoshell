'''
Created on 13 Dec 2016

@author: jdrumgoole
'''
import unittest
import pymongo

from batchwriter import BatchWriter

class Test(unittest.TestCase):

    def setUp(self):
        self._client = pymongo.MongoClient()
        self._db = self._client[ "test"]
        self._c = self._db[ "test" ]


    def tearDown(self):
        pass

    def _write(self, buf, loopSize ):
        
        bw = BatchWriter( self._c )
        writer = bw.bulkWrite( buf )
        totalInserted = 0 
        for i in range( loopSize ) :
            r = writer.send( { "v" : i })
            if r is not None and r[ 'nInserted' ] > 0  :
                #print( r )
                totalInserted =r[ 'nInserted' ] + totalInserted
        
        return totalInserted
        
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