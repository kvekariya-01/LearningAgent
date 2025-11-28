#!/usr/bin/env python3
"""
Test script for the scoring and recommendation system
Demonstrates how to submit test results and get score-based recommendations
"""

import requests
import json
import time
from datetime import datetime, timezone
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_scoring_system():
    """Test the complete scoring and recommendation system"""
    
    API_BASE = "http://localhost:5000/api"
    
    print("Testing Scoring and Recommendation System")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🔍 Testing API Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ API is healthy")
            print(f"   📊 Database connected: {health_data['database_connected']}")
            print(f"   🎯 Scoring enabled: {health_data['scoring_enabled']}")
            print(f"   🔧 Features: {health_data['features']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: Submit Sample Test Results
    print("\n2. 📝 Submitting Sample Test Results...")
    
    # Sample test results with different scores and types
    test_results = [
        {
            "learner_id": "demo-alice-123",
            "test_id": "python_quiz_1",
            "test_type": "quiz",
            "course_id": "python-101",
            "score": 85,
            "max_score": 100,
            "time_taken": 25,
            "attempts": 1,
            "feedback": "Good understanding of Python basics"
        },
        {
            "learner_id": "demo-alice-123",
            "test_id": "python_test_1",
            "test_type": "test",
            "course_id": "python-101",
            "score": 78,
            "max_score": 100,
            "time_taken": 45,
            "attempts": 1,
            "feedback": "Solid performance on core concepts"
        },
        {
            "learner_id": "demo-alice-123",
            "test_id": "data_science_assignment",
            "test_type": "assignment",
            "course_id": "data-science-intro",
            "score": 92,
            "max_score": 100,
            "time_taken": 120,
            "attempts": 1,
            "feedback": "Excellent analysis and insights"
        },
        {
            "learner_id": "demo-bob-456",
            "test_id": "javascript_quiz_1",
            "test_type": "quiz",
            "course_id": "web-dev-js",
            "score": 65,
            "max_score": 100,
            "time_taken": 30,
            "attempts": 2,
            "feedback": "Needs more practice with async concepts"
        },
        {
            "learner_id": "demo-bob-456",
            "test_id": "react_assignment",
            "test_type": "assignment",
            "course_id": "react-basics",
            "score": 88,
            "max_score": 100,
            "time_taken": 90,
            "attempts": 1,
            "feedback": "Great component structure and state management"
        }
    ]
    
    submitted_count = 0
    for test_data in test_results:
        try:
            response = requests.post(
                f"{API_BASE}/scoring/test-result",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ {test_data['test_type'].title()} submitted: {result['test_result']['percentage']:.1f}%")
                submitted_count += 1
            else:
                print(f"   ❌ Failed to submit {test_data['test_type']}: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error submitting {test_data['test_type']}: {e}")
    
    print(f"   📊 Successfully submitted {submitted_count}/{len(test_results)} test results")
    
    # Test 3: Get Score Summary
    print("\n3. 📈 Getting Score Summary...")
    
    learner_ids = ["demo-alice-123", "demo-bob-456"]
    for learner_id in learner_ids:
        try:
            response = requests.get(f"{API_BASE}/scoring/learner/{learner_id}/score-summary")
            
            if response.status_code == 200:
                data = response.json()
                summary = data['score_summary']
                print(f"   📋 Learner: {learner_id}")
                print(f"      🎯 Total Tests: {summary['total_tests']}")
                print(f"      📊 Average Score: {summary['average_score']:.1f}%")
                print(f"      📈 Latest Score: {summary['latest_score']:.1f}%")
                print(f"      📉 Trend: {summary['score_trend']}")
                print(f"      💪 Confidence: {summary['confidence_score']:.1f}%")
                print(f"      🎓 Level: {summary['recommendation_level']}")
                print(f"      💪 Strongest: {summary['strongest_subject']}")
                print(f"      ⚠️  Weakest: {summary['weakest_subject']}")
            else:
                print(f"   ❌ Failed to get summary for {learner_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error getting summary for {learner_id}: {e}")
    
    # Test 4: Get Score-Based Recommendations
    print("\n4. 🎯 Getting Score-Based Recommendations...")
    
    for learner_id in learner_ids:
        try:
            response = requests.get(f"{API_BASE}/scoring/learner/{learner_id}/recommendations")
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data['recommendations']
                
                print(f"   🎯 Recommendations for {learner_id}:")
                print(f"      📊 Score Summary: {data['recommendations']['score_summary']['recommendation_level']} level")
                
                for i, rec in enumerate(recommendations['recommendations'][:3], 1):
                    print(f"      {i}. {rec['title']}")
                    print(f"         📚 Difficulty: {rec['difficulty_level']}")
                    print(f"         🎯 Match Score: {rec['match_score']:.1f}")
                    print(f"         💡 Reason: {rec['recommendation_reason']}")
                print()
            else:
                print(f"   ❌ Failed to get recommendations for {learner_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error getting recommendations for {learner_id}: {e}")
    
    # Test 5: Get Learning Paths
    print("\n5. 🛤️  Getting Personalized Learning Paths...")
    
    for learner_id in learner_ids:
        try:
            response = requests.get(f"{API_BASE}/scoring/learner/{learner_id}/learning-path")
            
            if response.status_code == 200:
                data = response.json()
                learning_path = data['learning_path']
                
                print(f"   🛤️  Learning Path for {learner_id}:")
                print(f"      📝 Summary: {learning_path['path_summary']}")
                print(f"      ⏱️  Duration: {learning_path['estimated_duration']}")
                print(f"      🎓 Starting Level: {learning_path['starting_level']}")
                print(f"      📚 Courses in Path: {len(learning_path['learning_path'])}")
                print(f"      🎯 Skills Covered: {len(learning_path['skill_coverage'])}")
                
                for i, course in enumerate(learning_path['learning_path'][:2], 1):
                    print(f"      {i}. {course['title']} ({course['difficulty']})")
                print()
            else:
                print(f"   ❌ Failed to get learning path for {learner_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error getting learning path for {learner_id}: {e}")
    
    # Test 6: Performance Analytics (Admin Function)
    print("\n6. 📊 Performance Analytics...")
    
    try:
        response = requests.get(f"{API_BASE}/scoring/analytics/performance-trends")
        
        if response.status_code == 200:
            data = response.json()
            analytics = data['analytics']
            
            print(f"   📊 Analytics Overview:")
            print(f"      👥 Total Learners: {analytics['total_learners']}")
            print(f"      🎯 Common Level: {analytics['most_common_recommendation_level']}")
            print(f"      📈 Trends: {analytics['performance_trends']}")
        else:
            print(f"   ❌ Failed to get analytics: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting analytics: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Scoring System Test Complete!")
    print("\n🎯 Available API Endpoints:")
    print(f"   • Submit Test Result: POST {API_BASE}/scoring/test-result")
    print(f"   • Get Score Summary: GET {API_BASE}/scoring/learner/<id>/score-summary")
    print(f"   • Get Recommendations: GET {API_BASE}/scoring/learner/<id>/recommendations")
    print(f"   • Get Learning Path: GET {API_BASE}/scoring/learner/<id>/learning-path")
    print(f"   • Performance Analytics: GET {API_BASE}/scoring/analytics/performance-trends")

def demonstrate_score_calculation():
    """Demonstrate the scoring algorithm with sample data"""
    print("\n🔢 Scoring Algorithm Demonstration")
    print("=" * 50)
    
    # Import our scoring modules
    from ml.scoring_engine import ScoringEngine
    from models.test_result import TestResult
    from datetime import datetime, timezone
    
    # Create sample test results
    engine = ScoringEngine()
    
    sample_tests = [
        TestResult(
            learner_id="demo-user",
            test_id="quiz1",
            test_type="quiz",
            course_id="python-101",
            score=85,
            max_score=100,
            time_taken=20,
            completed_at=datetime.now(timezone.utc)
        ),
        TestResult(
            learner_id="demo-user",
            test_id="test1",
            test_type="test",
            course_id="python-101", 
            score=78,
            max_score=100,
            time_taken=45,
            completed_at=datetime.now(timezone.utc)
        ),
        TestResult(
            learner_id="demo-user",
            test_id="assignment1",
            test_type="assignment",
            course_id="data-science-intro",
            score=92,
            max_score=100,
            time_taken=120,
            completed_at=datetime.now(timezone.utc)
        )
    ]
    
    print("📝 Sample Test Results:")
    for test in sample_tests:
        print(f"   • {test.test_type.title()}: {test.percentage:.1f}% (Weight: {engine.weight_config[test.test_type]})")
    
    # Calculate metrics
    weighted_score = engine.calculate_weighted_score(sample_tests)
    trend = engine.calculate_score_trend(sample_tests)
    confidence = engine.calculate_confidence_score(sample_tests)
    level = engine.determine_recommendation_level(weighted_score, confidence, trend)
    
    print(f"\n📊 Calculated Metrics:")
    print(f"   🎯 Weighted Score: {weighted_score:.1f}%")
    print(f"   📈 Trend: {trend}")
    print(f"   💪 Confidence: {confidence:.1f}%")
    print(f"   🎓 Recommendation Level: {level}")

if __name__ == "__main__":
    print("Starting Scoring System Tests...")
    print(f"Test Started: {datetime.now().isoformat()}")
    
    # First demonstrate the scoring algorithm
    demonstrate_score_calculation()
    
    # Then test the full API system
    test_scoring_system()
    
    print(f"\n🏁 Testing Complete: {datetime.now().isoformat()}")