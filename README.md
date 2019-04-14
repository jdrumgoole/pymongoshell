# mongodbshell : A module that makes it easy to use MongoDB in the python shell

The Python shell is the ideal environment for Python developers to interact
with MongoDB. However output cursors and interacting with the database requires
a little more boilerplate than is convenient. the `mongodbshell` package 
provides a set a convenience functions and objects to allow easier
interaction with MongoDB via the Python interpreter. 

## Installation

you can install the software with pip3 or pipenv. The `mongodbshell` only
supports Python 3. 

```python
$ pip3 install mongodbshell
```

A complete set of API docs can be found on[read the docs](https://mongodbshell.readthedocs.io/en/latest/)

## Using the mongodbshell

First we create a `MongoDB` object. This is a proxy for all the 
commands we can run using `MongoDBShell`.

```python
>>> client=mongodbshell.MongoDB()
>>> client
mongodbshell.MongoDB('test', 'test', 'mongodb://localhost:27017')
```

As you can see a `MongoDB` object embeds the default database `test` and collection
`test`. We can also access the native `MongoClient` object.


Each `MongoDB` object has host of standard properties:
```python
>>> client
mongodbshell.MongoDB('test', 'test', 'mongodb://localhost:27017')
>>> client.client
MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True)
>>> client.database
Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'test')
>>> client.collection
Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'test'), 'test')
>>> client.uri
'mongodb://localhost:27017'
>>>
```

There are also convenience functions for the most popular operations:

```python
>>> client.is_master()
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
example connection to a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) hosted datbase. 

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
`MongoDB` object will automatically handle pretty printing and paginating outing. 

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



