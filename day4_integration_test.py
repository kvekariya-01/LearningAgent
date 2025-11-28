#!/usr/bin/env python3
"""
DAY 4 - Frontend Integration Test Suite
Comprehensive testing for the integrated learner and instructor dashboards
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class FrontendIntegrationTester:
    """Test suite for DAY 4 frontend integration"""
    
    def __init__(self, api_base_url="http://localhost:5001"):
        self.api_base_url = api_base_url
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        return success
    
    def test_api_connection(self):
        """Test API server connectivity"""
        try:
            response = requests.get(f"{self.api_base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "API Connection", 
                    True, 
                    f"Connected - Version: {data.get('version', 'unknown')}"
                )
            else:
                return self.log_test(
                    "API Connection", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            return self.log_test(
                "API Connection", 
                False, 
                f"Connection error: {str(e)}"
            )
    
    def test_learner_endpoints(self):
        """Test learner-related API endpoints"""
        endpoints = [
            "/api/learners",
            "/api/courses"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Endpoint {endpoint}", 
                        True, 
                        f"Status 200 - Data received"
                    )
                else:
                    self.log_test(
                        f"Endpoint {endpoint}", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    f"Endpoint {endpoint}", 
                    False, 
                    f"Error: {str(e)}"
                )
    
    def test_enhanced_endpoints(self):
        """Test enhanced scoring and recommendation endpoints"""
        test_learner_id = "demo-alice-123"
        endpoints = [
            f"/api/learner/{test_learner_id}/score",
            f"/api/learner/{test_learner_id}/recommendations",
            f"/api/learner/{test_learner_id}/learning-path",
            "/api/analytics/learners"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Enhanced Endpoint {endpoint}", 
                        True, 
                        f"Status 200 - Enhanced data received"
                    )
                else:
                    self.log_test(
                        f"Enhanced Endpoint {endpoint}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_test(
                    f"Enhanced Endpoint {endpoint}", 
                    False, 
                    f"Error: {str(e)}"
                )
    
    def test_batch_operations(self):
        """Test batch operations endpoints"""
        try:
            # Test batch score calculation
            test_data = {
                "learner_ids": ["demo-alice-123", "demo-bob-456"]
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/batch/calculate-scores",
                json=test_data,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Batch Score Calculation", 
                    True, 
                    f"Processed {result.get('successful_calculations', 0)} learners"
                )
            else:
                self.log_test(
                    "Batch Score Calculation", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Batch Score Calculation", 
                False, 
                f"Error: {str(e)}"
            )
    
    def test_frontend_files(self):
        """Test if frontend files exist and are valid"""
        frontend_files = [
            "day4_learner_dashboard.py",
            "day4_instructor_dashboard.py",
            "day4_launcher.py"
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 1000:  # Basic size check
                            self.log_test(
                                f"File {file_path}", 
                                True, 
                                f"Exists and has content ({len(content)} chars)"
                            )
                        else:
                            self.log_test(
                                f"File {file_path}", 
                                False, 
                                f"File exists but seems incomplete ({len(content)} chars)"
                            )
                except Exception as e:
                    self.log_test(
                        f"File {file_path}", 
                        False, 
                        f"Error reading file: {str(e)}"
                    )
            else:
                self.log_test(
                    f"File {file_path}", 
                    False, 
                    "File does not exist"
                )
    
    def test_streamlit_dependencies(self):
        """Test if required Streamlit dependencies are available"""
        required_modules = [
            'streamlit',
            'pandas',
            'plotly',
            'requests',
            'numpy'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                self.log_test(
                    f"Module {module}", 
                    True, 
                    "Available"
                )
            except ImportError:
                self.log_test(
                    f"Module {module}", 
                    False, 
                    "Not installed"
                )
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 DAY 4 Frontend Integration Test Suite")
        print("=" * 50)
        
        # Run test categories
        print("\n1️⃣ Testing API Connection...")
        self.test_api_connection()
        
        print("\n2️⃣ Testing Basic Endpoints...")
        self.test_learner_endpoints()
        
        print("\n3️⃣ Testing Enhanced Endpoints...")
        self.test_enhanced_endpoints()
        
        print("\n4️⃣ Testing Batch Operations...")
        self.test_batch_operations()
        
        print("\n5️⃣ Testing Frontend Files...")
        self.test_frontend_files()
        
        print("\n6️⃣ Testing Dependencies...")
        self.test_streamlit_dependencies()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Save results
        with open('day4_integration_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: day4_integration_test_results.json")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("DAY 4 Frontend Integration Test Suite")
    print("Testing the integrated learner and instructor dashboards")
    print()
    
    # Check if API server is running
    api_url = "http://localhost:5001"
    print(f"Testing API connectivity to {api_url}...")
    
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            api_available = True
        else:
            print(f"⚠️ API server responded with status {response.status_code}")
            api_available = False
    except requests.exceptions.RequestException:
        print("❌ API server is not responding")
        print("💡 Make sure the enhanced Flask API is running before testing")
        api_available = False
    
    print()
    
    # Run tests
    tester = FrontendIntegrationTester(api_url)
    all_passed = tester.run_all_tests()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! DAY 4 Integration is working correctly.")
        print("\n🚀 You can now launch the dashboards:")
        print("   python day4_launcher.py")
        print("\n🌐 Access URLs:")
        print("   Learner Dashboard: http://localhost:8501")
        print("   Instructor Dashboard: http://localhost:8502")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the enhanced Flask API is running on port 5001")
        print("2. Install any missing dependencies: pip install -r requirements.txt")
        print("3. Check that all DAY 4 files are present")
        print("4. Review the detailed test results for specific errors")

if __name__ == "__main__":
    main()