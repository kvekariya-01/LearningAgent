#!/usr/bin/env python3
"""
Test script to verify the score-based recommendation fix
"""

import sys
import os
sys.path.append('.')

def test_score_based_recommender():
    """Test the fixed score-based recommender"""
    try:
        print("Testing Fixed Score-Based Recommender")
        print("=" * 50)
        
        # Import the required modules
        from ml.score_based_recommender import ScoreBasedRecommender
        from ml.scoring_engine import get_learner_score_summary
        from models.test_result import TestResult
        from datetime import datetime
        
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
        
        # Test the recommender
        recommender = ScoreBasedRecommender()
        recommendations = recommender.get_personalized_recommendations(test_learner_id, score_summary, top_n=3)
        
        if not recommendations:
            print("[WARNING] No recommendations generated")
            return False
        
        print(f"[OK] Generated {len(recommendations)} recommendations")
        
        # Check the structure of the first recommendation
        if recommendations:
            first_rec = recommendations[0]
            print(f"[OK] First recommendation structure:")
            
            # Check if 'course' key exists (this was the bug)
            if 'course' in first_rec:
                print("[OK] 'course' key found in recommendation")
                course = first_rec['course']
                print(f"   Course title: {course.get('title', 'N/A')}")
                print(f"   Course ID: {course.get('id', 'N/A')}")
                print(f"   Difficulty: {course.get('difficulty_level', 'N/A')}")
            else:
                print("[FAIL] 'course' key missing from recommendation")
                print(f"   Available keys: {list(first_rec.keys())}")
                return False
            
            # Check other expected fields
            expected_fields = ['rank', 'course_id', 'title', 'description', 'match_score', 'confidence', 'recommendation_reason']
            for field in expected_fields:
                if field in first_rec:
                    print(f"[OK] {field}: {first_rec[field]}")
                else:
                    print(f"[WARNING] {field} missing from recommendation")
        
        # Test learning path generation
        print("\n[TEST] Testing learning path generation...")
        learning_path = recommender.generate_learning_path(test_learner_id, score_summary, target_skills=["programming"])
        
        if learning_path and learning_path.get('learning_path'):
            print(f"[OK] Learning path generated with {len(learning_path['learning_path'])} courses")
        else:
            print("[WARNING] No learning path generated")
        
        print("\n[SUCCESS] Score-based recommender test completed successfully!")
        return True
        
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
    print("Score-Based Recommendation Fix Test")
    print("=" * 50)
    
    success = test_score_based_recommender()
    
    if success:
        print("\n[SUCCESS] All tests passed! The 'course' error should be fixed.")
    else:
        print("\n[FAIL] Tests failed. The issue may still exist.")
    
    sys.exit(0 if success else 1)