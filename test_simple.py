#!/usr/bin/env python3
"""
Simple test script to verify activity logging functionality
"""

import sys
import os
sys.path.append('.')

def test_activity_logging():
    """Test activity logging functionality"""
    try:
        from utils.crud_operations import log_activity, read_learner_activities, create_learner
        from models.learner import Learner
        
        print("Testing Activity Logging Functionality")
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
            print(f"Test learner created with ID: {test_learner.id}")
            learner_id = test_learner.id
        else:
            print("Failed to create test learner")
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
                print(f"Logged activity: {activity_type}")
            else:
                print(f"Failed to log activity: {activity_type}")
                return False
        
        # Test 3: Retrieve activities
        print("\n3. Retrieving logged activities...")
        activities = read_learner_activities(learner_id)
        
        if activities and len(activities) == 3:
            print(f"Retrieved {len(activities)} activities successfully")
            
            # Display activities
            for i, activity in enumerate(activities, 1):
                print(f"   {i}. {activity.get('activity_type')} - Score: {activity.get('score')}, Duration: {activity.get('duration')}min")
            
            return True
        else:
            print(f"Expected 3 activities, got {len(activities) if activities else 0}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
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
        
        print("All required functions imported successfully")
        
        # Test that the functions are callable
        if callable(log_activity) and callable(read_learner_activities):
            print("Functions are callable")
            return True
        else:
            print("Functions are not callable")
            return False
            
    except Exception as e:
        print(f"Streamlit integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Activity Logging Fix")
    print("=" * 50)
    
    test1_result = test_activity_logging()
    test2_result = test_streamlit_integration()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Activity Logging: {'PASSED' if test1_result else 'FAILED'}")
    print(f"   Streamlit Integration: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("\nAll tests passed! The activity logging fix is working correctly.")
        print("\nSummary of fixes applied:")
        print("   1. Added 'Log Activity' page to Streamlit frontend")
        print("   2. Added 'View Activities' page to Streamlit frontend") 
        print("   3. Fixed 'View Learners' to show real activities from database")
        print("   4. Added read_learner_activities() function to CRUD operations")
        print("   5. Connected Streamlit frontend to activity logging system")
        print("\nYou can now:")
        print("   - Log activities using the 'Log Activity' page")
        print("   - View activities using the 'View Activities' page")
        print("   - See real activities in the 'View Learners' page")
    else:
        print("\nSome tests failed. Please check the error messages above.")
    
    sys.exit(0 if (test1_result and test2_result) else 1)