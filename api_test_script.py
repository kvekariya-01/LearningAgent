#!/usr/bin/env python3
"""
Learning Agent API Test Script
Validates the MongoDB Atlas integration and all Postman collection endpoints
"""

import requests
import json
import time
from datetime import datetime

class LearningAgentTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.learner_id = None
        self.test_results = []
    
    def log_test(self, test_name, success, response=None, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "error": str(error) if error else None
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}")
        if not success and error:
            print(f"    Error: {error}")
    
    def test_home(self):
        """Test home endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.log_test("Home Page", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Home Page", False, error=e)
            return False
    
    def test_register_learner(self):
        """Test learner registration"""
        try:
            data = {
                "name": "Test Learner",
                "age": 25,
                "gender": "male",
                "learning_style": "visual",
                "preferences": ["videos", "quizzes"]
            }
            response = requests.post(f"{self.base_url}/api/learner/register", json=data)
            success = response.status_code == 201
            
            if success:
                result = response.json()
                self.learner_id = result.get("id")
                self.log_test("Register Learner", True, result)
                return True
            else:
                self.log_test("Register Learner", False, response.json(), f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Register Learner", False, error=e)
            return False
    
    def test_get_learners(self):
        """Test get all learners"""
        try:
            response = requests.get(f"{self.base_url}/api/learners")
            success = response.status_code == 200
            self.log_test("Get All Learners", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Get All Learners", False, error=e)
            return False
    
    def test_get_learner_by_id(self):
        """Test get specific learner"""
        if not self.learner_id:
            self.log_test("Get Learner by ID", False, error="No learner ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/learner/{self.learner_id}")
            success = response.status_code == 200
            self.log_test("Get Learner by ID", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Get Learner by ID", False, error=e)
            return False
    
    def test_log_activity(self):
        """Test activity logging"""
        if not self.learner_id:
            self.log_test("Log Activity", False, error="No learner ID available")
            return False
            
        try:
            data = {
                "activity_type": "module_completed",
                "duration": 45.5,
                "score": 85
            }
            response = requests.post(f"{self.base_url}/api/learner/{self.learner_id}/activity", json=data)
            success = response.status_code == 201
            self.log_test("Log Activity", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Log Activity", False, error=e)
            return False
    
    def test_analytics(self):
        """Test analytics endpoint"""
        if not self.learner_id:
            self.log_test("Learner Analytics", False, error="No learner ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/analytics/learner/{self.learner_id}")
            success = response.status_code == 200
            self.log_test("Learner Analytics", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Learner Analytics", False, error=e)
            return False
    
    def test_cohort_analytics(self):
        """Test cohort comparison analytics"""
        try:
            response = requests.get(f"{self.base_url}/api/analytics/cohort?group_by=learning_style")
            success = response.status_code == 200
            self.log_test("Cohort Analytics", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Cohort Analytics", False, error=e)
            return False
    
    def test_system_analytics(self):
        """Test system analytics summary"""
        try:
            response = requests.get(f"{self.base_url}/api/analytics/summary")
            success = response.status_code == 200
            self.log_test("System Analytics", success, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("System Analytics", False, error=e)
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting Learning Agent API Tests...")
        print("=" * 50)
        
        # Test sequence
        tests = [
            self.test_home,
            self.test_register_learner,
            self.test_get_learners,
            self.test_get_learner_by_id,
            self.test_log_activity,
            self.test_analytics,
            self.test_cohort_analytics,
            self.test_system_analytics
        ]
        
        for test_func in tests:
            test_func()
            time.sleep(0.5)  # Small delay between tests
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for test in self.test_results if test["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\nAll tests passed! Your API is working correctly with MongoDB Atlas.")
        else:
            print("\nSome tests failed. Check the logs above for details.")
        
        # Save results to file
        with open("api_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: api_test_results.json")

def main():
    """Main test function"""
    print("Learning Agent API Test Suite")
    print("Testing MongoDB Atlas Integration...")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("API server is running")
    except requests.exceptions.RequestException:
        print("API server is not running!")
        print("Please start the server with: python app.py")
        return
    
    # Run tests
    tester = LearningAgentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()