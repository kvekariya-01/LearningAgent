#!/usr/bin/env python3
"""
Simple MongoDB Atlas Database Debug Script
"""

import sys
import traceback
from datetime import datetime

def test_mongodb_connection():
    print("=" * 50)
    print("MONGODB ATLAS CONNECTION TEST")
    print("=" * 50)
    
    try:
        from config.db_config import db, MONGO_URI, DB_NAME
        
        print("MongoDB URI:", MONGO_URI)
        print("Database Name:", DB_NAME)
        
        # Test connection
        collections = db.list_collection_names()
        print("Collections found:", collections)
        
        # Check each collection
        for collection_name in ['learners', 'contents', 'engagements', 'progress_logs', 'interventions']:
            count = db[collection_name].count_documents({})
            print(f"{collection_name}: {count} documents")
        
        # Test write operation
        test_doc = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Database test"
        }
        
        result = db.test_collection.insert_one(test_doc)
        print("Test insert successful - ID:", result.inserted_id)
        
        # Verify read
        retrieved = db.test_collection.find_one({"test": True})
        if retrieved:
            print("Test read successful")
        else:
            print("Test read failed")
            
        # Clean up
        db.test_collection.delete_one({"test": True})
        print("Test cleanup successful")
        
        return True
        
    except Exception as e:
        print("MongoDB connection error:", e)
        traceback.print_exc()
        return False

def test_learner_save():
    print("\n" + "=" * 50)
    print("LEARNER SAVE TEST")
    print("=" * 50)
    
    try:
        from models.learner import Learner
        from config.db_config import db
        
        # Create learner
        learner = Learner(
            name="Test Learner",
            age=25,
            gender="male",
            learning_style="visual",
            preferences=["videos", "quizzes"]
        )
        
        print("Learner created with ID:", learner.id)
        
        # Convert to dict
        learner_dict = learner.to_dict()
        print("Learner dict keys:", list(learner_dict.keys()))
        
        # Save to database
        result = db.learners.insert_one(learner_dict)
        print("MongoDB insert successful - ID:", result.inserted_id)
        
        # Verify save
        saved_learner = db.learners.find_one({"_id": result.inserted_id}, {"_id": 0})
        if saved_learner:
            print("Verification successful")
            print("Saved learner name:", saved_learner.get("name"))
            
            # Clean up
            db.learners.delete_one({"_id": result.inserted_id})
            print("Cleanup successful")
            return True
        else:
            print("Verification failed")
            return False
            
    except Exception as e:
        print("Learner save error:", e)
        traceback.print_exc()
        return False

def test_crud_operations():
    print("\n" + "=" * 50)
    print("CRUD OPERATIONS TEST")
    print("=" * 50)
    
    try:
        from utils.crud_operations import create_learner, read_learners
        from models.learner import Learner
        
        # Create test learner
        learner = Learner(
            name="CRUD Test",
            age=30,
            gender="female",
            learning_style="auditory",
            preferences=["podcasts"]
        )
        
        # Test create
        result = create_learner(learner)
        if result:
            print("create_learner successful")
            
            # Test read all
            all_learners = read_learners()
            print("read_learners successful, count:", len(all_learners))
            
            # Test read one
            learner_data = None
            for l in all_learners:
                if l.get("id") == learner.id:
                    learner_data = l
                    break
                    
            if learner_data:
                print("read_learner successful, name:", learner_data.get("name"))
                return True
            else:
                print("read_learner failed - learner not found")
                return False
        else:
            print("create_learner failed")
            return False
            
    except Exception as e:
        print("CRUD operations error:", e)
        traceback.print_exc()
        return False

def main():
    print("Starting MongoDB Atlas Database Tests...\n")
    
    results = []
    
    # Test 1: Basic connection
    results.append(("Connection", test_mongodb_connection()))
    
    # Test 2: Learner save
    results.append(("Learner Save", test_learner_save()))
    
    # Test 3: CRUD operations
    results.append(("CRUD Operations", test_crud_operations()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\nAll tests passed! MongoDB Atlas is working.")
    else:
        print("\nSome tests failed. Check errors above.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)