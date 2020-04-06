import pymongo
oc=pymongo.MongoClient()
db=oc["dbtest"]
col=db["coltest"]

import mongodbshell
c=mongodbshell.MongoClient()
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
c.create_index("social")
c.delete_index("social")
