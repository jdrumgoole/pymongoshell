# mongodbshell :  MongoDB in the python shell

The Python shell is the ideal environment for Python developers to interact
with MongoDB. However output cursors and interacting with the database requires
a little more boilerplate than is convenient. the `mongodbshell` package 
provides a set a convenience functions and objects to allow easier
interaction with MongoDB via the Python interpreter. 

The key value adds over the MongoDB Shell and just using the standard pymongo
package are:

 * Proper pagination of output including single document results
 * Pretty printing of output
 * Ability to stream output to a file in parallel to the screen
 * Full compatibility with pymongo API
 * Access to the full capabilities of the Python and iPython shells

## Installation

you can install the software with pip3 or pipenv. The `mongodbshell` only
supports Python 3. 

```shell script
$ pip3 install mongodbshell
```

## Using the mongodbshell

First we create a `MongoClient` object. This is a proxy for all the 
commands we can run using `MongoDBShell`. It is exaclty analogous to 
the PyMongo `MongoClient` and is in fact just a shim. 

```python
>>> import mongodbshell
>>> c = mongodbshell.MongoClient()
mongodbshell 1.1.0b5
Using collection 'test.test'
Server selection timeout set to 5.0 seconds
>>> c
mongodbshell.MongoClient(banner=True,
                         database_name='test',
                         collection_name='test',
                         host= 'mongodb://localhost:27017')
>>>
```

We can also access the native `MongoClient` object by using the `.client` property.

```python
>>> c.client
MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True, serverselectiontimeoutms=5000)
>>>
```

Each `mongodbshell.MongoClient` object has a set of standard properties:
```python
>>> c.database
Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True, serverselectiontimeoutms=5000), 'test')
>>> c.collection
Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True, serverselectiontimeoutms=5000), 'test'), 'test')
>>> c.uri
'mongodb://localhost:27017'
>>> c.database_name
'test'
>>> c.collection_name
'test.test'
>>>
```

There are also convenience functions for the most popular operations:

## is_master

