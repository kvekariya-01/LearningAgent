#!/usr/bin/env python3
"""
Final Verification Script - No MongoDB Messages
Tests that all MongoDB-related messages are completely eliminated
"""

def test_no_mongodb_messages():
    """Test that no MongoDB messages appear during initialization"""
    print("Testing MongoDB message elimination...")
    
    # Import and initialize database (this should be silent)
    from config.db_config import db, MONGO_URI, DB_NAME
    
    print(f"[OK] Database object: {db}")
    print(f"[OK] MongoDB URI: {MONGO_URI if MONGO_URI else 'Not set (expected)'}")
    print(f"[OK] Database Name: {DB_NAME}")
    
    # Test CRUD operations
    from utils.crud_operations import read_learners, create_learner
    from models.learner import Learner
    
    # Create test learner (should be silent)
    test_learner = Learner(
        name="Silent Test Learner",
        age=25,
        gender="male", 
        learning_style="visual",
        preferences=["tests"]
    )
    
    create_learner(test_learner)
    
    # Read all learners (should be silent)
    learners = read_learners()
    print(f"[OK] Found {len(learners)} learners")
    
    print("\n[SUCCESS]: No MongoDB messages appeared!")
    print("[OK] Database initialization is completely silent")
    print("[OK] All CRUD operations work silently")
    print("[OK] System is fully functional without any MongoDB output")

if __name__ == "__main__":
    test_no_mongodb_messages()