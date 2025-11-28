#!/usr/bin/env python3
"""
Simple Test to Verify Minimax API Error Fix
This test verifies that the system no longer makes external API calls and works with local recommendations only.
"""

import os
import sys
import json
import time

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
    print("\n[TEST] Environment Configuration")
    
    # Check environment variables
    use_ai_features = os.environ.get("USE_AI_FEATURES", "false").lower()
    disable_minimax = os.environ.get("DISABLE_MINIMAX_API", "false").lower()
    force_local = os.environ.get("FORCE_LOCAL_RECOMMENDATIONS", "false").lower()
    
    print(f"  USE_AI_FEATURES: {use_ai_features}")
    print(f"  DISABLE_MINIMAX_API: {disable_minimax}")
    print(f"  FORCE_LOCAL_RECOMMENDATIONS: {force_local}")
    
    # Should all be set to disable external APIs
    success = (use_ai_features == "false" and disable_minimax == "true")
    
    if success:
        print("  [OK] Environment properly configured")
    else:
        print("  [ERROR] Environment not properly configured")
    
    return success

def test_enhanced_recommendation_engine():
    """Test the enhanced recommendation engine doesn't make external API calls"""
    print("\n[TEST] Enhanced Recommendation Engine")
    
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
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
        if not all(key in result for key in ["learner_id", "recommendations", "enhanced_recommendations"]):
            print("  [ERROR] Result missing required keys")
            return False
        
        # Should be using local recommendations
        if result.get("recommendation_type") != "enhanced_local":
            print(f"  [ERROR] Expected 'enhanced_local', got '{result.get('recommendation_type')}'")
            return False
        
        if result.get("enhanced_by") != "EnhancedRecommendationEngine":
            print("  [ERROR] Should be enhanced by local engine")
            return False
        
        print("  [OK] Local recommendations working correctly")
        
        # Test with API base URL but external APIs disabled
        print("  Testing with API base URL (should still use local)...")
        result_with_url = get_enhanced_recommendations("test-learner-123", test_learner_data, "http://fake-api.com")
        
        # Should still use local recommendations due to environment settings
        if result_with_url.get("recommendation_type") != "enhanced_local":
            print("  [ERROR] Should still use local when external APIs disabled")
            return False
        
        fallback_reason = result_with_url.get("fallback_reason", "")
        if not fallback_reason.startswith("Using local recommendation engine"):
            print("  [ERROR] Should mention local engine usage")
            return False
        
        print("  [OK] External API calls properly blocked")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error testing enhanced recommendation engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handler_functionality():
    """Test that error handlers work properly"""
    print("\n[TEST] Error Handler Functionality")
    
    try:
        from utils.error_handlers import APIErrorHandler
        
        # Test Minimax error detection
        test_error = Exception("Minimax error: invalid params, tool result's tool id(call_function_rbauxm8k5vhv_1) not found (2013)")
        error_info = APIErrorHandler.handle_minimax_error(test_error)
        
        if error_info["error_type"] != "MinimaxAPIError":
            print("  [ERROR] Should detect Minimax API error")
            return False
        
        if error_info["error_code"] != "2013":
            print("  [ERROR] Should capture error code 2013")
            return False
        
        if "disabled_external_ai" not in error_info["solution_applied"]:
            print("  [ERROR] Should mention solution applied")
            return False
        
        print("  [OK] Minimax error detection working")
        
        # Test safe API call wrapper
        def mock_api_call():
            raise Exception("Some other error")
        
        result = APIErrorHandler.safe_api_call(mock_api_call)
        if "error_type" not in result:
            print("  [ERROR] Should return error info when API call fails")
            return False
        
        print("  [OK] Safe API call wrapper working")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error testing error handlers: {e}")
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
        
        print("  [OK] Enhanced recommendation engine import successful")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error importing enhanced recommendation engine: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("MINIMAX API ERROR FIX - VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("Enhanced Recommendation Engine", test_enhanced_recommendation_engine),
        ("Error Handler Functionality", test_error_handler_functionality),
        ("Learner Routes Imports", test_learner_routes_imports)
    ]
    
    results = []
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[INFO] Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  [ERROR] Test failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {total_tests} tests")
    print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    if failed == 0:
        print("\nSUCCESS: ALL TESTS PASSED!")
        print("[OK] Minimax API error has been successfully resolved!")
        print("[OK] System is now using local recommendations only")
        print("[OK] No external API calls will be made")
        return True
    else:
        print(f"\nWARNING: {failed} test(s) failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)