The [`is_master`](https://docs.mongodb.com/manual/reference/method/db.isMaster/) command returns the status and configuration of the Mongod server 
and/or cluster thatthe client is connected to. This represents the typical 
results from a single`mongod` running locally. The `is_master` is the canonical
way to determine if a client is connected to a `mongod` or `mongod` cluster.
```python
>>> c.is_master()
1  : {'connectionId': 9,
2  :  'ismaster': True,
3  :  'localTime': datetime.datetime(2020, 4, 1, 11, 32, 46, 753000),
4  :  'logicalSessionTimeoutMinutes': 30,
5  :  'maxBsonObjectSize': 16777216,
6  :  'maxMessageSizeBytes': 48000000,
7  :  'maxWireVersion': 8,
8  :  'maxWriteBatchSize': 100000,
9  :  'minWireVersion': 0,
10 :  'ok': 1.0,
11 :  'readOnly': False}
>>>
```

## insert_one
The [`insert_one`](https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.insert_one) 
operation adds a single document to the default collection
defined by `c.collection`. 
```
>>> c.insert_one({"name" : "Joe Drumgoole", "twitter_handle" : "@jdrumgoole"})
Inserted Id: 5e86748c5b17a01d0057d41a acknowledged: True
```

You should be aware that PyMongo updates the document you pass into it and adds
an `_id` field which you can see in the result string. This `_id` is also added
to the argument. 

```python
>>> c.insert_one(d1)
Inserted Id: 5e8739e95b17a01d0057d41b acknowledged: True
>>> c.find_one(d1)
1  : {'_id': ObjectId('5e8739e95b17a01d0057d41b'), 'name': 'Heracles'}
>>> c.insert_one(d1)
DuplicateKeyError:
{'code': 11000,
 'errmsg': 'E11000 duplicate key error collection: test.test index: _id_ dup '
           "key: { _id: ObjectId('5e8739e95b17a01d0057d41b') }",
 'index': 0,
 'keyPattern': {'_id': 1},
 'keyValue': {'_id': ObjectId('5e8739e95b17a01d0057d41b')}}
>>>
```

So if you insert a document that has just been inserted you will get a 
**DuplicateKeyError**. To to this successfully you need to ` del d1["_id"]` 
before doing the insert. 

## insert_many
We use the [`insert_many`](https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.insert_many)
when we want to insert multiple documents. This is much more efficient than inserting
individual documents as we avoid a network round trip for each document inserted.

```python
>>> d1 = {"name" : "Heracles"}
>>> d2 = {"name" : "Orpheus"}
>>> d3 = {"name" : "Jason"}
>>> d4 = {"name" : "Odysseus"}
>>> d5 = {"name" : "Achilles"}
>>> d6 = {"name" : "Menelaeus"}
>>> c.insert_many([d1,d2,d3,d4,d5])
1  : [ObjectId('5e8753c05b17a04ccc18e27b'),
2  :  ObjectId('5e8753c05b17a04ccc18e27c'),
3  :  ObjectId('5e8753c05b17a04ccc18e27d'),
4  :  ObjectId('5e8753c05b17a04ccc18e27e'),
5  :  ObjectId('5e8753c05b17a04ccc18e27f')]
>>>
```
## find_one
The [`find_one`](https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one)
operation queries for a single instance of a document in the current collection
defined by `c.collection`.

Assuming we have inserted the following data:
```python
>>> p1 = {"name" : "Joe Drumgoole",
...       "social": ["twitter", "instagram", "linkedin"],
...       "mobile": "+353 87xxxxxxx",
...       "email" : "Joe.Drumgoole@mongodb.com"}
>>> p2 = {"name" : "Hercules Mulligan",
...       "social": ["twitter", "linkedin"],
...       "mobile": "+1 12345678",
...       "email" : "Hercules.Mulligan@example.com"}
>>> p3 = {"name" : "Aaron Burr",
...       "social": ["instagram"],
...       "mobile": "+1 67891011",
...       "email" : "Aaron.Burr@example.com"}
>>> c.insert_many([p1,p2,p3])
1  : [ObjectId('5e8759c55b17a04ccc18e280'),
2  :  ObjectId('5e8759c55b17a04ccc18e281'),
3  :  ObjectId('5e8759c55b17a04ccc18e282')]
```

Lets find *Hercules Mulligan*. 
```
>>> c.find_one({"name" : "Hercules Mulligan"})
1  : {'_id': ObjectId('5e8759c55b17a04ccc18e281'),
2  :  'email': 'Hercules.Mulligan@example.com',
3  :  'mobile': '+1 12345678',
4  :  'name': 'Hercules Mulligan',
5  :  'social': ['twitter', 'linkedin']}
>>>
```

The `find_one` command will do what it says on the tin. Find the first element of 
any search in [natural order](https://docs.mongodb.com/manual/reference/glossary/#term-natural-order).
It will only ever return one document. In order to return a set of documents we 
need `find`.

##find
[`find`](https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find) 
will return the complete set of documents that match a query. These documents 
are returned in a [`cursor`](https://api.mongodb.com/python/2.8/api/pymongo/cursor.html) 
object. The PyMongo cursor is a standard python iterator. However to iterate
this cursor in the shell would be a tedious process of issuing `next()` calls or
writing your own `for` loop. The `mongodbshell` automatically prints out the 
results of the cursors returned by any shell commmand. The class comes with a
number of default settings.

```python
>>> c.paginate
True
>>> c.pretty_print
True
>>> c.line_numbers
True
>>>
```

### Paginate
Pagination ensures that the results of the output don't scroll off the screen. 
The pagination uses the screen dimensions to properly format and wrap the output
so that regardless of screen size changes the output can always be viewed. The 
viewport is recalcuated dynamically so the user can change the terminal window
size while paging throughout. Pagination can be turned off by setting `paginate`
to false.
```python
>>> c.paginate=False
>>> c.paginate
False
```

### pretty_print
Pretty printing is used to ensure that the JSON documents output are properly
formatted and easy to read. For small documents turning pretty printing off will
result in the documents printing on a single line which can sometimes be easier
to read.

To turn off `pretty_print` just set the value to `False`.
```python
>>> c.pretty_print=False
>>>
```
### line_numbers
Line numbers are added by default to allow a user to keep track of location
in a large stream output. Similarily to the other properties `line_numbers`
can be toggled on and off by settting the flag.
```python
>>> c.line_numbers=False
>>>
```

## Find Examples

### Find all documents
```python
>>> c.find()
1  : {'_id': ObjectId('5e8752f35b17a01d0057d423'), 'name': 'Heracles'}
2  : {'_id': ObjectId('5e8752f35b17a01d0057d424'), 'name': 'Orpheus'}
3  : {'_id': ObjectId('5e8752f35b17a01d0057d425'), 'name': 'Jason'}
4  : {'_id': ObjectId('5e8752f35b17a01d0057d426'), 'name': 'Odysseus'}
5  : {'_id': ObjectId('5e8752f35b17a01d0057d427'), 'name': 'Achilles'}
6  : {'_id': ObjectId('5e8753c05b17a04ccc18e27b'), 'name': 'Heracles'}
7  : {'_id': ObjectId('5e8753c05b17a04ccc18e27c'), 'name': 'Orpheus'}
8  : {'_id': ObjectId('5e8753c05b17a04ccc18e27d'), 'name': 'Jason'}
9  : {'_id': ObjectId('5e8753c05b17a04ccc18e27e'), 'name': 'Odysseus'}
10 : {'_id': ObjectId('5e8753c05b17a04ccc18e27f'), 'name': 'Achilles'}
11 : {'_id': ObjectId('5e8759c55b17a04ccc18e280'),
12 :  'email': 'Joe.Drumgoole@mongodb.com',
13 :  'mobile': '+353 87xxxxxxx',
14 :  'name': 'Joe Drumgoole',
15 :  'social': ['twitter', 'instagram', 'linkedin']}
16 : {'_id': ObjectId('5e8759c55b17a04ccc18e281'),
17 :  'email': 'Hercules.Mulligan@example.com',
18 :  'mobile': '+1 12345678',
19 :  'name': 'Hercules Mulligan',
20 :  'social': ['twitter', 'linkedin']}
21 : {'_id': ObjectId('5e8759c55b17a04ccc18e282'),
22 :  'email': 'Aaron.Burr@example.com',
23 :  'mobile': '+1 67891011',
24 :  'name': 'Aaron Burr',
25 :  'social': ['instagram']}
>>>
```
### Find all documents with an instagram social setting

Note that MongoDB knows to look inside an array when the target
field is an array.

>>> c.find({'social':'instagram'})
1  : {'_id': ObjectId('5e8759c55b17a04ccc18e280'),
2  :  'email': 'Joe.Drumgoole@mongodb.com',
3  :  'mobile': '+353 87xxxxxxx',
4  :  'name': 'Joe Drumgoole',
5  :  'social': ['twitter', 'instagram', 'linkedin']}
6  : {'_id': ObjectId('5e8759c55b17a04ccc18e282'),
7  :  'email': 'Aaron.Burr@example.com',
8  :  'mobile': '+1 67891011',
9  :  'name': 'Aaron Burr',
10 :  'social': ['instagram']}
>>>
>
## coll_stats 
The [`coll_stats`](https://docs.mongodb.com/manual/reference/command/collStats/)
command returns collection stats for the current collection defined by `c.collection`.
There is no directly analogous command in PyMongo. In instead it is constructed
using the [`command`](https://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.command) operation. 
function in PyMongo.

## command
Many admin operations in MongoDB are too esoteric to warrant a specific API call in the
driver. For these operations we support the generic 
[`command`](https://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.command) 
option. 
```python
>>> c.command('buildinfo')
1  : {'allocator': 'tcmalloc',
2  :  'bits': 64,
3  :  'buildEnvironment': {'cc': 'cl: Microsoft (R) C/C++ Optimizing Compiler '
4  :                             'Version 19.16.27032.1 for x64',
5  :                       'ccflags': '/nologo /EHsc /W3 /wd4068 /wd4244 /wd4267 '
6  :                                  '/wd4290 /wd4351 /wd4355 /wd4373 /wd4800 '
7  :                                  '/wd5041 /wd4291 /we4013 /we4099 /we4930 /WX '
8  :                                  '/errorReport:none /MD /O2 /Oy- /bigobj '
9  :                                  '/utf-8 /permissive- /Zc:__cplusplus '
10 :                                  '/Zc:sizedDealloc /volatile:iso '
11 :                                  '/diagnostics:caret /std:c++17 /Gw /Gy '
12 :                                  '/Zc:inline',
13 :                       'cxx': 'cl: Microsoft (R) C/C++ Optimizing Compiler '
14 :                              'Version 19.16.27032.1 for x64',
15 :                       'cxxflags': '/TP',
16 :                       'distarch': 'x86_64',
17 :                       'distmod': '2012plus',
18 :                       'linkflags': '/nologo /DEBUG /INCREMENTAL:NO '
19 :                                    '/LARGEADDRESSAWARE /OPT:REF',
20 :                       'target_arch': 'x86_64',
21 :                       'target_os': 'windows'},
22 :  'debug': False,
23 :  'gitVersion': 'a4b751dcf51dd249c5865812b390cfd1c0129c30',
24 :  'javascriptEngine': 'mozjs',
25 :  'maxBsonObjectSize': 16777216,
26 :  'modules': [],
27 :  'ok': 1.0,
28 :  'openssl': {'running': 'Windows SChannel'},
29 :  'storageEngines': ['biggie', 'devnull', 'ephemeralForTest', 'wiredTiger'],
30 :  'sysInfo': 'deprecated',
31 :  'targetMinOS': 'Windows 7/Windows Server 2008 R2',
32 :  'version': '4.2.0',
33 :  'versionArray': [4, 2, 0, 0]}
>>>
```

## count_documents
To accurately count a number of documents in a collection we can use the 
[`count_documents`](https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.count_documents)
operation. You can apply a filter to limit the number of documents returned.

In this example lets connect to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 
database hosted in the cloud. 
```python
c=mongodbshell.MongoClient("mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true")
mongodbshell 1.1.0b5
Using collection 'test.test'
Server selection timeout set to 5.0 seconds
>>> c.collection="demo.zipcodes"
>>> c.count_documents()
29350
>>> c.count_documents({"city" : "NEW YORK"})
40
>>>
```
This tells us there are 29350 zip codes in the USA and 49 in New York. This is an
old data set so those numbers may not be quite up to date with the latest
US zipcodes. 


## aggregate
The [`aggregate`](https://docs.mongodb.com/manual/aggregation/) command allows 
users to submit a list of 
[`aggregation operations`](https://docs.mongodb.com/manual/reference/operator/aggregation/) 
that will be processed in sequence on the server.

In this example lets connect to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 
database hosted in the cloud. We will calculate the total zipcodes in New York
but this time we will use aggregation.

```python
c=mongodbshell.MongoClient("mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true")
mongodbshell 1.1.0b5
Using collection 'test.test'
Server selection timeout set to 5.0 seconds
>>> c.collection="demo.zipcodes"
>>> c.aggregate([{"$match" : {"city": "NEW YORK"}}, {"$count": "NYC_zipcodes_total"}])
1  : {'NYC_zipcodes_total': 40}
>>>
```
This is identical to the `count_documents` example above. To show the power of
the aggregation framework let's use it to find the population of each of the zipcodes
in New York city.

```python
>>> c.aggregate([{"$match" : {"city": "NEW YORK"}}, {"$group" : { "_id":"$_id", "zipcode_total" : { "$sum" : "$pop" }}}])
1  : {'_id': '10020', 'zipcode_total': 393}
2  : {'_id': '10036', 'zipcode_total': 16748}
3  : {'_id': '10012', 'zipcode_total': 26365}
4  : {'_id': '10030', 'zipcode_total': 21132}
5  : {'_id': '10039', 'zipcode_total': 25293}
6  : {'_id': '10003', 'zipcode_total': 51224}
7  : {'_id': '10009', 'zipcode_total': 57426}
8  : {'_id': '10006', 'zipcode_total': 119}
9  : {'_id': '10026', 'zipcode_total': 28453}
10 : {'_id': '10007', 'zipcode_total': 3374}
11 : {'_id': '10010', 'zipcode_total': 24907}
12 : {'_id': '10037', 'zipcode_total': 14982}
13 : {'_id': '10128', 'zipcode_total': 52311}
14 : {'_id': '10280', 'zipcode_total': 5574}
15 : {'_id': '10011', 'zipcode_total': 46560}
16 : {'_id': '10028', 'zipcode_total': 42757}
17 : {'_id': '10035', 'zipcode_total': 28099}
18 : {'_id': '10023', 'zipcode_total': 57385}
19 : {'_id': '10025', 'zipcode_total': 100027}
20 : {'_id': '10027', 'zipcode_total': 54631}
21 : {'_id': '10022', 'zipcode_total': 31870}
22 : {'_id': '10033', 'zipcode_total': 58648}
23 : {'_id': '10019', 'zipcode_total': 36602}
24 : {'_id': '10034', 'zipcode_total': 41131}
25 : {'_id': '10017', 'zipcode_total': 12465}
26 : {'_id': '10005', 'zipcode_total': 202}
27 : {'_id': '10002', 'zipcode_total': 84143}
28 : {'_id': '10032', 'zipcode_total': 61332}
29 : {'_id': '10044', 'zipcode_total': 8190}
30 : {'_id': '10018', 'zipcode_total': 4834}
31 : {'_id': '10021', 'zipcode_total': 106564}
32 : {'_id': '10016', 'zipcode_total': 51561}
33 : {'_id': '10038', 'zipcode_total': 14015}
34 : {'_id': '10040', 'zipcode_total': 39780}
35 : {'_id': '10013', 'zipcode_total': 21860}
36 : {'_id': '10029', 'zipcode_total': 74643}
37 : {'_id': '10031', 'zipcode_total': 55989}
38 : {'_id': '10024', 'zipcode_total': 65141}
39 : {'_id': '10014', 'zipcode_total': 31147}
40 : {'_id': '10001', 'zipcode_total': 18913}
>>>
```
## Line Numbers on Output 

Line numbers are added to output by default. You can turn off line numbers by
setting the `line_numbers` flag to false.

```python
>>> client.insert_one({"name" : "Joe Drumgoole", "twitter_handle" : "@jdrumgoole"})
ObjectId('5c3f4f2fc3b498d6674b08f0')
>>> client.find_one( {"name" : "Joe Drumgoole"})
1    {'_id': ObjectId('5c3f4b04c3b498d4a1c6ce22'),
2     'name': 'Joe Drumgoole',
3     'twitter_handle': '@jdrumgoole'}
>>> client.line_numbers = False                      # Turn off line numbers
>>> client.find_one( {"name" : "Joe Drumgoole"})
{'_id': ObjectId('5c3f4b04c3b498d4a1c6ce22'),
 'name': 'Joe Drumgoole',
 'twitter_handle': '@jdrumgoole'}
>>>
```
## Connecting to a specific MongoDB URI

You can connect to a different database by using the `MongoDB` class. Here is an
example connection to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) hosted database. 

The example below is a live read-only database. You can try it out at the 
MongoDB URI:

```shell script
"mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true"
```

In the `mongodbshell`:

```python
>>> from mongodbshell import MongoDB
>>> atlas=MongoDB(uri="mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true", database="demo", collection="zipcodes")
>>> atlas.find_one()
1    {'_id': '01069',
2     'city': 'PALMER',
3     'loc': [-72.328785, 42.176233],
4     'pop': 9778,
5     'state': 'MA'}

```

## Looking at large volumes of output

If you run a query in the python shell it will return a cursor. To look at
the objects in the cursor using the PyMongo library you need to either 
write a loop to consume the cursor or explicitly call `next()` on each cursor item.

```python
>>> c=pymongo.MongoClient("mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true")
>>> db=c["demo"]
>>> collection=db["zipcodes"]
>>> collection.find()
<pymongo.cursor.Cursor object at 0x105bf1d68>
>>> cursor=collection.find()
>>> next(cursor)
{'_id': '01069', 'city': 'PALMER', 'loc': [-72.328785, 42.176233], 'pop': 9778, 'state': 'MA'}
>>> next(cursor)
{'_id': '01002', 'city': 'CUSHMAN', 'loc': [-72.51565, 42.377017], 'pop': 36963, 'state': 'MA'}
>>>
```

This is tedious and becomes even more so when the objects are large enough to
scroll off the screen. This is not a problem with the `mongodbshell` as the
`MongoClient` object will automatically handle pretty printing and paginating output. 

```python
>>> atlas.find()
1    {'_id': '01069', 'city': 'PALMER', 'loc': [-72.328785, 42.176233], 'pop': 9778, 'state': 'MA'}
2    {'_id': '01002', 'city': 'CUSHMAN', 'loc': [-72.51565, 42.377017], 'pop': 36963, 'state': 'MA'}
3    {'_id': '01012', 'city': 'CHESTERFIELD', 'loc': [-72.833309, 42.38167], 'pop': 177, 'state': 'MA'}
4    {'_id': '01073', 'city': 'SOUTHAMPTON', 'loc': [-72.719381, 42.224697], 'pop': 4478, 'state': 'MA'}
5    {'_id': '01096', 'city': 'WILLIAMSBURG', 'loc': [-72.777989, 42.408522], 'pop': 2295, 'state': 'MA'}
6    {'_id': '01262', 'city': 'STOCKBRIDGE', 'loc': [-73.322263, 42.30104], 'pop': 2200, 'state': 'MA'}
7    {'_id': '01240', 'city': 'LENOX', 'loc': [-73.271322, 42.364241], 'pop': 5001, 'state': 'MA'}
8    {'_id': '01370', 'city': 'SHELBURNE FALLS', 'loc': [-72.739059, 42.602203], 'pop': 4525, 'state': 'MA'}
9    {'_id': '01340', 'city': 'COLRAIN', 'loc': [-72.726508, 42.67905], 'pop': 2050, 'state': 'MA'}
10   {'_id': '01462', 'city': 'LUNENBURG', 'loc': [-71.726642, 42.58843], 'pop': 9117, 'state': 'MA'}
11   {'_id': '01473', 'city': 'WESTMINSTER', 'loc': [-71.909599, 42.548319], 'pop': 6191, 'state': 'MA'}
12   {'_id': '01510', 'city': 'CLINTON', 'loc': [-71.682847, 42.418147], 'pop': 13269, 'state': 'MA'}
13   {'_id': '01569', 'city': 'UXBRIDGE', 'loc': [-71.632869, 42.074426], 'pop': 10364, 'state': 'MA'}
14   {'_id': '01775', 'city': 'STOW', 'loc': [-71.515019, 42.430785], 'pop': 5328, 'state': 'MA'}
Hit Return to continue (q or quit to exit)
```
Pagination will dynamically adjust to screen height.

## Outputting to a file

The `MongoDB` class can send output to a file by setting the `output_file` property
on the `MongoDB` class. 

```python
>>> atlas.output_file="zipcodes.txt"
>>> atlas.find()
Output is also going to 'zipcodes.txt'
1    {'_id': '01069', 'city': 'PALMER', 'loc': [-72.328785, 42.176233], 'pop': 9778, 'state': 'MA'}
2    {'_id': '01002', 'city': 'CUSHMAN', 'loc': [-72.51565, 42.377017], 'pop': 36963, 'state': 'MA'}
3    {'_id': '01012', 'city': 'CHESTERFIELD', 'loc': [-72.833309, 42.38167], 'pop': 177, 'state': 'MA'}
4    {'_id': '01073', 'city': 'SOUTHAMPTON', 'loc': [-72.719381, 42.224697], 'pop': 4478, 'state': 'MA'}
5    {'_id': '01096', 'city': 'WILLIAMSBURG', 'loc': [-72.777989, 42.408522], 'pop': 2295, 'state': 'MA'}
6    {'_id': '01262', 'city': 'STOCKBRIDGE', 'loc': [-73.322263, 42.30104], 'pop': 2200, 'state': 'MA'}
7    {'_id': '01240', 'city': 'LENOX', 'loc': [-73.271322, 42.364241], 'pop': 5001, 'state': 'MA'}
8    {'_id': '01370', 'city': 'SHELBURNE FALLS', 'loc': [-72.739059, 42.602203], 'pop': 4525, 'state': 'MA'}
9    {'_id': '01340', 'city': 'COLRAIN', 'loc': [-72.726508, 42.67905], 'pop': 2050, 'state': 'MA'}
10   {'_id': '01462', 'city': 'LUNENBURG', 'loc': [-71.726642, 42.58843], 'pop': 9117, 'state': 'MA'}
11   {'_id': '01473', 'city': 'WESTMINSTER', 'loc': [-71.909599, 42.548319], 'pop': 6191, 'state': 'MA'}
12   {'_id': '01510', 'city': 'CLINTON', 'loc': [-71.682847, 42.418147], 'pop': 13269, 'state': 'MA'}
13   {'_id': '01569', 'city': 'UXBRIDGE', 'loc': [-71.632869, 42.074426], 'pop': 10364, 'state': 'MA'}
14   {'_id': '01775', 'city': 'STOW', 'loc': [-71.515019, 42.430785], 'pop': 5328, 'state': 'MA'}
>>> print(open('zipcodes.txt').read())
{'_id': '01069', 'city': 'PALMER', 'loc': [-72.328785, 42.176233], 'pop': 9778, 'state': 'MA'}
{'_id': '01002', 'city': 'CUSHMAN', 'loc': [-72.51565, 42.377017], 'pop': 36963, 'state': 'MA'}
{'_id': '01012', 'city': 'CHESTERFIELD', 'loc': [-72.833309, 42.38167], 'pop': 177, 'state': 'MA'}
{'_id': '01073', 'city': 'SOUTHAMPTON', 'loc': [-72.719381, 42.224697], 'pop': 4478, 'state': 'MA'}
{'_id': '01096', 'city': 'WILLIAMSBURG', 'loc': [-72.777989, 42.408522], 'pop': 2295, 'state': 'MA'}
{'_id': '01262', 'city': 'STOCKBRIDGE', 'loc': [-73.322263, 42.30104], 'pop': 2200, 'state': 'MA'}
{'_id': '01240', 'city': 'LENOX', 'loc': [-73.271322, 42.364241], 'pop': 5001, 'state': 'MA'}
{'_id': '01370', 'city': 'SHELBURNE FALLS', 'loc': [-72.739059, 42.602203], 'pop': 4525, 'state': 'MA'}
{'_id': '01340', 'city': 'COLRAIN', 'loc': [-72.726508, 42.67905], 'pop': 2050, 'state': 'MA'}
{'_id': '01462', 'city': 'LUNENBURG', 'loc': [-71.726642, 42.58843], 'pop': 9117, 'state': 'MA'}
{'_id': '01473', 'city': 'WESTMINSTER', 'loc': [-71.909599, 42.548319], 'pop': 6191, 'state': 'MA'}
{'_id': '01510', 'city': 'CLINTON', 'loc': [-71.682847, 42.418147], 'pop': 13269, 'state': 'MA'}
{'_id': '01569', 'city': 'UXBRIDGE', 'loc': [-71.632869, 42.074426], 'pop': 10364, 'state': 'MA'}
{'_id': '01775', 'city': 'STOW', 'loc': [-71.515019, 42.430785], 'pop': 5328, 'state': 'MA'}
```
Output will continue to be sent to the `output_file` until the output_file is assigned
`None` or the empty string ("").

## Options

You can set the following options on the `MongoDB` class objects. 

`MongoDB.line_numbers` : Bool. True to display line numbers in output, False to 
remove them.

`MongoDB.pretty_print` : Bool. True to use `pprint.pprint` to output documents.
False to write them out as the database returned them.

`MongoDB.paginate` : Bool. True to paginate output based on screen height. False to just
send all output directly to console.

`MongoDB.output_file` : Str. Define a file to write results to. All output is
appended to the file. Each line is flushed so content is not lost. Set `output_file`
ton `None` or the emtpy string ("") to stop output going to a file.



