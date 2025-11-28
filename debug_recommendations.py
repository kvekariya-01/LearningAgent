#!/usr/bin/env python3
"""
Debug script to understand why no recommendations are generated
"""

import sys
import os
sys.path.append('.')

def debug_recommendation_process():
    """Debug the recommendation generation process"""
    try:
        print("Debugging Score-Based Recommendation Process")
        print("=" * 55)
        
        # Import the required modules
        from ml.score_based_recommender import ScoreBasedRecommender
        from ml.scoring_engine import get_learner_score_summary
        from models.test_result import TestResult
        from datetime import datetime
        from utils.crud_operations import read_contents
        
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
        
        print(f"[DEBUG] Mock courses available: {len(mock_courses)}")
        for i, course in enumerate(mock_courses):
            print(f"  {i+1}. {course['title']} ({course['difficulty_level']})")
        
        # Monkey patch read_contents
        import utils.crud_operations
        original_read_contents = utils.crud_operations.read_contents
        utils.crud_operations.read_contents = lambda: mock_courses
        
        try:
            # Create test data
            test_learner_id = "test-learner-123"
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
                )
            ]
            
            # Generate score summary
            score_summary = get_learner_score_summary(test_learner_id, test_results)
            print(f"\n[DEBUG] Score Summary:")
            print(f"  Recommendation level: {score_summary.recommendation_level}")
            print(f"  Average score: {score_summary.average_score:.1f}%")
            print(f"  Confidence: {score_summary.confidence_score:.1f}")
            print(f"  Strongest subject: {score_summary.strongest_subject}")
            
            # Test the recommender step by step
            recommender = ScoreBasedRecommender()
            
            # Step 1: Check if courses are retrieved
            all_courses = read_contents()
            print(f"\n[DEBUG] Retrieved courses: {len(all_courses) if all_courses else 0}")
            
            # Step 2: Check course matching logic
            print(f"\n[DEBUG] Testing course matching for each course:")
            scored_courses = []
            for course in all_courses:
                match_analysis = recommender.calculate_course_match_score(course, score_summary)
                total_score = match_analysis['total_score']
                print(f"  Course: {course['title']}")
                print(f"    Total score: {total_score}")
                print(f"    Difficulty: {course.get('difficulty_level', 'N/A')}")
                print(f"    Recommendation level: {score_summary.recommendation_level}")
                
                if total_score > 0:
                    scored_courses.append({
                        'course': course,
                        'match_score': match_analysis['total_score'],
                        'confidence': match_analysis['confidence'],
                        'reason': match_analysis['recommendation_reason']
                    })
                    print(f"    -> ADDED to recommendations")
                else:
                    print(f"    -> SKIPPED (score = 0)")
            
            print(f"\n[DEBUG] Courses with scores > 0: {len(scored_courses)}")
            
            if scored_courses:
                # Sort and get top recommendations
                scored_courses.sort(key=lambda x: x['match_score'], reverse=True)
                recommendations = []
                top_n = 3
                
                for i, course_data in enumerate(scored_courses[:top_n]):
                    recommendation = {
                        'rank': i + 1,
                        'course': course_data['course'],  # This is the fix we made
                        'course_id': course_data['course']['id'],
                        'title': course_data['course']['title'],
                        'description': course_data['course']['description'],
                        'difficulty_level': course_data['course'].get('difficulty_level', 'intermediate'),
                        'content_type': course_data['course'].get('content_type', 'video'),
                        'tags': course_data['course'].get('tags', []),
                        'match_score': course_data['match_score'],
                        'confidence': course_data['confidence'],
                        'recommendation_reason': course_data['reason']
                    }
                    recommendations.append(recommendation)
                
                print(f"\n[DEBUG] Final recommendations generated: {len(recommendations)}")
                
                # Test the structure fix
                if recommendations:
                    first_rec = recommendations[0]
                    if 'course' in first_rec:
                        print(f"[SUCCESS] 'course' key found in recommendation!")
                        print(f"  Course title: {first_rec['course']['title']}")
                        return True
                    else:
                        print(f"[FAIL] 'course' key still missing")
                        print(f"  Keys: {list(first_rec.keys())}")
                        return False
            else:
                print(f"\n[DEBUG] No courses received scores > 0")
                print(f"This explains why no recommendations were generated")
                
                # Let's check the scoring logic
                course = all_courses[0]  # Test with first course
                print(f"\n[DEBUG] Detailed scoring for '{course['title']}':")
                match_analysis = recommender.calculate_course_match_score(course, score_summary)
                
                for key, value in match_analysis['score_breakdown'].items():
                    print(f"  {key}: {value}")
                print(f"  Total: {match_analysis['total_score']}")
                
                return False
            
        finally:
            utils.crud_operations.read_contents = original_read_contents
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_recommendation_process()