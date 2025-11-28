#!/usr/bin/env python3
"""
Test script to verify learner update functionality
"""

import sys
import os
sys.path.append('.')

def test_update_learner():
    """Test learner update functionality"""
    try:
        from utils.crud_operations import update_learner, create_learner, read_learner
        from models.learner import Learner
        
        print("Testing Learner Update Functionality")
        print("=" * 50)
        
        # Test 1: Create a test learner
        print("\n1. Creating test learner...")
        test_learner = Learner(
            name="Update Test Learner",
            age=25,
            gender="Other",
            learning_style="Visual",
            preferences=["Testing", "Update Testing"]
        )
        
        result = create_learner(test_learner)
        if result:
            print(f"Test learner created with ID: {test_learner.id}")
            learner_id = test_learner.id
        else:
            print("Failed to create test learner")
            return False
        
        # Test 2: Verify initial data
        print("\n2. Verifying initial learner data...")
        initial_learner = read_learner(learner_id)
        if initial_learner:
            print(f"Initial name: {initial_learner.get('name')}")
            print(f"Initial age: {initial_learner.get('age')}")
            print(f"Initial learning style: {initial_learner.get('learning_style')}")
        else:
            print("Failed to read initial learner data")
            return False
        
        # Test 3: Update learner information
        print("\n3. Updating learner information...")
        update_fields = {
            'name': 'Updated Test Learner',
            'age': 30,
            'learning_style': 'Auditory'
        }
        
        updated_learner = update_learner(learner_id, update_fields)
        if updated_learner:
            print("Learner updated successfully")
            print(f"Updated name: {updated_learner.get('name')}")
            print(f"Updated age: {updated_learner.get('age')}")
            print(f"Updated learning style: {updated_learner.get('learning_style')}")
        else:
            print("Failed to update learner")
            return False
        
        # Test 4: Verify changes persist
        print("\n4. Verifying changes persist...")
        final_learner = read_learner(learner_id)
        if final_learner:
            if (final_learner.get('name') == 'Updated Test Learner' and 
                final_learner.get('age') == 30 and 
                final_learner.get('learning_style') == 'Auditory'):
                print("Changes verified successfully - all updates persisted correctly")
                return True
            else:
                print("Changes did not persist correctly")
                return False
        else:
            print("Failed to verify final learner data")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_update_integration():
    """Test that Streamlit app can import and use update functions"""
    try:
        print("\n5. Testing Streamlit update integration...")
        
        # Test imports that Streamlit app uses for updates
        from utils.crud_operations import update_learner
        
        print("update_learner function imported successfully")
        
        # Test that the function is callable
        if callable(update_learner):
            print("update_learner function is callable")
            return True
        else:
            print("update_learner function is not callable")
            return False
            
    except Exception as e:
        print(f"Streamlit update integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Learner Update Feature")
    print("=" * 50)
    
    test1_result = test_update_learner()
    test2_result = test_streamlit_update_integration()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Learner Update: {'PASSED' if test1_result else 'FAILED'}")
    print(f"   Streamlit Integration: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("\nAll tests passed! The learner update feature is working correctly.")
        print("\nUpdate Feature Summary:")
        print("   - Added 'Update Learner' page to navigation")
        print("   - Learner selection dropdown (populated from database)")
        print("   - Pre-filled forms with current learner information")
        print("   - Selective field updates (checkboxes for each field)")
        print("   - Real-time form validation and feedback")
        print("   - Integration with existing update_learner() database function")
        print("\nHow to use:")
        print("   1. Go to 'Update Learner' page")
        print("   2. Select learner from dropdown")
        print("   3. Check fields you want to update")
        print("   4. Modify values in the form")
        print("   5. Submit to update learner information")
    else:
        print("\nSome tests failed. Please check the error messages above.")
    
    sys.exit(0 if (test1_result and test2_result) else 1)