#!/usr/bin/env python3
"""
Simple test script for the scoring and recommendation system
Demonstrates how to submit test results and get score-based recommendations
"""

import sys
import os
from datetime import datetime, timezone

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_scoring_algorithm():
    """Test the core scoring algorithm"""
    print("Testing Scoring Algorithm")
    print("=" * 30)
    
    # Import our scoring modules
    from ml.scoring_engine import ScoringEngine
    from models.test_result import TestResult
    
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
    
    print("Sample Test Results:")
    for test in sample_tests:
        weight = engine.weight_config[test.test_type]
        print(f"  - {test.test_type.title()}: {test.percentage:.1f}% (Weight: {weight})")
    
    # Calculate metrics
    weighted_score = engine.calculate_weighted_score(sample_tests)
    trend = engine.calculate_score_trend(sample_tests)
    confidence = engine.calculate_confidence_score(sample_tests)
    level = engine.determine_recommendation_level(weighted_score, confidence, trend)
    
    print(f"\nCalculated Metrics:")
    print(f"  Weighted Score: {weighted_score:.1f}%")
    print(f"  Trend: {trend}")
    print(f"  Confidence: {confidence:.1f}%")
    print(f"  Recommendation Level: {level}")
    
    return True

def test_recommendation_system():
    """Test the recommendation system"""
    print("\nTesting Recommendation System")
    print("=" * 35)
    
    # Import recommendation modules
    from ml.score_based_recommender import ScoreBasedRecommender
    from ml.scoring_engine import get_learner_score_summary
    from models.test_result import TestResult
    
    # Create sample score summary
    sample_tests = [
        TestResult(
            learner_id="demo-user",
            test_id="quiz1",
            test_type="quiz",
            course_id="python-101",
            score=85,
            max_score=100
        ),
        TestResult(
            learner_id="demo-user",
            test_id="test1",
            test_type="test",
            course_id="python-101", 
            score=78,
            max_score=100
        )
    ]
    
    score_summary = get_learner_score_summary("demo-user", sample_tests)
    print(f"Score Summary Generated:")
    print(f"  Total Tests: {score_summary.total_tests}")
    print(f"  Average Score: {score_summary.average_score:.1f}%")
    print(f"  Recommendation Level: {score_summary.recommendation_level}")
    print(f"  Confidence: {score_summary.confidence_score:.1f}%")
    
    # Test recommender (this will work with actual course data)
    recommender = ScoreBasedRecommender()
    print(f"Recommendation Engine Initialized")
    print(f"  Difficulty Mapping: {list(recommender.difficulty_mapping.keys())}")
    print(f"  Performance Thresholds: {list(recommender.thresholds.keys())}")
    
    return True

def test_data_models():
    """Test the data models"""
    print("\nTesting Data Models")
    print("=" * 20)
    
    from models.test_result import TestResult, LearnerScoreSummary
    
    # Test TestResult creation
    test_result = TestResult(
        learner_id="test-learner",
        test_id="test-quiz",
        test_type="quiz",
        course_id="test-course",
        score=85,
        max_score=100,
        time_taken=30
    )
    
    print(f"TestResult Created:")
    print(f"  ID: {test_result.id}")
    print(f"  Score: {test_result.score}/{test_result.max_score}")
    print(f"  Percentage: {test_result.percentage:.1f}%")
    print(f"  Passed: {test_result.passed}")
    
    # Test LearnerScoreSummary creation
    score_summary = LearnerScoreSummary(
        learner_id="test-learner",
        total_tests=1,
        average_score=85.0,
        latest_score=85.0,
        score_trend="stable",
        strongest_subject="test-course",
        weakest_subject="test-course",
        recommendation_level="beginner",
        confidence_score=75.0
    )
    
    print(f"\nLearnerScoreSummary Created:")
    print(f"  Learner ID: {score_summary.learner_id}")
    print(f"  Total Tests: {score_summary.total_tests}")
    print(f"  Recommendation Level: {score_summary.recommendation_level}")
    
    return True

def test_api_structure():
    """Test API route structure (without starting server)"""
    print("\nTesting API Structure")
    print("=" * 22)
    
    # Test that routes can be imported
    try:
        from routes.scoring_routes import scoring_bp
        print("Scoring routes blueprint imported successfully")
        print(f"  Blueprint name: {scoring_bp.name}")
        print(f"  URL prefix: {scoring_bp.url_prefix}")
    except Exception as e:
        print(f"Error importing scoring routes: {e}")
        return False
    
    # Test Flask app integration
    try:
        from flask_api import app
        print("Flask app imported successfully")
        
        # Check if scoring blueprint is registered
        registered_blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"  Registered blueprints: {registered_blueprints}")
        
        if 'scoring' in registered_blueprints:
            print("  Scoring blueprint is registered")
        else:
            print("  WARNING: Scoring blueprint not found in registered blueprints")
            
    except Exception as e:
        print(f"Error importing Flask app: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print(f"Starting Scoring System Tests at {datetime.now().isoformat()}")
    print("=" * 60)
    
    tests = [
        ("Scoring Algorithm", test_scoring_algorithm),
        ("Recommendation System", test_recommendation_system),
        ("Data Models", test_data_models),
        ("API Structure", test_api_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} Test...")
        try:
            if test_func():
                print(f"PASSED: {test_name}")
                passed += 1
            else:
                print(f"FAILED: {test_name}")
                failed += 1
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! The scoring system is ready to use.")
        print("\nTo start the API server, run:")
        print("  python flask_api.py")
        print("\nThen test with:")
        print("  python test_scoring_system_simple.py")
    else:
        print("Some tests failed. Please check the errors above.")
    
    print(f"\nTest completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()