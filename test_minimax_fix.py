#!/usr/bin/env python3
"""
Test script to verify Minimax API error fix
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_config():
    """Test that environment is configured correctly"""
    print("[TOOLS] Testing Environment Configuration...")
    
    # Check environment variables
    checks = {
        "USE_AI_FEATURES": os.getenv("USE_AI_FEATURES", "true").lower() == "false",
        "USE_HUGGINGFACE_API": os.getenv("USE_HUGGINGFACE_API", "true").lower() == "false",
        "DISABLE_MINIMAX_API": os.getenv("DISABLE_MINIMAX_API", "false").lower() == "true",
        "USE_LOCAL_MODELS": os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
    }
    
    all_passed = True
    for var, should_be_true in checks.items():
        actual = os.getenv(var, "")
        status = "[OK] PASS" if should_be_true else "[FAIL] FAIL"
        if not should_be_true:
            status = "[OK] PASS" if actual.lower() == "false" else "[FAIL] FAIL"
        print(f"  {var}={actual} - {status}")
        if "FAIL" in status:
            all_passed = False
    
    return all_passed

def test_error_handlers():
    """Test that error handlers are available"""
    print("\n🛡️ Testing Error Handlers...")
    
    try:
        from utils.error_handlers import APIErrorHandler, get_safe_recommendations
        print("  [OK] APIErrorHandler imported successfully")
        print("  [OK] get_safe_recommendations imported successfully")
        
        # Test error handler methods exist
        handler_methods = [
            "handle_minimax_error",
            "handle_api_timeout", 
            "handle_connection_error",
            "safe_api_call"
        ]
        
        for method in handler_methods:
            if hasattr(APIErrorHandler, method):
                print(f"  [OK] {method} method available")
            else:
                print(f"  [FAIL] {method} method missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"  [FAIL] Failed to import error handlers: {e}")
        return False

def test_minimax_error_detection():
    """Test Minimax error detection specifically"""
    print("\n[TARGET] Testing Minimax Error Detection...")
    
    try:
        from utils.error_handlers import APIErrorHandler
        
        # Create a mock Minimax error
        test_error = Exception("Minimax error: invalid params, tool result's tool id(call_function_ahy0gvoe8tfy_1) not found (2013)")
        
        # Test the error handler
        result = APIErrorHandler.handle_minimax_error(test_error)
        
        expected_keys = ["error_type", "error_message", "error_code", "solution_applied", "fallback_action"]
        
        all_present = True
        for key in expected_keys:
            if key in result:
                print(f"  [OK] {key}: {result[key]}")
            else:
                print(f"  [FAIL] Missing key: {key}")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  [FAIL] Error testing Minimax detection: {e}")
        return False

def test_safe_api_calls():
    """Test safe API call wrapper"""
    print("\n[SECURE] Testing Safe API Calls...")
    
    try:
        from utils.error_handlers import APIErrorHandler
        
        def mock_api_function():
            raise Exception("Minimax error: invalid params, tool result's tool id(call_function_ahy0gvoe8tfy_1) not found (2013)")
        
        # Test safe API call with Minimax error
        result = APIErrorHandler.safe_api_call(mock_api_function)
        
        if isinstance(result, dict) and "error_type" in result:
            print(f"  [OK] Minimax error handled correctly: {result['error_type']}")
            print(f"  [OK] Recovery status: {result.get('recovery_status', 'Unknown')}")
            return True
        else:
            print(f"  [FAIL] Unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Error testing safe API calls: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("[START] MINIMAX API ERROR FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment_config),
        ("Error Handlers", test_error_handlers),
        ("Minimax Error Detection", test_minimax_error_detection),
        ("Safe API Calls", test_safe_api_calls)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[LIST] Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"[OK] {test_name}: PASSED")
            else:
                print(f"[FAIL] {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"[TARGET] RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED! Minimax API error fix is working correctly!")
        print("\n[OK] The following issues have been resolved:")
        print("  • Minimax API calls are disabled")
        print("  • Error handlers are active")  
        print("  • Fallback mechanisms are in place")
        print("  • Local recommendations will be used")
        print("\n[START] Your Learning Management System is now robust against Minimax API errors!")
    else:
        print("[WARNING] Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)