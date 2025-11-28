#!/usr/bin/env python3
"""
MongoDB Atlas Database Debug Script
Checks connection, data persistence, and fixes issues
"""

import sys
import os
import traceback
from datetime import datetime

def debug_mongodb_connection():
    """Debug MongoDB Atlas connection and data persistence"""
    print("=" * 60)
    print("[SEARCH] MongoDB Atlas Database Debug")
    print("=" * 60)
    
    try:
        # Import database config
        from config.db_config import db, MONGO_URI, DB_NAME
        
        print(f"[OK] MongoDB URI: {MONGO_URI}")
        print(f"[OK] Database Name: {DB_NAME}")
        
        # Test basic connection
        try:
            collections = db.list_collection_names()
            print(f"[OK] Collections found: {collections}")
        except Exception as e:
            print(f"[FAIL] Error listing collections: {e}")
            return False
        
        # Check learners collection
        print("\n[STATS] COLLECTION ANALYSIS:")
        for collection_name in ['learners', 'contents', 'engagements', 'progress_logs', 'interventions']:
            try:
                count = db[collection_name].count_documents({})
                print(f"  {collection_name}: {count} documents")
            except Exception as e:
                print(f"  {collection_name}: Error - {e}")
        
        # Test write operation
        print("\n🧪 TESTING WRITE OPERATIONS:")
        test_doc = {
            "test_collection": True,
            "timestamp": datetime.now().isoformat(),
            "debug_message": "Database connection test"
        }
        
        try:
            result = db.test_debug.insert_one(test_doc)
            print(f"[OK] Test write successful - ID: {result.inserted_id}")
            
            # Verify we can read it back
            retrieved = db.test_debug.find_one({"test_collection": True})
            if retrieved:
                print("[OK] Test read successful")
            else:
                print("[FAIL] Test read failed")
                
            # Clean up
            db.test_debug.delete_one({"test_collection": True})
            print("[OK] Test cleanup completed")
            
        except Exception as e:
            print(f"[FAIL] Test write failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        traceback.print_exc()
        return False

def debug_learner_creation():
    """Debug learner creation process"""
    print("\n" + "=" * 60)
    print("[USER] LEARNER CREATION DEBUG")
    print("=" * 60)
    
    try:
        from models.learner import Learner
        
        # Create test learner
        test_learner = Learner(
            name="Debug Learner",
            age=25,
            gender="male",
            learning_style="visual",
            preferences=["videos", "quizzes"]
        )
        
        print(f"[OK] Learner object created: {test_learner.id}")
        
        # Convert to dict and check structure
        learner_dict = test_learner.to_dict()
        print(f"[OK] Dict conversion successful")
        print(f"Keys in dict: {list(learner_dict.keys())}")
        
        # Test MongoDB insertion
        from config.db_config import db
        try:
            result = db.learners.insert_one(learner_dict)
            print(f"[OK] MongoDB insert successful - ID: {result.inserted_id}")
            
            # Verify insertion
            saved_learner = db.learners.find_one({"_id": result.inserted_id}, {"_id": 0})
            if saved_learner:
                print("[OK] Verification successful")
                print(f"Saved learner name: {saved_learner.get('name')}")
                
                # Clean up
                db.learners.delete_one({"_id": result.inserted_id})
                print("[OK] Cleanup successful")
                return True
            else:
                print("[FAIL] Verification failed - learner not found after insertion")
                return False
                
        except Exception as e:
            print(f"[FAIL] MongoDB insert failed: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"[FAIL] Learner creation failed: {e}")
        traceback.print_exc()
        return False

def debug_crud_operations():
    """Debug CRUD operations"""
    print("\n" + "=" * 60)
    print("[TOOLS] CRUD OPERATIONS DEBUG")
    print("=" * 60)
    
    try:
        from utils.crud_operations import create_learner, read_learners, read_learner
        from models.learner import Learner
        
        # Test create learner
        test_learner = Learner(
            name="CRUD Test Learner",
            age=30,
            gender="female",
            learning_style="auditory",
            preferences=["podcasts", "discussions"]
        )
        
        print("Testing create_learner...")
        result = create_learner(test_learner)
        if result:
            print(f"[OK] create_learner successful - ID: {test_learner.id}")
            
            print("Testing read_learners...")
            all_learners = read_learners()
            print(f"[OK] read_learners successful - Count: {len(all_learners)}")
            
            print("Testing read_learner...")
            single_learner = read_learner(test_learner.id)
            if single_learner:
                print(f"[OK] read_learner successful - Name: {single_learner.get('name')}")
                return True
            else:
                print("[FAIL] read_learner failed")
                return False
        else:
            print("[FAIL] create_learner failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] CRUD operations failed: {e}")
        traceback.print_exc()
        return False

def run_complete_debug():
    """Run complete database debugging"""
    print("[START] Starting Complete MongoDB Atlas Debug...\n")
    
    results = {
        "connection": debug_mongodb_connection(),
        "learner_creation": debug_learner_creation(),
        "crud_operations": debug_crud_operations()
    }
    
    print("\n" + "=" * 60)
    print("[LIST] DEBUG SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] All database tests passed! MongoDB Atlas is working correctly.")
    else:
        print("\n[WARNING]  Some database tests failed. Check errors above.")
        
    return all_passed

if __name__ == "__main__":
    success = run_complete_debug()
    sys.exit(0 if success else 1)