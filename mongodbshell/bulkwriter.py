'''

Use a generator function to recieve data from the send command. Accumulate docs until
writeLimit is reached and then bulkexecute writes. Keep a count of write ops in
writeCount.

Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo
import bson

from mongodbshell.generator_utils import coroutine


def no_op(new_name, d):
    _ = new_name
    return d


def feedback_nop(doc):
    _ = doc
    print(".")


class Pipeline:
       
    def actor(self, doc):
        return doc
    
    @coroutine  
    def pour(self,destination):
        while True:
            doc = (yield)
            destination.send(self.actor(doc))


class Sink:
        
    def end_it(self, doc):
        pass 
    
    @coroutine
    def drain(self):
        while True:
            doc = (yield)
            self.end_it(doc)


class BulkWriter:
    """
    Bulk_Writer
    ==================
    Bulk_Writer is a wrapper class for the bulk_write operation in mongodb. It allows user
    to send (using generator send operations) write and update operations to MongoDB which accumulates 
    them up a batch_size threshold. Once the threshold is met the operations are committed to the server.
    
    In the event that the generator is destroyED before completing its write operations then the generator exit
    exception that is called will force remaining writes to be completed.
    """
     
    def __init__(self, collection, transform_func=None, new_doc_name=None, feedback=None):
         
        self._collection = collection
        self._orderedWrites = False
        if transform_func is None:
            self._processFunc = no_op
        else:
            self._processFunc = transform_func
            
        if new_doc_name is None:
            self._new_doc_name = ""
        else:
            self._new_doc_name = new_doc_name
            
        self._writeCount = 0

        self._feedback = feedback
        
    def written(self):
        return self._writeCount
    
    '''
    Intialise coroutine automatically
    '''
    @coroutine 
    def __call__(self, write_limit=1000):

        try:
            if self._orderedWrites:
                bulk_op = self._collection.initialize_ordered_bulk_op()
            else:
                bulk_op = self._collection.initialize_unordered_bulk_op()
                
            bulk_count = 0
            
            try:
                while True:
                    doc = (yield)
                    if self._feedback:
                        self._feedback(doc)
                    # pprint.pprint( doc ))
                    bulk_op.insert(self._processFunc(self._new_doc_name, doc))
                    bulk_count += 1
                    if bulk_count == write_limit:
                        result = bulk_op.execute()
                        self._writeCount = self._writeCount + result['nInserted']
                        if self._orderedWrites:
                            bulk_op = self._collection.initialize_ordered_bulk_op()
                        else:
                            bulk_op = self._collection.initialize_unordered_bulk_op()
                             
                        bulk_count = 0
            except GeneratorExit:
                if bulk_count > 0:
                    result = bulk_op.execute()
                    self._writeCount = self._writeCount + result['nInserted']
            except bson.errors.InvalidDocument as e:
                print("Invalid Document")
                print(f"bson.errors.InvalidDocument: {e}")
                raise
            
        except pymongo.errors.BulkWriteError as e :
            print(f"Bulk write error : {e.details}")
            raise
        

