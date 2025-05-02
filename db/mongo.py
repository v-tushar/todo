import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

client = None
db = None
todo_collection = None

async def connect_to_mongo():
    global client, db, todo_collection
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        logging.error("❌ MONGO_URI is missing from .env")
        raise ValueError("MONGO_URI is missing from .env")

    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client["todo_db"]
        todo_collection = db["todos"]

        logging.info(f"✅ Connected to MongoDB database: {db.name}")
        logging.info(f"🗂️ Collection reference set: {todo_collection.name}")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise e

def close_mongo_connection():
    if client:
        client.close()
        print("🔌 MongoDB connection closed.")
