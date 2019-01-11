'''
Created on 4 Apr 2017

@author: jdrumgoole
'''


class NestedDict(dict):

    def _key_split(self, key):
        if isinstance(key, str):
            return key.split('.')
        else:
            raise ValueError("Expected a <str> type")

    def _has_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict.__contains__(d, keys[0]):
                return self._has_nested(d[keys[0]], keys[1:])
            else:
                return False
        else:
            return dict.__contains__(d, keys[0])

    def _get_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._get_nested(d[keys[0]], keys[1:])
            else:
                raise KeyError(f"no such key:{keys[0]}")
        else:
            return dict.__getitem__(d, keys[0])

    def _set_nested(self, d, keys, value):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._set_nested(d[keys[0]], keys[1:], value)
            else:
                dict.__setitem__(d, keys[0], {})
        else:
            dict.__setitem__(d, keys[0], value)

    def _del_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._del_nested(d[keys[0]], keys[1:])
            else:
                dict.__delitem__(d, keys[0])
        else:
            dict.__delitem__(d, keys[0])

    def __contains__(self, key):
        return self._has_nested(self, key.split('.'))

    def __getitem__(self, item):
        return self._get_nested(self, item.split('.'))

    def __setitem__(self, key, value):
        self._set_nested(self, key.split('.'), value)

    def get(self, key, default_value=None):
        try:
            return self._get_nested(self, key.split('.'))
        except KeyError:
            return default_value

    def has_key(self, key):
        try:
            return self._get_nested(self, key.split('.'))
        except KeyError:
            return False

    def __delitem__(self, key):
        self._del_nested(self, key.split('.'))

    def pop(self, key, default_value=None):
        v=None
        try:
            v = self._get_nested(self, key.split('.'))
            self._del_nested(self, key.split('.'))
        except KeyError:
            v = default_value

        return v

    def popitem(self, key):
        v=None
        v = self._get_nested(self, key.split('.'))
        self._del_nested(self, key.split('.'))
        return key, v





class Nested_Dict( object ):
    '''
    Allow dotted access of nested dicts.
    so :
    a[ "x.y.z" ] = 1 is equivalent to a[ x[ y[ z ]]] = 1
    
    a = { x : { y : z }}}
    '''
    
    def __init__(self, d=None):
        
        if d is None:
            self._dict = {}
        elif isinstance( d, dict ):
            self._dict = d
        else:
            raise ValueError( "d is not a dict type")

    def dict_value(self ):
        return self._dict
    
    def get_value( self, k ):
        keys = k.split( ".", 1 )
        
        #print( "get_value %s" % k  )
        if len( keys ) == 1 :
            #print( "len(keys) : 1")
            return self._dict[ keys[ 0 ]]
        elif keys[ 0 ] in self._dict :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist in keys %s of %s" % ( keys[ 0 ], keys, self._dict ))
        
        if isinstance( nested, dict ) :
            return Nested_Dict( nested ).get_value( '.'.join(keys[ 1:len( keys )]))

        else:
            return nested
    
    def __len__(self):
        return len( self._dict )
    
    def has_key( self, k ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            return keys[ 0 ] in self._dict
        elif keys[ 0 ] in self._dict :
                nested = self._dict[ keys[ 0 ]]
        else:
            raise ValueError( "nested key :'%s' does not exist" % keys[ 0 ])
        
        if isinstance( nested, dict ) :
            return keys[ 1 ] in Nested_Dict( nested ).dict_value()

        else:
            return True
                      
        
    def set_value( self, k, v ):
        
        keys = k.split( ".", 1 )
        nested = None
        if len( keys ) == 1 :
            self._dict[ keys[ 0 ]] = v
            return self
        elif keys[ 0 ] in self._dict :
            nested = self._dict[ keys[ 0 ]]
        else:
            self._dict[ keys[ 0 ]] = {}
            nested = self._dict[ keys[ 0 ]]
        
        if isinstance( nested, dict ) :

            return Nested_Dict( nested ).set_value( '.'.join( keys[ 1:len( keys ) ]), v  )
        else:
            self._dict[ keys[ 0 ]] = v
             
        return self

# class dotted_dict( dict ):
#     '''
#     Allow dotted access of nested dicts.
#     so :
#     a[ "x.y.z" ] = 1 is equivalent to a[ x[ y[ z ]]] = 1
#     
#     a = { x : { y : z }}}
#     '''
#     def __init__( self, *args, **kwargs ):
#         super( dotted_dict, self).__init__( *args, **kwargs )
# 
# 
#     def dict_value(self ):
#         return self._dict
#     
#     def get_value( self, k ):
#         keys = k.split( ".", 1 )
#         
#         #print( "get_value %s" % k  )
#         if len( keys ) == 1 :
#             #print( "len(keys) : 1")
#             return self._dict[ keys[ 0 ]]
#         elif self._dict.has_key( keys[ 0 ]) :
#                 nested = self._dict[ keys[ 0 ]]
#         else:
#             raise ValueError( "nested key :'%s' does not exist in keys %s of %s" % ( keys[ 0 ], keys, self._dict ))
#         
#         if isinstance( nested, dict ) :
#             nested = NestedDict( nested )
#             return nested.get_value( keys[ 1 ] )
#         else:
#             return nested
#     
#     def has_key( self, k ):
#         
#         keys = k.split( ".", 1 )
#         nested = None
#         if len( keys ) == 1 :
#             return self._dict.has_key( keys[ 0 ] )
#         elif self._dict.has_key( keys[ 0 ]) :
#                 nested = self._dict[ keys[ 0 ]]
#         else:
#             raise ValueError( "nested key :'%s' does not exist" % keys[ 0 ])
#         
#         if isinstance( nested, dict ) :
#             nested = NestedDict( nested )
#             return nested.has_key( keys[ 1 ] )
#         else:
#             return True
#                       
#         
#     def set_value( self, k, v ):
#         
#         keys = k.split( ".", 1 )
#         nested = None
#         if len( keys ) == 1 :
#             self._dict[ keys[ 0 ]] = v
#             return self
#         elif self._dict.has_key( keys[ 0 ]) :
#             nested = self._dict[ keys[ 0 ]]
#         else:
#             self._dict[ keys[ 0 ]] = {}
#             nested = self._dict[ keys[ 0 ]]
#         
#         if isinstance( nested, dict ) :
#             nested = NestedDict( nested )
#             nested.set_value( keys[ 1 ], v )
#             return self
