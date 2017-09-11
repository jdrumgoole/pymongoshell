'''
Created on 11 Sep 2017

@author: jdrumgoole
'''

import pprint

from mongodb_utils.bulkwriter import Pipeline, Sink

class Add_Field( Pipeline ):
    
    def __init__(self, name, value ):
        self._name = name
        self._value = value 

    def actor(self, doc ):
        doc[ self._name ] = self._value
        return doc
        
class Rename_Field( Pipeline ):
    
    def __init__(self, old_name, new_name ):
        self._old_name = old_name
        self._new_name = new_name
        
    def actor(self, doc ):
        if self._old_name in doc :
            v = doc[ self._old_name ]
            del doc[ self._old_name ]
            doc[ self._new_name ] = v
        return doc
    
class print_sink( Sink ):
    
    def ender(self, doc ):
        pprint.pprint( doc )
        
if __name__ == '__main__':
    
    printer = print_sink()
    adder = Add_Field( "hello", { "key" : 'hole'})
    renamer = Rename_Field( "hello" , "goodbye")
    
    pipe = adder.pour( renamer.pour( printer.drain()))
    for i in range( 5 ):
        pipe.send( { "doc_id" : i })