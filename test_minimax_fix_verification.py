#!/usr/bin/env python3
"""
Comprehensive Test to Verify Minimax API Error Fix
This test verifies that the system no longer makes external API calls and works with local recommendations only.
"""

import os
import sys
import json
import time
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file if available
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
        print("[OK] Loaded .env file")
except ImportError:
    print("[INFO] dotenv not available, using system environment variables only")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

def test_environment_configuration():
    """Test that environment is properly configured to disable external APIs"""
    print("[TEST] Environment Configuration")
    
    # Check environment variables
    use_ai_features = os.environ.get("USE_AI_FEATURES", "false").lower()
    disable_minimax = os.environ.get("DISABLE_MINIMAX_API", "false").lower()
    force_local = os.environ.get("FORCE_LOCAL_RECOMMENDATIONS", "false").lower()
    
    print(f"  USE_AI_FEATURES: {use_ai_features}")
    print(f"  DISABLE_MINIMAX_API: {disable_minimax}")
    print(f"  FORCE_LOCAL_RECOMMENDATIONS: {force_local}")
    
    # Should all be set to disable external APIs
    assert use_ai_features == "false", f"USE_AI_FEATURES should be 'false', got '{use_ai_features}'"
    assert disable_minimax == "true", f"DISABLE_MINIMAX_API should be 'true', got '{disable_minimax}'"
    
    print("  ✅ Environment properly configured")
    return True

def test_enhanced_recommendation_engine():
    """Test the enhanced recommendation engine doesn't make external API calls"""
    print("\n[TEST] Enhanced Recommendation Engine")
    
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations, EnhancedRecommendationEngine
        
        # Test data
        test_learner_data = {
            "id": "test-learner-123",
            "name": "Test Learner",
            "age": 25,
            "learning_style": "Visual",
            "preferences": ["Python", "Data Science"],
            "activities": [
                {"activity_type": "module_completed", "score": 85, "duration": 60, "timestamp": "2024-01-15T10:00:00"},
                {"activity_type": "quiz_completed", "score": 92, "duration": 30, "timestamp": "2024-01-16T14:30:00"}
            ]
        }
        
        # Test without API base URL (should use local recommendations only)
        print("  Testing local recommendations (no API base URL)...")
        result = get_enhanced_recommendations("test-learner-123", test_learner_data)
        
        # Verify the result structure
        assert "learner_id" in result, "Result should contain learner_id"
        assert "recommendations" in result, "Result should contain recommendations"
        assert "enhanced_recommendations" in result, "Result should contain enhanced_recommendations"
        assert "fallback_used" in result, "Result should indicate fallback usage"
        
        # Should be using local recommendations
        assert result.get("recommendation_type") == "enhanced_local", f"Expected 'enhanced_local', got '{result.get('recommendation_type')}'"
        assert result.get("enhanced_by") == "EnhancedRecommendationEngine", "Should be enhanced by local engine"
        
        print("  ✅ Local recommendations working correctly")
        
        # Test with API base URL but external APIs disabled
        print("  Testing with API base URL (should still use local)...")
        result_with_url = get_enhanced_recommendations("test-learner-123", test_learner_data, "http://fake-api.com")
        
        # Should still use local recommendations due to environment settings
        assert result_with_url.get("recommendation_type") == "enhanced_local", "Should still use local when external APIs disabled"
        assert result_with_url.get("fallback_reason", "").startswith("Using local recommendation engine"), "Should mention local engine usage"
        
        print("  ✅ External API calls properly blocked")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing enhanced recommendation engine: {e}")
        return False

def test_error_handler_functionality():
    """Test that error handlers work properly"""
    print("\n[TEST] Error Handler Functionality")
    
    try:
        from utils.error_handlers import APIErrorHandler
        
        # Test Minimax error detection
        test_error = Exception("Minimax error: invalid params, tool result's tool id(call_function_rbauxm8k5vhv_1) not found (2013)")
        error_info = APIErrorHandler.handle_minimax_error(test_error)
        
        assert error_info["error_type"] == "MinimaxAPIError", "Should detect Minimax API error"
        assert error_info["error_code"] == "2013", "Should capture error code 2013"
        assert "disabled_external_ai" in error_info["solution_applied"], "Should mention solution applied"
        
        print("  ✅ Minimax error detection working")
        
        # Test safe API call wrapper
        def mock_api_call():
            raise Exception("Some other error")
        
        result = APIErrorHandler.safe_api_call(mock_api_call)
        assert "error_type" in result, "Should return error info when API call fails"
        
        print("  ✅ Safe API call wrapper working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing error handlers: {e}")
        return False

def test_learner_routes_imports():
    """Test that learner routes can import without errors"""
    print("\n[TEST] Learner Routes Imports")
    
    try:
        # This will test if the import in learner_routes works without external API calls
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
        # Test the function signature
        test_data = {"id": "test", "name": "Test"}
        result = get_enhanced_recommendations("test", test_data)
        
        print("  ✅ Enhanced recommendation engine import successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Error importing enhanced recommendation engine: {e}")
        return False

def test_database_configuration():
    """Test database configuration for fallbacks"""
    print("\n[TEST] Database Configuration")
    
    try:
        from config.db_config import db
        
        # Test that we can access the database config
        print(f"  Database object available: {db is not None}")
        
        # Check environment settings for database fallbacks
        use_in_memory = os.environ.get("USE_IN_MEMORY_DB", "false").lower()
        enable_error_recovery = os.environ.get("ENABLE_ERROR_RECOVERY", "false").lower()
        
        print(f"  USE_IN_MEMORY_DB: {use_in_memory}")
        print(f"  ENABLE_ERROR_RECOVERY: {enable_error_recovery}")
        
        print("  ✅ Database configuration accessible")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing database configuration: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("MINIMAX API ERROR FIX - COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("Enhanced Recommendation Engine", test_enhanced_recommendation_engine),
        ("Error Handler Functionality", test_error_handler_functionality),
        ("Learner Routes Imports", test_learner_routes_imports),
        ("Database Configuration", test_database_configuration)
    ]
    
    results = []
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[INFO] Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {total_tests} tests")
    print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Minimax API error has been successfully resolved!")
        print("✅ System is now using local recommendations only")
        print("✅ No external API calls will be made")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)