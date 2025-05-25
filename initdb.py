import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["library_db"]

# Create collections if not exist
db.create_collection("users")
db.create_collection("books")
db.create_collection("borrowed")

print("Database initialized with users, books, and borrowed collections.")
