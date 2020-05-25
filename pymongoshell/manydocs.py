import pymongo
oc=pymongo.MongoClient()
db=oc["dbtest"]
col=db["coltest"]

import pymongoshell
c=pymongoshell.MongoClient()
c.collection="test.test"
c.is_master()
d1 = {"name" : "Heracles"}
d2 = {"name" : "Orpheus"}
d3 = {"name" : "Jason"}
d4 = {"name" : "Odysseus"}
d5 = {"name" : "Achilles"}
d6 = {"name" : "Menelaeus"}
c.insert_one(d1)
c.insert_many([d2,d3,d4,d5])
c.drop_collection(confirm=False)

p1 = {"name" : "Joe Drumgoole",
      "social": ["twitter", "instagram", "linkedin"],
      "mobile": "+353 87xxxxxxx",
      "email" : "Joe.Drumgoole@mongodb.com"}
p2 = {"name" : "Hercules Mulligan",
      "social": ["twitter", "linkedin"],
      "mobile": "+1 12345678",
      "email" : "Hercules.Mulligan@example.com"}
p3 = {"name" : "Aaron Burr",
      "social": ["instagram"],
      "mobile": "+1 67891011",
      "email" : "Aaron.Burr@example.com"}
c.insert_many([p1,p2,p3])
c.count_documents()
c.count_documents({"name":"Joe Drumgoole"})
c.create_index("social")
c.drop_index("social_1")
c.update_one({"name" : "Joe Drumgoole"}, {"$set" : {"age" : 35}})
c.update_one({"name" : "Joe Drumgoole"}, {"$set" : {"age" : 35}})
c.update_many({"social" : "twitter"}, {"$set" : {"followers" : 1000}})
c=pymongoshell.MongoClient(host="mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority")
c.find(1) # force an error
c.bongo #make a collection
c.bongospongo() # call an invalid method

#
c=pymongoshell.MongoClient()
c.ldbs
c.collection = "dummy.data"
c.insert_one({"name":"Joe Drumgoole"})
c.ldbs
c.drop_database()
c.ldbs
