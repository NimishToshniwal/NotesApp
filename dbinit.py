from pymongo import MongoClient 
from pymongo.errors import ConnectionFailure, ConfigurationError 
from dotenv import load_dotenv 
import os 
import csv 
load_dotenv() # MongoDB connection function 
def get_db_connection(): 
    try: 
        mongo_uri = os.getenv("MONGO_URI") 
        if not mongo_uri: 
            raise ValueError("Missing required environment variable: MONGO_URI") 
        client = MongoClient(mongo_uri) 
        # Test the connection 
        try: 
            client.admin.command("ping") 
            # print("Connected to MongoDB successfully") 
        except ConnectionFailure as cf: 
            raise ConnectionFailure(f"Failed to ping MongoDB server: {cf}") 
        # Retrieve the database specified in the MONGO_URI 
        try: 
            database = os.getenv("DATABASE_NAME") 
            db = client[database] 
        except ConfigurationError: 
            raise ValueError("Database name is missing in the MONGO_URI .") 
        collection_name = os.getenv("COLLECTION_NAME") 
        collection = db[collection_name] 
        # print(f"Accessing collection: {collection}") 
        return collection 
    except ValueError as e: 
        print(f"Configuration error: {e}") 
        raise 
    except ConnectionFailure as cf: 
        print(f"MongoDB connection failure: {cf}") 
        raise 
    except Exception as e: 
        print(f"Unexpected error occurred in db_init: {e}") 
        raise 

def clear_collection(): 
    collection = get_db_connection() 
    collection.delete_many({}) 