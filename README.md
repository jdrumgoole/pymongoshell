# mongodbshell : A class that makes it easy to use MongoDB in the python shell

the Python shell is the ideal environment for Python developers to interact
with MongoDB. However output cursors and interacting with the database requires
a little more boilerplate than is convenient. the `mongodbshell` package 
provides a set a convenience functions and objects to allow easier
interaction with MongoDB via the Python interpreter. 

## Installation

you can install the software with pip3 or pipenv. The `mongodbshell` only
supports Python 3. 

```python
$ pip3 install mongodbshell
Collecting mongodbshell
  Downloading https://files.pythonhosted.org/packages/9f/23/e5478384a52b609353f10a1201742a516c6310fe64ddb62e4362c188f752/mongodbshell-0.1a5.tar.gz
Requirement already satisfied: pymongo in /Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages (from mongodbshell) (3.7.2)
Collecting dnspython (from mongodbshell)
  Downloading https://files.pythonhosted.org/packages/ec/d3/3aa0e7213ef72b8585747aa0e271a9523e713813b9a20177ebe1e939deb0/dnspython-1.16.0-py2.py3-none-any.whl (188kB)
    100% |████████████████████████████████| 194kB 7.3MB/s
Building wheels for collected packages: mongodbshell
  Running setup.py bdist_wheel for mongodbshell ... done
  Stored in directory: /Users/jdrumgoole/Library/Caches/pip/wheels/54/5c/0d/2a430d7b25fb55ddee658aefab9593940d2d0047a6b1fcfc6d
Successfully built mongodbshell
Installing collected packages: dnspython, mongodbshell
Successfully installed dnspython-1.16.0 mongodbshell-0.1a5
```

## Using the mongodbshell

The easiest way to get started with `mongodbshell` is to import the prebuilt
`mongo_client` object. The `mongo_client` object expects to connect to a `mongod` running 
locally on port 27017 (it uses the [MongoDB URI](https://docs.mongodb.com/manual/reference/connection-string/) 
`mongodb://localhost:27017` by default)

```python
$ python3
Python 3.6.5 (v3.6.5:f59c0932b4, Mar 28 2018, 03:03:55)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from mongodbshell import mongo_client
>>> mongo_client
Client('test', 'test', 'mongodb://localhost:27017')
>>> monggo_client.list_database_names()
1    config
2    test
3    local
4    admin
>>>
```
Each proxy object has host of standard properties:
```python
>>> mongo_client.client
MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True)
>>> mongo_client.database
Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'test')
>>> mongo_client.collection
Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'test'), 'test')
>>> mongo_client.uri
'mongodb://localhost:27017'
>>>
```

There are also convenience functions for the most popular operations:

```python
>>> mongo_client.is_master()
{'ismaster': True,
 'localTime': datetime.datetime(2019, 1, 16, 15, 15, 41, 87000),
 'logicalSessionTimeoutMinutes': 30,
 'maxBsonObjectSize': 16777216,
 'maxMessageSizeBytes': 48000000,
 'maxWireVersion': 7,
 'maxWriteBatchSize': 100000,
 'minWireVersion': 0,
 'ok': 1.0,
 'readOnly': False}
>>> mongo_client.insert_one({"name" : "Joe Drumgoole", "twitter_handle" : "@jdrumgoole"})
ObjectId('5c3f4f2fc3b498d6674b08f0')
>>> mongo_client.find_one( {"name" : "Joe Drumgoole"})
1    {'_id': ObjectId('5c3f4b04c3b498d4a1c6ce22'),
2     'name': 'Joe Drumgoole',
3     'twitter_handle': '@jdrumgoole'}
```

## Line Numbers on Output

Line numbers are added to output by default. You can turn off line numbers by
setting the `line_numbers` flag to false.

```python
>>> mongo_client.insert_one({"name" : "Joe Drumgoole", "twitter_handle" : "@jdrumgoole"})
ObjectId('5c3f4f2fc3b498d6674b08f0')
>>> mongo_client.find_one( {"name" : "Joe Drumgoole"})
1    {'_id': ObjectId('5c3f4b04c3b498d4a1c6ce22'),
2     'name': 'Joe Drumgoole',
3     'twitter_handle': '@jdrumgoole'}
>>> mongo_client.line_numbers = False                      # Turn off line numbers
>>> mongo_client.find_one( {"name" : "Joe Drumgoole"})
{'_id': ObjectId('5c3f4b04c3b498d4a1c6ce22'),
 'name': 'Joe Drumgoole',
 'twitter_handle': '@jdrumgoole'}
>>>
```
## Connecting to a specific MongoDB URI

You can connect to a different database by using the `Proxy` class. Here is an
example connection to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) hosted datbase. 

```python
>>> from mongodbshell import Proxy
>>> atlas=Proxy(uri="mongodb+srv://readonly:readonly@demodata-rgl39.mongodb.net/test?retryWrites=true", database="demo", collection="zipcodes")
>>> atlas.find_one()
1    {'_id': '01069',
2     'city': 'PALMER',
3     'loc': [-72.328785, 42.176233],
4     'pop': 9778,
5     'state': 'MA'}

```

## Looking at large volumes of output

If you run a query in the python shell it will return a cursor and to look at
the objects in the cursor you need to either write a loop to consume the cursor
or explicitly call `next()` on each cursor item.

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
`Proxy` class and the built in `mongo_client` object automatically handle 
pretty printing and paginating outing. 

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

The `Proxy` class can send output to a file by setting the `output_file` property
on the `Proxy` class. 

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

You can set the following options on the `mongo_client` or `Client` class objects. 

`Client.line_numbers` : Bool. True to display line numbers in output, False to 
remove them.

`Client.pretty_print` : Bool. True to use `pprint.pprint` to output documents.
False to write them out as the database returned them.

`Client.paginate` : Bool. True to paginate output based on screen height. False to just
send all output directly to console.

`Client.output_file` : Str. Define a file to write results to. All output is
appended to the file. Each line is flushed so content is not lost. Set `output_file`
ton `None` or the emtpy string ("") to stop output going to a file.



