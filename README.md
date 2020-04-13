# mongodbshell :  MongoDB in the python shell

The Python shell is the ideal environment for Python developers to interact
with MongoDB. However output cursors and interacting with the database requires
a little more boilerplate than is convenient. the `mongodbshell` package 
provides a set a convenience functions and objects to allow easier
interaction with MongoDB via the Python interpreter. 

The key value adds for the `mongodbshell` over the standard `pymongo`
package are:

 * Proper pagination of output
 * Pretty printing of output
 * Ability to stream output to a file in parallel to the screen
 * Full compatibility with pymongo API
 
The shell is actually a shim class that wraps the 
[`pymongo.Collection`](https://api.mongodb.com/python/current/api/pymongo/collection.html) class. The
class `mongodbshell` intercepts method and property requests and forwards
them to that class. 

We then process the return values using the properties:
* `pagination`
* `linenumbers`
* `prettyprinting` 

to format the output sensibly for
a human viewer.  

## Installation

you can install the software with `pip3`. The `mongodbshell` only
supports Python 3. 

```shell script
$ pip3 install mongodbshell
```

## Using the mongodbshell

First we create a `MongoClient` object. This is a proxy for all the 
commands we can run using `MongoDBShell`. It is exactly analogous to 
the PyMongo `MongoClient` and is in fact just a shim. We support one
additional argument `banner`. This argument controls whether we output a banner
detailing which version and which collections 

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

Each `mongodbshell.MongoClient` object has a set of standard properties that 
represent the `pymongo` objects. In normal use you will not reference these
objects:

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

There are also convenience functions for some more common operations:

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

# Changing Format of Output

The `mongodbshell` supports three formatting directives. All are boolean values
and all are true by default.
```python
>>> c.paginate
True
>>> c.pretty_print
True
>>> c.line_numbers
True
>>>
```

## Paginate
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

## pretty_print
Pretty printing is used to ensure that the JSON documents output are properly
formatted and easy to read. For small documents turning pretty printing off will
result in the documents printing on a single line which can sometimes be easier
to read.

To turn off `pretty_print` just set the value to `False`.
```python
>>> c.pretty_print=False
>>>
```
## line_numbers
Line numbers are added by default to allow a user to keep track of location
in a large stream output. Similarily to the other properties `line_numbers`
can be toggled on and off by settting the flag.
```python
>>> c.line_numbers=False
>>>
```

# Find Examples

Let's create an example dataset.

```python
>>> import mongodbshell
>>> c=mongodbshell.MongoClient()
mongodbshell 1.1.0b5
Using collection 'test.test'
Server requests set to timeout after 5.0 seconds
>>>
>>> d1 = {"name" : "Heracles"}
>>> d2 = {"name" : "Orpheus"}
>>> d3 = {"name" : "Jason"}
>>> d4 = {"name" : "Odysseus"}
>>> d5 = {"name" : "Achilles"}
>>> d6 = {"name" : "Menelaeus"}
>>> c.insert_one(d1)
Inserted: 5e9479265b17a0612c508328
>>> c.insert_many([d2,d3,d4,d5])
1  : [ObjectId('5e9479275b17a0612c508329'),
2  :  ObjectId('5e9479275b17a0612c50832a'),
3  :  ObjectId('5e9479275b17a0612c50832b'),
4  :  ObjectId('5e9479275b17a0612c50832c')]
>>>
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
1  : [ObjectId('5e9478e75b17a0612c508325'),
2  :  ObjectId('5e9478e75b17a0612c508326'),
3  :  ObjectId('5e9478e75b17a0612c508327')]
>>>
```
### Find all documents
```python
>>> c.find()
1  : {'_id': ObjectId('5e9478e75b17a0612c508325'),
2  :  'email': 'Joe.Drumgoole@mongodb.com',
3  :  'mobile': '+353 87xxxxxxx',
4  :  'name': 'Joe Drumgoole',
5  :  'social': ['twitter', 'instagram', 'linkedin']}
6  : {'_id': ObjectId('5e9478e75b17a0612c508326'),
7  :  'email': 'Hercules.Mulligan@example.com',
8  :  'mobile': '+1 12345678',
9  :  'name': 'Hercules Mulligan',
10 :  'social': ['twitter', 'linkedin']}
11 : {'_id': ObjectId('5e9478e75b17a0612c508327'),
12 :  'email': 'Aaron.Burr@example.com',
13 :  'mobile': '+1 67891011',
14 :  'name': 'Aaron Burr',
15 :  'social': ['instagram']}
16 : {'_id': ObjectId('5e9479265b17a0612c508328'), 'name': 'Heracles'}
17 : {'_id': ObjectId('5e9479275b17a0612c508329'), 'name': 'Orpheus'}
18 : {'_id': ObjectId('5e9479275b17a0612c50832a'), 'name': 'Jason'}
19 : {'_id': ObjectId('5e9479275b17a0612c50832b'), 'name': 'Odysseus'}
20 : {'_id': ObjectId('5e9479275b17a0612c50832c'), 'name': 'Achilles'}
>>>
```
### Find all documents with an instagram social setting

Note that MongoDB knows to look inside an array when the target
field is an array.

```python


>>> c.find({'social':'instagram'})
1  : {'_id': ObjectId('5e9478e75b17a0612c508325'),
2  :  'email': 'Joe.Drumgoole@mongodb.com',
3  :  'mobile': '+353 87xxxxxxx',
4  :  'name': 'Joe Drumgoole',
5  :  'social': ['twitter', 'instagram', 'linkedin']}
6  : {'_id': ObjectId('5e9478e75b17a0612c508327'),
7  :  'email': 'Aaron.Burr@example.com',
8  :  'mobile': '+1 67891011',
9  :  'name': 'Aaron Burr',
10 :  'social': ['instagram']}
>>>
```

##Connecting to a specific MongoDB URI

You can connect to a different database by passing in a different URI to the `host` 
parameter for `mongodbshell.MongoClient`. Here is an
example connection to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 
hosted database. 

The example below is a live read-only database. You can try it out at the 
MongoDB URI:

```shell script
"mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true"
```

In the `mongodbshell`:

```python
>>> import mongodbshell
>>> atlas=mongodbshell.MongoClient(host="mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true", database="demo", collection="zipcodes")
>>> atlas.find_one()
1    {'_id': '01069',
2     'city': 'PALMER',
3     'loc': [-72.328785, 42.176233],
4     'pop': 9778,
5     'state': 'MA'}

```

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




