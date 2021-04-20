import pymongo
import gridfs

c = pymongo.MongoClient(host="mongodb://jdrumgoole:6KilQUN1sgUSR8cQm55kke8mmY7ZA9ILJ8Nx0dDPTw3iY0ffAvRBR2UHTiw10JFSeWxWmGMkFMBN3u7TuW3i0g==@jdrumgoole.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@jdrumgoole@")

db = c["test"]
collection = db["test"]

path = "bigfile.bz2"
copy = "bigfile2.bz2"
fs = gridfs.GridFS(db)
with open(path, 'rb') as file1:
    grid = fs.put(file1)
    eye = fs.get(grid)
    with open(copy, "wb") as file2:
        for block in eye:
            file2.write(block)
