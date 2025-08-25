from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fruit_store")

# Global client instance
client = AsyncIOMotorClient(MONGODB_URL)

def get_database():
    """Get database instance"""
    return client[DATABASE_NAME]

def get_collections():
    """Get all collections"""
    database = get_database()
    return {
        'customers': database.customers,
        'fruits': database.fruits,
        'suppliers': database.suppliers,
        'orders': database.orders
    }

async def close_database_connection():
    """Close database connection"""
    client.close()