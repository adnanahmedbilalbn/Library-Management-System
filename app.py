from flask import Flask
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from routes import setup_routes  # import the setup function

app = Flask(__name__)
app.secret_key = "your-secret-key"  # needed for session handling
app.config["MONGO_URI"] = "mongodb://localhost:27017/library_db"

mongo = PyMongo(app)

setup_routes(app)  # ✅ THIS is what's missing

if __name__ == "__main__":
    app.run(debug=True)
