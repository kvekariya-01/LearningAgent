#!/usr/bin/env python3
"""
Test script to verify the API errors fixes are working correctly
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_progress_log_fix():
    """Test that ProgressLog can be created with LearningVelocity objects"""
    print("Testing ProgressLog fix...")
    
    try:
        from models.progress import ProgressLog, LearningVelocity
        
        # Test creating LearningVelocity object
        learning_velocity = LearningVelocity(
            current_velocity=1.5,
            velocity_trend="stable"
        )
        print(f"OK LearningVelocity created: {learning_velocity.current_velocity}")
        
        # Test creating ProgressLog with LearningVelocity object
        progress_log = ProgressLog(
            learner_id="test-learner-123",
            milestone="module_completed",
            engagement_score=85.0,
            learning_velocity=learning_velocity
        )
        print(f"OK ProgressLog created successfully: {progress_log.id}")
        
        # Test with float value (should fail with proper error)
        try:
            bad_progress_log = ProgressLog(
                learner_id="test-learner-456",
                milestone="quiz_completed",
                engagement_score=90.0,
                learning_velocity=1.5  # This should fail
            )
            print("FAIL ProgressLog with float learning_velocity should have failed!")
            return False
        except Exception as e:
            print(f"OK ProgressLog correctly rejects float learning_velocity: {str(e)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"FAIL ProgressLog test failed: {e}")
        return False

def test_network_blocker():
    """Test that network blocker is working"""
    print("\nTesting network blocker...")
    
    try:
        import network_blocker
        
        # Test that network blocker can be activated
        network_blocker.activate_network_blocker()
        print("OK Network blocker activated successfully")
        
        # Test that external requests are blocked
        try:
            import requests
            response = requests.get("https://httpbin.org/get")
            print("FAIL Network blocker not working - request succeeded!")
            return False
        except ConnectionError as e:
            print(f"OK Network blocker working correctly: {str(e)}")
        
        # Test that urllib is blocked
        try:
            import urllib.request
            urllib.request.urlopen("https://httpbin.org/")
            print("FAIL urllib not blocked!")
            return False
        except ConnectionError as e:
            print(f"OK urllib blocked correctly: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"FAIL Network blocker test failed: {e}")
        return False

def test_routes_fix():
    """Test that the routes file can be imported without errors"""
    print("\nTesting routes file fix...")
    
    try:
        # Test importing the routes module
        from routes import learner_routes
        print("OK learner_routes module imported successfully")
        
        # Test that ProgressLog and LearningVelocity can be imported together
        from models.progress import ProgressLog, LearningVelocity
        print("OK ProgressLog and LearningVelocity imports successful")
        
        return True
        
    except Exception as e:
        print(f"FAIL Routes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("API ERRORS FIX VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Test ProgressLog fix
    results.append(test_progress_log_fix())
    
    # Test network blocker
    results.append(test_network_blocker())
    
    # Test routes fix
    results.append(test_routes_fix())
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"OK ALL TESTS PASSED ({passed}/{total})")
        print("\nAPI errors have been successfully fixed!")
        print("\nNext steps:")
        print("1. Run the Streamlit app to test progress registration")
        print("2. Verify no more Minimax API errors appear in logs")
        print("3. Test local recommendations functionality")
        return 0
    else:
        print(f"FAIL SOME TESTS FAILED ({passed}/{total})")
        print("\nPlease check the error messages above and fix any issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)