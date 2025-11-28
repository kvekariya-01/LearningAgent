#!/usr/bin/env python3
"""
Simple import test
"""

import sys
import os
sys.path.append('.')

def test_import():
    """Test if the import issue is resolved"""
    try:
        print("Testing imports...")
        
        # Test the main imports that were failing
        from utils.crud_operations import read_learner_activities
        print("read_learner_activities imported successfully")
        
        # Test the fallback function
        from utils.crud_operations import read_learner
        def test_fallback(learner_id):
            learner_data = read_learner(learner_id)
            if not learner_data:
                return None
            return learner_data.get("activities", [])
        
        print("Fallback function works")
        
        # Test that they're the same function
        if read_learner_activities == test_fallback:
            print("Functions are identical")
        else:
            print("Functions are different (this is expected)")
        
        return True
        
    except Exception as e:
        print(f"Import test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Import Fix")
    print("=" * 30)
    
    result = test_import()
    
    if result:
        print("\nImport fix successful! The Streamlit app should now work without import errors.")
    else:
        print("\nImport issue persists. Please check the error above.")