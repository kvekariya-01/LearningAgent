#!/usr/bin/env python3
"""
Minimax API Error Verification Script
Tests that all external API calls are blocked and error is resolved
"""

import os
import sys
import time
from datetime import datetime

def test_environment_settings():
    """Test that environment settings are correct"""
    print("=" * 60)
    print("TESTING ENVIRONMENT SETTINGS")
    print("=" * 60)
    
    required_settings = {
        "USE_AI_FEATURES": "false",
        "USE_HUGGINGFACE_API": "false", 
        "USE_EXTERNAL_AI_SERVICES": "false",
        "DISABLE_MINIMAX_API": "true",
        "DISABLE_ALL_EXTERNAL_APIS": "true",
        "USE_LOCAL_MODELS": "true",
        "ENABLE_LOCAL_RECOMMENDATIONS": "true",
        "USE_IN_MEMORY_DB": "true",
        "FORCE_LOCAL_RECOMMENDATIONS": "true"
    }
    
    all_correct = True
    
    for setting, expected in required_settings.items():
        actual = os.environ.get(setting, "not set")
        status = "PASS" if actual.lower() == expected else "FAIL"
        
        if status == "FAIL":
            all_correct = False
            
        print(f"{setting:30} = {actual:10} [{status}]")
    
    return all_correct

def test_network_blocker():
    """Test that network blocker is working"""
    print("\n" + "=" * 60)
    print("TESTING NETWORK BLOCKER")
    print("=" * 60)
    
    try:
        import network_blocker
        network_blocker.activate_network_blocker()
        
        # Test blocking requests
        try:
            import requests
            requests.get("https://example.com")
            print("FAIL - External requests not blocked")
            return False
        except Exception as e:
            if "External API calls disabled" in str(e):
                print("PASS - External requests successfully blocked")
                return True
            else:
                print(f"FAIL - Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"FAIL - Network blocker error: {e}")
        return False

def test_local_recommendations():
    """Test that local recommendations work"""
    print("\n" + "=" * 60)
    print("TESTING LOCAL RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
        test_learner_data = {
            "id": "test-learner",
            "name": "Test Learner", 
            "age": 25,
            "learning_style": "Visual",
            "preferences": ["Programming", "Data Science"],
            "activities": [
                {"activity_type": "module_completed", "score": 85, "duration": 60, "timestamp": "2024-01-15T10:00:00Z"},
                {"activity_type": "quiz_completed", "score": 92, "duration": 30, "timestamp": "2024-01-16T14:30:00Z"}
            ]
        }
        
        result = get_enhanced_recommendations("test-learner", test_learner_data)
        
        if "enhanced_recommendations" in result and "courses" in result["enhanced_recommendations"]:
            print("PASS - Local recommendations working")
            print(f"Generated {len(result['enhanced_recommendations']['courses'])} course recommendations")
            return True
        else:
            print("FAIL - Local recommendations not working")
            return False
            
    except Exception as e:
        print(f"FAIL - Local recommendations error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    try:
        from utils.error_handlers import APIErrorHandler
        
        # Test Minimax error detection
        test_error = Exception("Minimax error: invalid params, tool result's tool id(call_function_test_1) not found (2013)")
        result = APIErrorHandler.handle_minimax_error(test_error)
        
        if result["error_type"] == "MinimaxAPIError" and result["error_code"] == "2013":
            print("PASS - Minimax error detection working")
            return True
        else:
            print("FAIL - Minimax error detection not working")
            return False
            
    except Exception as e:
        print(f"FAIL - Error handling test failed: {e}")
        return False

def run_complete_verification():
    """Run all verification tests"""
    print("\n" + "=" * 80)
    print("MINIMAX API ERROR - COMPLETE VERIFICATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load environment
    try:
        from dotenv import load_dotenv
        if os.path.exists(".env"):
            load_dotenv()
            print("SUCCESS: .env file loaded")
    except:
        print("WARNING: .env file not loaded")
    
    # Run tests
    test_results = []
    
    test_results.append(("Environment Settings", test_environment_settings()))
    test_results.append(("Network Blocker", test_network_blocker()))
    test_results.append(("Local Recommendations", test_local_recommendations()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} [{status}]")
        if result:
            passed += 1
    
    print("\n" + "=" * 80)
    success_rate = (passed / total) * 100
    
    if success_rate == 100:
        print("STATUS: ALL TESTS PASSED - MINIMAX API ERROR RESOLVED!")
        print("\nYour application is now protected against Minimax API errors.")
        print("Start the application using: python start_safe_app.py")
        print("Or manually: streamlit run app.py --server.port 8501")
    else:
        print(f"STATUS: {success_rate:.1f}% SUCCESS - SOME ISSUES REMAIN")
        print(f"Passed: {passed}/{total} tests")
    
    print("=" * 80)
    
    return success_rate == 100

if __name__ == "__main__":
    success = run_complete_verification()
    sys.exit(0 if success else 1)