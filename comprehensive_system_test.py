#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Enhanced Learning Agent
Tests all APIs, scoring system, and recommendation engine functionality
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta
import traceback
from typing import Dict, List, Any, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EnhancedSystemTester:
    """Comprehensive testing suite for the enhanced learning system"""
    
    def __init__(self, api_base_url: str = "http://localhost:5001"):
        self.api_base_url = api_base_url
        self.test_results = []
        self.failed_tests = []
        self.start_time = datetime.now()
        
        # Test data
        self.sample_learners = [
            {
                "id": "test-learner-high",
                "name": "Test High Performer",
                "age": 25,
                "gender": "Other",
                "learning_style": "Visual",
                "preferences": ["Python", "Data Science", "Machine Learning"],
                "activities": [
                    {"activity_type": "test_completed", "timestamp": "2024-01-15T10:00:00", "score": 95, "duration": 60},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 92, "duration": 30},
                    {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 94, "duration": 120},
                    {"activity_type": "module_completed", "timestamp": "2024-01-18T11:00:00", "score": 96, "duration": 90}
                ]
            },
            {
                "id": "test-learner-medium",
                "name": "Test Medium Performer",
                "age": 30,
                "gender": "Female",
                "learning_style": "Kinesthetic",
                "preferences": ["Web Development", "JavaScript", "React"],
                "activities": [
                    {"activity_type": "test_completed", "timestamp": "2024-01-15T10:00:00", "score": 75, "duration": 60},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 78, "duration": 25},
                    {"activity_type": "project_completed", "timestamp": "2024-01-17T16:00:00", "score": 80, "duration": 180}
                ]
            },
            {
                "id": "test-learner-low",
                "name": "Test Low Performer",
                "age": 22,
                "gender": "Male",
                "learning_style": "Auditory",
                "preferences": ["Mathematics", "Physics", "Science"],
                "activities": [
                    {"activity_type": "test_completed", "timestamp": "2024-01-15T10:00:00", "score": 45, "duration": 60},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 52, "duration": 30},
                    {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 48, "duration": 90}
                ]
            },
            {
                "id": "test-learner-new",
                "name": "Test New Learner",
                "age": 19,
                "gender": "Other",
                "learning_style": "Mixed",
                "preferences": ["Programming", "Design"],
                "activities": []  # New learner with no activities
            }
        ]
    
    def log_test_result(self, test_name: str, success: bool, message: str, data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        self.test_results.append(result)
        
        if success:
            print(f"PASS {test_name}: {message}")
        else:
            print(f"FAIL {test_name}: {message}")
            self.failed_tests.append(test_name)
    
    def test_api_health(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "API Health Check",
                    True,
                    f"API is healthy (v{data.get('version', 'unknown')})",
                    data
                )
                return True
            else:
                self.log_test_result(
                    "API Health Check",
                    False,
                    f"API returned status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test_result(
                "API Health Check",
                False,
                f"Failed to connect: {str(e)}"
            )
            return False
    
    def test_course_catalog(self) -> bool:
        """Test course catalog endpoints"""
        try:
            # Test basic catalog
            response = requests.get(f"{self.api_base_url}/api/courses", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                course_count = data.get('total_courses', 0)
                
                self.log_test_result(
                    "Course Catalog",
                    True,
                    f"Loaded {course_count} courses",
                    {"total_courses": course_count}
                )
                
                # Test filtering
                if course_count > 0:
                    # Test subject filter
                    response = requests.get(f"{self.api_base_url}/api/courses?subject=programming", timeout=10)
                    if response.status_code == 200:
                        self.log_test_result(
                            "Course Filtering",
                            True,
                            "Subject filtering works correctly"
                        )
                    else:
                        self.log_test_result(
                            "Course Filtering",
                            False,
                            f"Subject filter failed: {response.status_code}"
                        )
                
                return True
            else:
                self.log_test_result(
                    "Course Catalog",
                    False,
                    f"Failed to load catalog: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test_result(
                "Course Catalog",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_scoring_system(self) -> bool:
        """Test comprehensive scoring system"""
        scoring_tests_passed = 0
        total_scoring_tests = len(self.sample_learners)
        
        for learner in self.sample_learners:
            learner_id = learner['id']
            try:
                response = requests.get(f"{self.api_base_url}/api/learner/{learner_id}/score", timeout=10)
                
                if response.status_code == 200:
                    score_data = response.json()
                    
                    # Validate score structure
                    required_fields = ['overall_score', 'performance_level', 'component_scores']
                    if all(field in score_data for field in required_fields):
                        overall_score = score_data.get('overall_score', 0)
                        performance_level = score_data.get('performance_level', 'unknown')
                        component_scores = score_data.get('component_scores', {})
                        
                        self.log_test_result(
                            f"Scoring - {learner['name']}",
                            True,
                            f"Score: {overall_score:.1f}, Level: {performance_level}",
                            {
                                "overall_score": overall_score,
                                "performance_level": performance_level,
                                "components": list(component_scores.keys())
                            }
                        )
                        scoring_tests_passed += 1
                    else:
                        self.log_test_result(
                            f"Scoring - {learner['name']}",
                            False,
                            "Invalid score structure"
                        )
                else:
                    self.log_test_result(
                        f"Scoring - {learner['name']}",
                        False,
                        f"API returned {response.status_code}"
                    )
            except Exception as e:
                self.log_test_result(
                    f"Scoring - {learner['name']}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return scoring_tests_passed == total_scoring_tests
    
    def test_recommendation_system(self) -> bool:
        """Test recommendation generation"""
        rec_tests_passed = 0
        total_rec_tests = len(self.sample_learners[:3])  # Test with first 3 learners
        
        for learner in self.sample_learners[:3]:
            learner_id = learner['id']
            try:
                response = requests.get(f"{self.api_base_url}/api/learner/{learner_id}/recommendations?count=5", timeout=10)
                
                if response.status_code == 200:
                    rec_data = response.json()
                    
                    # Validate recommendation structure
                    if 'recommendations' in rec_data:
                        recommendations = rec_data.get('recommendations', [])
                        learning_path = rec_data.get('learning_path', {})
                        
                        self.log_test_result(
                            f"Recommendations - {learner['name']}",
                            True,
                            f"Generated {len(recommendations)} recommendations, path: {'[OK]' if learning_path else '[FAIL]'}",
                            {
                                "recommendations_count": len(recommendations),
                                "has_learning_path": bool(learning_path),
                                "insights_count": len(rec_data.get('insights', []))
                            }
                        )
                        rec_tests_passed += 1
                    else:
                        self.log_test_result(
                            f"Recommendations - {learner['name']}",
                            False,
                            "Invalid recommendation structure"
                        )
                else:
                    self.log_test_result(
                        f"Recommendations - {learner['name']}",
                        False,
                        f"API returned {response.status_code}"
                    )
            except Exception as e:
                self.log_test_result(
                    f"Recommendations - {learner['name']}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return rec_tests_passed == total_rec_tests
    
    def test_learning_paths(self) -> bool:
        """Test learning path generation"""
        path_tests_passed = 0
        total_path_tests = len(self.sample_learners[:2])  # Test with first 2 learners
        
        for learner in self.sample_learners[:2]:
            learner_id = learner['id']
            try:
                response = requests.get(f"{self.api_base_url}/api/learner/{learner_id}/learning-path", timeout=10)
                
                if response.status_code == 200:
                    path_data = response.json()
                    
                    # Validate learning path structure
                    learning_path = path_data.get('learning_path', {})
                    if learning_path and 'courses' in learning_path:
                        courses = learning_path.get('courses', [])
                        milestones = learning_path.get('milestones', [])
                        assessments = learning_path.get('assessment_points', [])
                        
                        self.log_test_result(
                            f"Learning Path - {learner['name']}",
                            True,
                            f"Generated path with {len(courses)} courses, {len(milestones)} milestones",
                            {
                                "courses_count": len(courses),
                                "milestones_count": len(milestones),
                                "assessments_count": len(assessments),
                                "total_duration": learning_path.get('total_estimated_duration', 0)
                            }
                        )
                        path_tests_passed += 1
                    else:
                        self.log_test_result(
                            f"Learning Path - {learner['name']}",
                            False,
                            "Invalid learning path structure"
                        )
                else:
                    self.log_test_result(
                        f"Learning Path - {learner['name']}",
                        False,
                        f"API returned {response.status_code}"
                    )
            except Exception as e:
                self.log_test_result(
                    f"Learning Path - {learner['name']}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return path_tests_passed == total_path_tests
    
    def test_analytics_endpoints(self) -> bool:
        """Test analytics endpoints"""
        analytics_passed = 0
        total_analytics_tests = 2
        
        try:
            # Test learner analytics
            response = requests.get(f"{self.api_base_url}/api/analytics/learners", timeout=10)
            if response.status_code == 200:
                analytics_data = response.json()
                self.log_test_result(
                    "Learner Analytics",
                    True,
                    f"Generated analytics for {analytics_data.get('total_learners', 0)} learners",
                    {
                        "total_learners": analytics_data.get('total_learners', 0),
                        "average_score": analytics_data.get('average_score', 0)
                    }
                )
                analytics_passed += 1
            else:
                self.log_test_result(
                    "Learner Analytics",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Learner Analytics",
                False,
                f"Error: {str(e)}"
            )
        
        try:
            # Test performance insights
            response = requests.get(f"{self.api_base_url}/api/analytics/performance-insights", timeout=10)
            if response.status_code == 200:
                insights_data = response.json()
                component_analysis = insights_data.get('component_analysis', {})
                self.log_test_result(
                    "Performance Insights",
                    True,
                    f"Generated insights with {len(component_analysis)} components",
                    {
                        "components_analyzed": len(component_analysis),
                        "recommendations_count": len(insights_data.get('recommendations', []))
                    }
                )
                analytics_passed += 1
            else:
                self.log_test_result(
                    "Performance Insights",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Performance Insights",
                False,
                f"Error: {str(e)}"
            )
        
        return analytics_passed == total_analytics_tests
    
    def test_batch_operations(self) -> bool:
        """Test batch operations"""
        batch_tests_passed = 0
        total_batch_tests = 2
        
        # Prepare learner IDs for batch testing
        learner_ids = [learner['id'] for learner in self.sample_learners[:3]]
        
        try:
            # Test batch score calculation
            response = requests.post(
                f"{self.api_base_url}/api/batch/calculate-scores",
                json={"learner_ids": learner_ids},
                timeout=30
            )
            
            if response.status_code == 200:
                batch_data = response.json()
                successful = batch_data.get('successful_calculations', 0)
                total = batch_data.get('total_requested', 0)
                
                self.log_test_result(
                    "Batch Score Calculation",
                    successful == total,
                    f"Processed {successful}/{total} learners successfully",
                    {"successful": successful, "total": total}
                )
                batch_tests_passed += 1
            else:
                self.log_test_result(
                    "Batch Score Calculation",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Batch Score Calculation",
                False,
                f"Error: {str(e)}"
            )
        
        try:
            # Test batch recommendation generation
            response = requests.post(
                f"{self.api_base_url}/api/batch/generate-recommendations",
                json={"learner_ids": learner_ids, "count": 3},
                timeout=30
            )
            
            if response.status_code == 200:
                batch_data = response.json()
                successful = batch_data.get('successful_generations', 0)
                total = batch_data.get('total_requested', 0)
                
                self.log_test_result(
                    "Batch Recommendation Generation",
                    successful == total,
                    f"Generated recommendations for {successful}/{total} learners",
                    {"successful": successful, "total": total}
                )
                batch_tests_passed += 1
            else:
                self.log_test_result(
                    "Batch Recommendation Generation",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Batch Recommendation Generation",
                False,
                f"Error: {str(e)}"
            )
        
        return batch_tests_passed == total_batch_tests
    
    def test_specific_recommendation_algorithms(self) -> bool:
        """Test specific recommendation algorithms"""
        algorithm_tests_passed = 0
        total_algorithm_tests = 2
        
        test_learner_id = self.sample_learners[0]['id']  # Use high performer for testing
        
        try:
            # Test score-based recommendations
            response = requests.get(f"{self.api_base_url}/api/learner/{test_learner_id}/recommendations/score-based?count=3", timeout=10)
            if response.status_code == 200:
                rec_data = response.json()
                recommendations = rec_data.get('recommendations', [])
                
                self.log_test_result(
                    "Score-based Recommendations",
                    len(recommendations) > 0,
                    f"Generated {len(recommendations)} score-based recommendations",
                    {"algorithm": "score_based", "count": len(recommendations)}
                )
                algorithm_tests_passed += 1
            else:
                self.log_test_result(
                    "Score-based Recommendations",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Score-based Recommendations",
                False,
                f"Error: {str(e)}"
            )
        
        try:
            # Test interest-based recommendations
            response = requests.get(f"{self.api_base_url}/api/learner/{test_learner_id}/recommendations/interest-based?count=3", timeout=10)
            if response.status_code == 200:
                rec_data = response.json()
                recommendations = rec_data.get('recommendations', [])
                
                self.log_test_result(
                    "Interest-based Recommendations",
                    len(recommendations) > 0,
                    f"Generated {len(recommendations)} interest-based recommendations",
                    {"algorithm": "interest_matching", "count": len(recommendations)}
                )
                algorithm_tests_passed += 1
            else:
                self.log_test_result(
                    "Interest-based Recommendations",
                    False,
                    f"API returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Interest-based Recommendations",
                False,
                f"Error: {str(e)}"
            )
        
        return algorithm_tests_passed == total_algorithm_tests
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in sequence"""
        print("Starting Enhanced Learning Agent Test Suite")
        print("=" * 60)
        
        # Test sequence
        test_sequence = [
            ("API Health Check", self.test_api_health),
            ("Course Catalog", self.test_course_catalog),
            ("Scoring System", self.test_scoring_system),
            ("Recommendation System", self.test_recommendation_system),
            ("Learning Paths", self.test_learning_paths),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("Batch Operations", self.test_batch_operations),
            ("Recommendation Algorithms", self.test_specific_recommendation_algorithms)
        ]
        
        for test_name, test_func in test_sequence:
            print(f"\nRunning {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_test_result(
                    test_name,
                    False,
                    f"Test execution failed: {str(e)}"
                )
                traceback.print_exc()
        
        # Generate test summary
        return self.generate_test_summary()
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "test_run": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "api_base_url": self.api_base_url
            },
            "results": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate
            },
            "test_details": self.test_results,
            "failed_test_names": self.failed_tests,
            "status": "PASSED" if failed_tests == 0 else "FAILED"
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("[STATS] TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"[OK] Passed: {passed_tests}")
        print(f"[FAIL] Failed: {failed_tests}")
        print(f"[GROWTH] Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"[TARGET] Overall Status: {summary['status']}")
        
        if self.failed_tests:
            print("\n[FAIL] Failed Tests:")
            for test in self.failed_tests:
                print(f"  • {test}")
        
        print("\n[START] Test Suite Completed!")
        
        return summary
    
    def save_test_results(self, filename: str = "enhanced_system_test_results.json"):
        """Save test results to file"""
        summary = self.generate_test_summary()
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[DOC] Test results saved to {filename}")

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Learning Agent Test Suite")
    parser.add_argument("--api-url", default="http://localhost:5001", help="API base URL")
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = EnhancedSystemTester(args.api_url)
    
    try:
        # Run all tests
        summary = tester.run_all_tests()
        
        # Save results if requested
        if args.save_results:
            tester.save_test_results()
        
        # Exit with appropriate code
        exit_code = 0 if summary['status'] == 'PASSED' else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n[WARNING] Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()