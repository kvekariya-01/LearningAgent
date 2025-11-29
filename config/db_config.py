"""
Database configuration for Learning Agent
Handles MongoDB Atlas connection
"""

import os
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not available, try to load .env manually
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    except Exception as e:
        print("Error loading .env manually:", e)
        pass  # Continue without .env file


# --------------------------
# [TOOLS] Environment Variables
# --------------------------

# MongoDB Atlas connection string
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://learning_agent_db:learningagent%40123@learningagentdb.a53g2hi.mongodb.net/?appName=learningagentdb")

# Database name
DB_NAME = os.environ.get("MONGO_DB", "learning_agent_db")

# Enable MongoDB Atlas usage
# Set MONGO_ENABLED="false" only to disable (for testing)
MONGO_ENABLED = os.environ.get("MONGO_ENABLED", "true").lower() == "true"

# Check for environment override to disable external AI services
USE_IN_MEMORY_DB = os.environ.get("USE_IN_MEMORY_DB", "false").lower() == "true"
ENABLE_ERROR_RECOVERY = os.environ.get("ENABLE_ERROR_RECOVERY", "false").lower() == "true"

# Global variable for database object
db = None


def initialize_database():
    """
    Initialize MongoDB Atlas connection.
    Returns True if MongoDB Atlas is connected, False if failed.
    """
    global db

    # If in-memory database is enabled, skip external connections
    if USE_IN_MEMORY_DB:
        # Silent initialization for in-memory database
        db = None  # Will use in-memory fallback in CRUD operations
        return False  # Return False to indicate in-memory mode

    # If explicitly disabled MongoDB usage
    if not MONGO_ENABLED:
        print("X MongoDB Atlas disabled via environment variable")
        db = None
        return False

    # If no Mongo URI provided
    if not MONGO_URI:
        if ENABLE_ERROR_RECOVERY:
            # Silent fallback to in-memory database
            db = None  # Will use in-memory fallback
            return False
        else:
            print("X No MONGO_URI found in environment variables")
            return False

    # Try connecting to MongoDB Atlas
    try:
        print(f"Attempting MongoDB Atlas connection...")
        
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )

        # Test connection
        client.admin.command("ping")
        db = client[DB_NAME]

        print(f"[OK] MongoDB Atlas Connected Successfully -> Database: {DB_NAME}")
        return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"X MongoDB Atlas connection failed: {e}")
        
        # Enable error recovery if configured
        if ENABLE_ERROR_RECOVERY:
            print("[OK] Enabling error recovery - using in-memory fallback")
            db = None  # Will use in-memory fallback
            return False
        else:
            db = None
            return False


# Initialize database when this file is imported
initialize_database()
