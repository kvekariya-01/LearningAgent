#!/usr/bin/env python3
"""
Interactive Scoring and Recommendation API Demo
=============================================

This script demonstrates how to interact with the scoring and recommendation system
through API endpoints, showing a complete workflow from submitting test results
to receiving personalized recommendations.

Usage:
    python scoring_api_demo.py
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class ScoringAPIDemo:
    """Interactive demo for scoring and recommendation API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.learner_id = "api-demo-learner"
        
    def check_api_health(self) -> bool:
        """Check if the API is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("API is healthy!")
                print(f"   Database Connected: {health_data.get('database_connected', False)}")
                print(f"   Scoring Enabled: {health_data.get('scoring_enabled', False)}")
                print(f"   Features: {health_data.get('features', {})}")
                return True
            else:
                print(f"API returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to API: {e}")
            print("Make sure the Flask API server is running:")
            print("   python flask_api.py")
            return False
    
    def submit_test_result(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a test result to the scoring system"""
        try:
            response = requests.post(
                f"{self.base_url}/api/scoring/test-result",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"Test result submitted successfully!")
                print(f"   Score: {result['test_result']['percentage']:.1f}%")
                print(f"   Test ID: {result['test_result']['test_id']}")
                return result
            else:
                print(f"Failed to submit test result: {response.status_code}")
                print(f"   Response: {response.text}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Error submitting test result: {e}")
            return {}
    
    def get_score_summary(self) -> Dict[str, Any]:
        """Get the learner's score summary"""
        try:
            response = requests.get(f"{self.base_url}/api/scoring/learner/{self.learner_id}/score-summary")
            
            if response.status_code == 200:
                result = response.json()
                print("📊 Score Summary Retrieved!")
                
                summary = result['score_summary']
                print(f"   Total Tests: {summary['total_tests']}")
                print(f"   Average Score: {summary['average_score']:.1f}%")
                print(f"   Latest Score: {summary['latest_score']:.1f}%")
                print(f"   Performance Trend: {summary['score_trend']}")
                print(f"   Confidence Level: {summary['confidence_score']:.1f}/100")
                print(f"   Recommendation Level: {summary['recommendation_level']}")
                print(f"   Strongest Subject: {summary['strongest_subject']}")
                print(f"   Weakest Subject: {summary['weakest_subject']}")
                
                return result
            else:
                print(f"❌ Failed to get score summary: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting score summary: {e}")
            return {}
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get personalized course recommendations"""
        try:
            response = requests.get(f"{self.base_url}/api/scoring/learner/{self.learner_id}/recommendations")
            
            if response.status_code == 200:
                result = response.json()
                print("🎯 Course Recommendations Retrieved!")
                
                recommendations = result['recommendations']['recommendations']
                print(f"   Number of recommendations: {len(recommendations)}")
                
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"\n   {i}. {rec['title']}")
                    print(f"      Difficulty: {rec['difficulty_level']}")
                    print(f"      Match Score: {rec['match_score']:.1f}/100")
                    print(f"      Confidence: {rec['confidence']:.1f}%")
                    print(f"      Reason: {rec['recommendation_reason']}")
                    print(f"      Estimated Time: {rec['estimated_completion_time']}")
                
                return result
            else:
                print(f"❌ Failed to get recommendations: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting recommendations: {e}")
            return {}
    
    def get_learning_path(self) -> Dict[str, Any]:
        """Get the personalized learning path"""
        try:
            response = requests.get(f"{self.base_url}/api/scoring/learner/{self.learner_id}/learning-path")
            
            if response.status_code == 200:
                result = response.json()
                print("🛤️ Learning Path Retrieved!")
                
                learning_path = result['learning_path']
                path_items = learning_path['learning_path']
                
                print(f"   Path contains {len(path_items)} courses")
                print(f"   Total estimated duration: {learning_path['estimated_duration']}")
                print(f"   Starting level: {learning_path['starting_level'].title()}")
                print(f"   Expected outcome: {learning_path['expected_outcome']}")
                
                print(f"\n   Learning Sequence:")
                for item in path_items[:3]:
                    print(f"   {item['sequence']}. {item['title']}")
                    print(f"      Duration: {item['estimated_time']}")
                    print(f"      Match Confidence: {item['match_confidence']:.1f}%")
                
                return result
            else:
                print(f"❌ Failed to get learning path: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting learning path: {e}")
            return {}
    
    def generate_sample_test_results(self, num_tests: int = 6) -> list:
        """Generate realistic sample test results"""
        test_types = ['quiz', 'test', 'assignment', 'exam']
        course_ids = ['python-101', 'data-science-101', 'web-dev-101']
        
        test_results = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_tests):
            # Simulate improving performance over time
            base_score = 60 + (i * 5) + (i % 3) * 5
            score = min(95, max(50, base_score + (i % 2) * 10 - 5))
            
            test_data = {
                'learner_id': self.learner_id,
                'test_id': f'api_test_{i+1:03d}',
                'test_type': test_types[i % len(test_types)],
                'course_id': course_ids[i % len(course_ids)],
                'score': score,
                'max_score': 100,
                'time_taken': 30 + (i * 5),
                'attempts': 1 if i % 4 != 0 else 2,
                'content_id': f'content_{i+1:03d}',
                'metadata': {
                    'difficulty': 'medium',
                    'questions_count': 20 + (i * 2)
                }
            }
            test_results.append(test_data)
        
        return test_results
    
    def run_complete_workflow_demo(self):
        """Run the complete API workflow demonstration"""
        print("LEARNING AGENT - SCORING & RECOMMENDATION API DEMO")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Learner ID: {self.learner_id}")
        print("=" * 80)
        
        # Step 1: Check API health
        print("\nSTEP 1: CHECKING API HEALTH")
        print("-" * 50)
        if not self.check_api_health():
            print("\nPlease start the API server first:")
            print("   python flask_api.py")
            return
        
        # Step 2: Submit test results
        print("\nSTEP 2: SUBMITTING TEST RESULTS")
        print("-" * 50)
        test_results = self.generate_sample_test_results()
        print(f"Generated {len(test_results)} sample test results")
        
        for i, test_data in enumerate(test_results, 1):
            print(f"\nSubmitting Test {i}: {test_data['test_type']} in {test_data['course_id']}")
            result = self.submit_test_result(test_data)
            if not result:
                break
            time.sleep(0.5)  # Small delay for readability
        
        if not result:
            print("Failed to submit test results. Aborting demo.")
            return
        
        # Step 3: Get score summary
        print("\nSTEP 3: RETRIEVING SCORE SUMMARY")
        print("-" * 50)
        score_summary = self.get_score_summary()
        if not score_summary:
            print("Failed to retrieve score summary.")
            return
        
        # Step 4: Get recommendations
        print("\nSTEP 4: GETTING COURSE RECOMMENDATIONS")
        print("-" * 50)
        recommendations = self.get_recommendations()
        if not recommendations:
            print("Failed to get recommendations.")
            return
        
        # Step 5: Get learning path
        print("\nSTEP 5: GENERATING LEARNING PATH")
        print("-" * 50)
        learning_path = self.get_learning_path()
        if not learning_path:
            print("Failed to get learning path.")
            return
        
        # Step 6: Summary
        print("\nDEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("What we demonstrated:")
        print("- Submitting test/quiz results to the scoring system")
        print("- Calculating weighted scores based on test performance")
        print("- Analyzing performance trends and confidence levels")
        print("- Generating personalized course recommendations")
        print("- Creating tailored learning paths")
        print("\nKey Features:")
        print("- Weighted scoring system (exams > assignments > tests > quizzes)")
        print("- Recency-based score adjustment")
        print("- Performance trend analysis (improving/stable/declining)")
        print("- Confidence scoring based on consistency")
        print("- Subject strength/weakness identification")
        print("- Personalized difficulty matching")
        print("- Learning path generation with estimated durations")
        
    def test_single_learner_workflow(self, learner_id: str = "single-learner-demo"):
        """Test the workflow with a single learner"""
        self.learner_id = learner_id
        print(f"\nTESTING SINGLE LEARNER WORKFLOW")
        print(f"Learner ID: {learner_id}")
        print("-" * 50)
        
        # Submit a few test results
        test_data = {
            'learner_id': self.learner_id,
            'test_id': 'single_test_001',
            'test_type': 'quiz',
            'course_id': 'python-101',
            'score': 85,
            'max_score': 100,
            'time_taken': 25,
            'attempts': 1
        }
        
        print("Submitting quiz result...")
        if self.submit_test_result(test_data):
            print("Getting score summary...")
            self.get_score_summary()
            print("Getting recommendations...")
            self.get_recommendations()

def main():
    """Main function to run the API demo"""
    print("Learning Agent Scoring & Recommendation API Demo")
    print("=" * 60)
    
    demo = ScoringAPIDemo()
    
    # Check if user wants to run the full demo or a quick test
    print("\nChoose demo mode:")
    print("1. Full workflow demo (recommended)")
    print("2. Quick single learner test")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo.run_complete_workflow_demo()
        elif choice == "2":
            learner_id = input("Enter learner ID (or press Enter for default): ").strip()
            if not learner_id:
                learner_id = "quick-test-learner"
            demo.test_single_learner_workflow(learner_id)
        elif choice == "3":
            print("Goodbye! 👋")
            return
        else:
            print("Invalid choice. Running full demo...")
            demo.run_complete_workflow_demo()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()