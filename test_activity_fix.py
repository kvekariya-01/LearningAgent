#!/usr/bin/env python3
"""
Test script to verify activity logging functionality works properly
"""

import sys
import os
sys.path.append('.')

def test_activity_logging():
    """Test activity logging functionality"""
    try:
        from utils.crud_operations import log_activity, read_learner_activities, create_learner
        from models.learner import Learner
        
        print("🧪 Testing Activity Logging Functionality")
        print("=" * 50)
        
        # Test 1: Create a test learner
        print("\n1. Creating test learner...")
        test_learner = Learner(
            name="Test Learner",
            age=25,
            gender="Other",
            learning_style="Visual",
            preferences=["Testing", "Development"]
        )
        
        result = create_learner(test_learner)
        if result:
            print(f"[OK] Test learner created with ID: {test_learner.id}")
            learner_id = test_learner.id
        else:
            print("[FAIL] Failed to create test learner")
            return False
        
        # Test 2: Log activities
        print("\n2. Logging test activities...")
        
        activities_to_log = [
            ("module_completed", 45.0, 92.0),
            ("quiz_completed", 30.0, 88.0),
            ("assignment_submitted", 60.0, 95.0)
        ]
        
        for activity_type, duration, score in activities_to_log:
            logged_learner = log_activity(learner_id, activity_type, duration, score)
            if logged_learner:
                print(f"[OK] Logged activity: {activity_type}")
            else:
                print(f"[FAIL] Failed to log activity: {activity_type}")
                return False
        
        # Test 3: Retrieve activities
        print("\n3. Retrieving logged activities...")
        activities = read_learner_activities(learner_id)
        
        if activities and len(activities) == 3:
            print(f"[OK] Retrieved {len(activities)} activities successfully")
            
            # Display activities
            for i, activity in enumerate(activities, 1):
                print(f"   {i}. {activity.get('activity_type')} - Score: {activity.get('score')}, Duration: {activity.get('duration')}min")
            
            return True
        else:
            print(f"[FAIL] Expected 3 activities, got {len(activities) if activities else 0}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_integration():
    """Test that Streamlit app can import the necessary functions"""
    try:
        print("\n4. Testing Streamlit integration...")
        
        # Test imports that Streamlit app uses
        from utils.crud_operations import (
            log_activity, read_learner_activities, read_learners, read_learner
        )
        
        print("[OK] All required functions imported successfully")
        
        # Test that the functions are callable
        if callable(log_activity) and callable(read_learner_activities):
            print("[OK] Functions are callable")
            return True
        else:
            print("[FAIL] Functions are not callable")
            return False
            
    except Exception as e:
        print(f"[FAIL] Streamlit integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("[START] Testing Activity Logging Fix")
    print("=" * 50)
    
    test1_result = test_activity_logging()
    test2_result = test_streamlit_integration()
    
    print("\n" + "=" * 50)
    print("[STATS] Test Results:")
    print(f"   Activity Logging: {'[OK] PASSED' if test1_result else '[FAIL] FAILED'}")
    print(f"   Streamlit Integration: {'[OK] PASSED' if test2_result else '[FAIL] FAILED'}")
    
    if test1_result and test2_result:
        print("\n[SUCCESS] All tests passed! The activity logging fix is working correctly.")
        print("\n[LIST] Summary of fixes applied:")
        print("   1. [OK] Added 'Log Activity' page to Streamlit frontend")
        print("   2. [OK] Added 'View Activities' page to Streamlit frontend")
        print("   3. [OK] Fixed 'View Learners' to show real activities from database")
        print("   4. [OK] Added read_learner_activities() function to CRUD operations")
        print("   5. [OK] Connected Streamlit frontend to activity logging system")
        print("\n[START] You can now:")
        print("   - Log activities using the 'Log Activity' page")
        print("   - View activities using the 'View Activities' page")
        print("   - See real activities in the 'View Learners' page")
    else:
        print("\n[FAIL] Some tests failed. Please check the error messages above.")
    
    sys.exit(0 if (test1_result and test2_result) else 1)