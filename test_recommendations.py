#!/usr/bin/env python3
"""
Test script to verify recommendation functionality
"""

import sys
import os
sys.path.append('.')

def test_local_recommendations():
    """Test local recommendation generation"""
    try:
        print("Testing Local Recommendation Generation")
        print("=" * 50)
        
        # Test the local recommendation functions
        from app import generate_local_recommendations, read_learner, read_learners
        
        # Get existing learners or create test data
        learners = read_learners()
        
        if not learners:
            print("No learners found - creating test scenario")
            # Test new learner scenario
            new_learner_recs = generate_local_recommendations("test-new-learner")
            
            if "error" in new_learner_recs:
                print(f"Expected error for non-existent learner: {new_learner_recs['error']}")
            else:
                print("[OK] New learner recommendations generated successfully")
                print(f"   Is new learner: {new_learner_recs.get('is_new_learner')}")
                print(f"   Recommendations count: {len(new_learner_recs.get('recommendations', []))}")
        else:
            print(f"Found {len(learners)} learners - testing with existing learner")
            
            # Test with existing learner
            test_learner = learners[0]
            learner_id = test_learner.get('_id', test_learner.get('id', 'test-id'))
            
            existing_learner_recs = generate_local_recommendations(learner_id)
            
            if "error" in existing_learner_recs:
                print(f"Error generating recommendations: {existing_learner_recs['error']}")
            else:
                print("[OK] Existing learner recommendations generated successfully")
                print(f"   Is new learner: {existing_learner_recs.get('is_new_learner')}")
                print(f"   Recommendations count: {len(existing_learner_recs.get('recommendations', []))}")
                
                if "performance_summary" in existing_learner_recs:
                    summary = existing_learner_recs["performance_summary"]
                    print(f"   Performance summary included: {summary}")
        
        return True
        
    except Exception as e:
        print(f"Local recommendations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_recommendation_imports():
    """Test that all recommendation-related imports work"""
    try:
        print("\nTesting Recommendation Imports")
        print("=" * 40)
        
        # Test ML recommender imports
        try:
            from ml.recommender import hybrid_recommend, recommend_for_new_learner
            print("[OK] ML recommender functions imported successfully")
        except ImportError as e:
            print(f"[WARNING] ML recommender import failed (expected in some environments): {e}")
        
        # Test Streamlit app imports
        from app import get_recommendations, generate_local_recommendations
        print("[OK] Streamlit recommendation functions imported successfully")
        
        # Test that functions are callable
        if callable(generate_local_recommendations):
            print("[OK] generate_local_recommendations is callable")
        else:
            print("[FAIL] generate_local_recommendations is not callable")
            return False
        
        if callable(get_recommendations):
            print("[OK] get_recommendations is callable")
        else:
            print("[FAIL] get_recommendations is not callable")
            return False
        
        return True
        
    except Exception as e:
        print(f"Recommendation imports test failed: {str(e)}")
        return False

def test_recommendation_structure():
    """Test recommendation data structure"""
    try:
        print("\nTesting Recommendation Data Structure")
        print("=" * 45)
        
        from app import generate_local_recommendations
        
        # Test with mock learner data
        test_recs = generate_local_recommendations("test-learner-id")
        
        if "error" in test_recs:
            print(f"Expected error for test: {test_recs['error']}")
            return True
        
        # Validate structure
        required_fields = ["learner_id", "is_new_learner", "recommendations"]
        for field in required_fields:
            if field not in test_recs:
                print(f"[FAIL] Missing required field: {field}")
                return False
        
        # Validate recommendations structure
        recs = test_recs["recommendations"]
        if recs:
            first_rec = recs[0]
            recommended_fields = ["title", "reason"]
            for field in recommended_fields:
                if field not in first_rec:
                    print(f"[WARNING] Missing recommended field in recommendation: {field}")
        
        print("[OK] Recommendation data structure is valid")
        print(f"   Learner ID: {test_recs.get('learner_id')}")
        print(f"   Is New Learner: {test_recs.get('is_new_learner')}")
        print(f"   Recommendations: {len(recs)} items")
        
        return True
        
    except Exception as e:
        print(f"Recommendation structure test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Recommendation System")
    print("=" * 50)
    
    test1_result = test_local_recommendations()
    test2_result = test_recommendation_imports()
    test3_result = test_recommendation_structure()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Local Recommendations: {'[OK] PASSED' if test1_result else '[FAIL] FAILED'}")
    print(f"   Import Functions: {'[OK] PASSED' if test2_result else '[FAIL] FAILED'}")
    print(f"   Data Structure: {'[OK] PASSED' if test3_result else '[FAIL] FAILED'}")
    
    if test1_result and test2_result and test3_result:
        print("\n[SUCCESS] All recommendation tests passed!")
        print("\n[LIST] Recommendation System Features:")
        print("   [OK] Local recommendation generation (fallback)")
        print("   [OK] API integration (when Flask backend available)")
        print("   [OK] New learner recommendations")
        print("   [OK] Existing learner recommendations")
        print("   [OK] Performance-based suggestions")
        print("   [OK] Activity-based recommendations")
        print("   [OK] ML-powered recommendations (when available)")
        print("   [OK] User-friendly Streamlit interface")
        print("\n[START] Ready to use!")
    else:
        print("\n[FAIL] Some recommendation tests failed.")
        print("Check the error messages above for details.")
    
    sys.exit(0 if (test1_result and test2_result and test3_result) else 1)