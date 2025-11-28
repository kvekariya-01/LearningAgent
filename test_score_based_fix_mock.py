#!/usr/bin/env python3
"""
Test script to verify the score-based recommendation fix with mock data
"""

import sys
import os
sys.path.append('.')

def test_with_mock_data():
    """Test with mock course data"""
    try:
        print("Testing Score-Based Recommender with Mock Data")
        print("=" * 55)
        
        # Import the required modules
        from ml.score_based_recommender import ScoreBasedRecommender
        from ml.scoring_engine import get_learner_score_summary
        from models.test_result import TestResult
        from datetime import datetime
        
        # Create mock course data
        mock_courses = [
            {
                "id": "python-101",
                "title": "Introduction to Python Programming",
                "description": "Learn the basics of Python programming including variables, loops, and functions.",
                "difficulty_level": "beginner",
                "content_type": "video",
                "tags": ["python", "programming", "basics"],
                "estimated_duration": 120
            },
            {
                "id": "data-science-intro",
                "title": "Data Science Fundamentals", 
                "description": "Introduction to data science concepts, tools, and techniques.",
                "difficulty_level": "intermediate",
                "content_type": "article", 
                "tags": ["data", "science", "statistics"],
                "estimated_duration": 90
            },
            {
                "id": "machine-learning-101",
                "title": "Machine Learning Introduction",
                "description": "Basic concepts of machine learning and AI algorithms.",
                "difficulty_level": "advanced",
                "content_type": "video",
                "tags": ["machine-learning", "ai", "algorithms"],
                "estimated_duration": 150
            }
        ]
        
        # Monkey patch read_contents to return our mock data
        import utils.crud_operations
        original_read_contents = utils.crud_operations.read_contents
        utils.crud_operations.read_contents = lambda: mock_courses
        
        try:
            # Create a test learner ID
            test_learner_id = "test-learner-123"
            
            # Create some sample test results
            test_results = [
                TestResult(
                    learner_id=test_learner_id,
                    test_id="quiz_001",
                    test_type="quiz",
                    course_id="python-101",
                    content_id="quiz_content_001",
                    score=85,
                    max_score=100,
                    time_taken=30.0,
                    attempts=1,
                    completed_at=datetime.now()
                ),
                TestResult(
                    learner_id=test_learner_id,
                    test_id="test_001",
                    test_type="test",
                    course_id="python-101",
                    content_id="test_content_001",
                    score=78,
                    max_score=100,
                    time_taken=60.0,
                    attempts=1,
                    completed_at=datetime.now()
                )
            ]
            
            # Generate score summary
            score_summary = get_learner_score_summary(test_learner_id, test_results)
            print(f"[OK] Score summary generated: {score_summary.recommendation_level} level")
            print(f"     Average score: {score_summary.average_score:.1f}%")
            print(f"     Confidence: {score_summary.confidence_score:.1f}/100")
            
            # Test the recommender
            recommender = ScoreBasedRecommender()
            recommendations = recommender.get_personalized_recommendations(test_learner_id, score_summary, top_n=3)
            
            if not recommendations:
                print("[FAIL] No recommendations generated")
                return False
            
            print(f"\n[OK] Generated {len(recommendations)} recommendations")
            
            # Check the structure of each recommendation
            success = True
            for i, rec in enumerate(recommendations, 1):
                print(f"\n--- Recommendation {i} ---")
                
                # Check if 'course' key exists (this was the bug)
                if 'course' in rec:
                    print("[OK] 'course' key found in recommendation")
                    course = rec['course']
                    print(f"   Course title: {course.get('title', 'N/A')}")
                    print(f"   Course ID: {course.get('id', 'N/A')}")
                    print(f"   Difficulty: {course.get('difficulty_level', 'N/A')}")
                else:
                    print("[FAIL] 'course' key missing from recommendation")
                    print(f"   Available keys: {list(rec.keys())}")
                    success = False
                    continue
                
                # Check other expected fields
                expected_fields = ['rank', 'course_id', 'title', 'description', 'match_score', 'confidence', 'recommendation_reason']
                missing_fields = []
                for field in expected_fields:
                    if field not in rec:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"[WARNING] Missing fields: {missing_fields}")
                else:
                    print("[OK] All expected fields present")
                
                print(f"   Match score: {rec.get('match_score', 0):.1f}/100")
                print(f"   Confidence: {rec.get('confidence', 0):.1f}%")
                print(f"   Reason: {rec.get('recommendation_reason', 'N/A')[:50]}...")
            
            # Test learning path generation
            print(f"\n[TEST] Testing learning path generation...")
            learning_path = recommender.generate_learning_path(test_learner_id, score_summary, target_skills=["programming"])
            
            if learning_path and learning_path.get('learning_path'):
                print(f"[OK] Learning path generated with {len(learning_path['learning_path'])} courses")
                print(f"     Path: {learning_path.get('path_summary', 'N/A')}")
            else:
                print("[WARNING] No learning path generated")
            
            return success
            
        finally:
            # Restore original function
            utils.crud_operations.read_contents = original_read_contents
        
    except KeyError as e:
        if "'course'" in str(e):
            print(f"[FAIL] The 'course' error still exists: {e}")
            return False
        else:
            print(f"[FAIL] Unexpected KeyError: {e}")
            return False
    except Exception as e:
        print(f"[FAIL] Error testing score-based recommender: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Score-Based Recommendation Fix Test (with Mock Data)")
    print("=" * 60)
    
    success = test_with_mock_data()
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] All tests passed! The 'course' error should be fixed.")
        print("The score-based recommendations should now work properly in the Streamlit app.")
    else:
        print("\n" + "="*60)
        print("[FAIL] Tests failed. The issue may still exist.")
    
    sys.exit(0 if success else 1)