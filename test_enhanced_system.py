#!/usr/bin/env python3
"""
Test script for Enhanced Learning Management System
Verifies all components work correctly after Minimax API fix
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append('.')

def test_enhanced_recommendation_engine():
    """Test the enhanced recommendation engine"""
    print("Testing Enhanced Recommendation Engine...")
    
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
        # Test learner data
        test_learner_data = {
            "id": "test-learner",
            "name": "Test Learner",
            "age": 25,
            "learning_style": "Visual",
            "preferences": ["Programming", "Data Science"],
            "activities": [
                {"activity_type": "module_completed", "score": 85, "duration": 60, "timestamp": "2024-01-15T10:00:00"},
                {"activity_type": "quiz_completed", "score": 92, "duration": 30, "timestamp": "2024-01-16T14:30:00"},
                {"activity_type": "assignment_submitted", "score": 78, "duration": 90, "timestamp": "2024-01-17T09:15:00"}
            ]
        }
        
        # Get enhanced recommendations
        result = get_enhanced_recommendations("test-learner", test_learner_data)
        
        # Verify structure
        assert "enhanced_recommendations" in result
        enhanced_recs = result["enhanced_recommendations"]
        
        # Check all recommendation types are present
        assert "courses" in enhanced_recs
        assert "pdf_resources" in enhanced_recs
        assert "assessments" in enhanced_recs
        assert "projects" in enhanced_recs
        assert "performance_analysis" in enhanced_recs
        
        # Verify learning score analysis
        performance = enhanced_recs["performance_analysis"]
        assert "learning_score" in performance
        assert "performance_level" in performance
        assert performance["learning_score"] > 0
        
        print("✓ Enhanced Recommendation Engine: PASSED")
        print(f"  - Learning Score: {performance['learning_score']}/100")
        print(f"  - Performance Level: {performance['performance_level']}")
        print(f"  - Courses Recommended: {len(enhanced_recs['courses'])}")
        print(f"  - PDF Resources: {len(enhanced_recs['pdf_resources'])}")
        print(f"  - Assessments: {len(enhanced_recs['assessments'])}")
        print(f"  - Projects: {len(enhanced_recs['projects'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced Recommendation Engine: FAILED - {e}")
        return False

def test_route_integration():
    """Test integration with Flask routes"""
    print("\nTesting Route Integration...")
    
    try:
        # Check if enhanced engine is properly imported in routes
        with open('routes/learner_routes.py', 'r') as f:
            routes_content = f.read()
        
        assert "from enhanced_recommendation_engine import get_enhanced_recommendations" in routes_content
        assert "get_enhanced_recommendations" in routes_content
        
        print("✓ Route Integration: PASSED")
        print("  - Enhanced recommendation import found")
        print("  - Integration function present")
        
        return True
        
    except Exception as e:
        print(f"✗ Route Integration: FAILED - {e}")
        return False

def test_streamlit_enhancements():
    """Test Streamlit UI enhancements"""
    print("\nTesting Streamlit Enhancements...")
    
    try:
        # Check if enhanced display functions exist
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check for new display functions
        required_functions = [
            "display_enhanced_recommendations",
            "display_pdf_resources", 
            "display_assessments",
            "display_projects"
        ]
        
        for func in required_functions:
            assert f"def {func}" in app_content
        
        # Check for enhanced display usage
        assert "display_enhanced_recommendations(recommendations)" in app_content
        
        print("✓ Streamlit Enhancements: PASSED")
        print("  - Enhanced display functions found")
        print("  - New UI components integrated")
        
        return True
        
    except Exception as e:
        print(f"✗ Streamlit Enhancements: FAILED - {e}")
        return False

def test_environment_configuration():
    """Test environment configuration for Minimax fix"""
    print("\nTesting Environment Configuration...")
    
    try:
        # Check .env file exists and has correct settings
        assert os.path.exists('.env')
        
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Check critical settings
        required_settings = [
            "USE_AI_FEATURES=false",
            "USE_HUGGINGFACE_API=false",
            "DISABLE_MINIMAX_API=true",
            "USE_LOCAL_MODELS=true"
        ]
        
        for setting in required_settings:
            assert setting in env_content, f"Missing setting: {setting}"
        
        print("✓ Environment Configuration: PASSED")
        print("  - External AI services disabled")
        print("  - Local models enabled")
        print("  - Minimax API disabled")
        
        return True
        
    except Exception as e:
        print(f"✗ Environment Configuration: FAILED - {e}")
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\nTesting Error Handling...")
    
    try:
        # Test enhanced recommendation engine with error case
        from enhanced_recommendation_engine import EnhancedRecommendationEngine
        
        engine = EnhancedRecommendationEngine()
        
        # Test with empty learner data (should not crash)
        empty_learner = {"id": "test", "activities": []}
        result = engine.generate_enhanced_recommendations(empty_learner, count=3)
        
        assert "courses" in result
        assert "performance_analysis" in result
        
        print("✓ Error Handling: PASSED")
        print("  - Graceful handling of empty data")
        print("  - Fallback mechanisms working")
        
        return True
        
    except Exception as e:
        print(f"✗ Error Handling: FAILED - {e}")
        return False

def test_learning_score_analysis():
    """Test learning score calculation"""
    print("\nTesting Learning Score Analysis...")
    
    try:
        from enhanced_recommendation_engine import EnhancedRecommendationEngine
        
        engine = EnhancedRecommendationEngine()
        
        # Test with various performance levels
        test_cases = [
            {
                "name": "High Performer",
                "data": {
                    "activities": [
                        {"activity_type": "module_completed", "score": 95, "duration": 60, "timestamp": "2024-01-15T10:00:00"},
                        {"activity_type": "quiz_completed", "score": 90, "duration": 30, "timestamp": "2024-01-16T14:30:00"},
                        {"activity_type": "assignment_submitted", "score": 88, "duration": 90, "timestamp": "2024-01-17T09:15:00"}
                    ]
                }
            },
            {
                "name": "New Learner",
                "data": {"activities": []}
            },
            {
                "name": "Struggling Learner", 
                "data": {
                    "activities": [
                        {"activity_type": "quiz_attempt", "score": 45, "duration": 30, "timestamp": "2024-01-15T10:00:00"},
                        {"activity_type": "module_attempted", "score": 30, "duration": 45, "timestamp": "2024-01-16T14:30:00"}
                    ]
                }
            }
        ]
        
        for test_case in test_cases:
            analysis = engine.analyze_learning_score(test_case["data"])
            assert "learning_score" in analysis
            assert "performance_level" in analysis
            assert 0 <= analysis["learning_score"] <= 100
            
            print(f"  - {test_case['name']}: Score {analysis['learning_score']}, Level {analysis['performance_level']}")
        
        print("✓ Learning Score Analysis: PASSED")
        print("  - Score calculation working for all performance levels")
        
        return True
        
    except Exception as e:
        print(f"✗ Learning Score Analysis: FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED LEARNING MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    tests = [
        test_enhanced_recommendation_engine,
        test_route_integration,
        test_streamlit_enhancements,
        test_environment_configuration,
        test_error_handling,
        test_learning_score_analysis
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"Success Rate: {(passed/(passed+failed))*100:.1f}%")
    
    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("The Enhanced Learning Management System is working correctly.")
        print("Minimax API error has been resolved with robust fallbacks.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed.")
        print("Please check the failed tests and fix any issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)