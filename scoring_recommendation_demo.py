#!/usr/bin/env python3
"""
Comprehensive Scoring and Recommendation System Demo
==================================================

This script demonstrates a complete scoring and recommendation system that:
1. Calculates learner scores based on test marks and quiz marks
2. Provides performance analysis and insights
3. Recommends personalized courses based on scoring results
4. Generates learning paths for continued education

Usage:
    python scoring_recommendation_demo.py
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our scoring and recommendation modules
from models.test_result import TestResult, LearnerScoreSummary
from ml.scoring_engine import ScoringEngine, get_learner_score_summary
from ml.score_based_recommender import ScoreBasedRecommender

class ScoringRecommendationDemo:
    """Demo class for scoring and recommendation system"""
    
    def __init__(self):
        self.scoring_engine = ScoringEngine()
        self.recommender = ScoreBasedRecommender()
        
        # Sample course database
        self.courses = self._load_sample_courses()
        
    def _load_sample_courses(self) -> List[Dict[str, Any]]:
        """Load sample course data for recommendations"""
        return [
            {
                'id': 'python-101',
                'title': 'Python Programming Fundamentals',
                'description': 'Learn the basics of Python programming including variables, loops, functions, and data structures.',
                'difficulty_level': 'beginner',
                'content_type': 'video',
                'tags': ['python', 'programming', 'basics'],
                'estimated_duration': 120,
                'course_id': 'programming-fundamentals'
            },
            {
                'id': 'python-201',
                'title': 'Advanced Python Programming',
                'description': 'Master advanced Python concepts including OOP, decorators, generators, and best practices.',
                'difficulty_level': 'intermediate',
                'content_type': 'video',
                'tags': ['python', 'advanced-programming', 'oop'],
                'estimated_duration': 180,
                'course_id': 'advanced-programming'
            },
            {
                'id': 'data-science-101',
                'title': 'Introduction to Data Science',
                'description': 'Learn data science fundamentals including data analysis, visualization, and statistical concepts.',
                'difficulty_level': 'beginner',
                'content_type': 'article',
                'tags': ['data-science', 'statistics', 'analysis'],
                'estimated_duration': 150,
                'course_id': 'data-science-intro'
            },
            {
                'id': 'data-science-201',
                'title': 'Machine Learning with Python',
                'description': 'Build machine learning models using scikit-learn, pandas, and numpy.',
                'difficulty_level': 'intermediate',
                'content_type': 'video',
                'tags': ['machine-learning', 'python', 'scikit-learn'],
                'estimated_duration': 240,
                'course_id': 'machine-learning'
            },
            {
                'id': 'web-dev-101',
                'title': 'Web Development with HTML/CSS',
                'description': 'Learn the fundamentals of web development with HTML, CSS, and responsive design.',
                'difficulty_level': 'beginner',
                'content_type': 'video',
                'tags': ['html', 'css', 'web-development'],
                'estimated_duration': 200,
                'course_id': 'web-development'
            },
            {
                'id': 'web-dev-201',
                'title': 'JavaScript and React Development',
                'description': 'Master modern JavaScript and React for building interactive web applications.',
                'difficulty_level': 'intermediate',
                'content_type': 'video',
                'tags': ['javascript', 'react', 'frontend'],
                'estimated_duration': 300,
                'course_id': 'javascript-development'
            },
            {
                'id': 'algorithm-101',
                'title': 'Data Structures and Algorithms',
                'description': 'Learn fundamental data structures and algorithms for technical interviews.',
                'difficulty_level': 'advanced',
                'content_type': 'video',
                'tags': ['algorithms', 'data-structures', 'programming'],
                'estimated_duration': 400,
                'course_id': 'algorithms'
            },
            {
                'id': 'database-101',
                'title': 'Database Design and SQL',
                'description': 'Learn database design principles and SQL for managing relational databases.',
                'difficulty_level': 'intermediate',
                'content_type': 'article',
                'tags': ['sql', 'database', 'data-management'],
                'estimated_duration': 160,
                'course_id': 'database-fundamentals'
            }
        ]
    
    def generate_sample_test_results(self, learner_id: str, num_tests: int = 8) -> List[TestResult]:
        """Generate realistic sample test results for demonstration"""
        test_types = ['quiz', 'test', 'assignment', 'exam']
        course_ids = ['programming-fundamentals', 'data-science-intro', 'web-development', 'algorithms']
        
        test_results = []
        base_date = datetime.now() - timedelta(days=60)  # Start 60 days ago
        
        for i in range(num_tests):
            # Create realistic score progression
            base_score = 70 + (i * 2) + random.randint(-10, 15)  # Generally improving with variation
            base_score = max(40, min(95, base_score))  # Clamp between 40-95
            
            test_type = random.choice(test_types)
            course_id = random.choice(course_ids)
            
            # Exams are generally harder, quizzes are easier
            if test_type == 'exam':
                score = base_score - random.randint(5, 15)
            elif test_type == 'quiz':
                score = base_score + random.randint(0, 10)
            else:
                score = base_score
                
            score = max(30, min(100, score))  # Final clamp
            
            test_result = TestResult(
                learner_id=learner_id,
                test_id=f"test_{i+1:03d}",
                test_type=test_type,
                course_id=course_id,
                score=score,
                max_score=100.0,
                time_taken=random.randint(15, 90),
                attempts=random.randint(1, 3),
                completed_at=base_date + timedelta(days=i * 7)  # Weekly tests
            )
            
            test_results.append(test_result)
        
        return sorted(test_results, key=lambda x: x.completed_at)
    
    def display_learner_performance(self, learner_id: str, test_results: List[TestResult]):
        """Display detailed learner performance analysis"""
        print(f"\n{'='*80}")
        print(f"LEARNER PERFORMANCE ANALYSIS")
        print(f"{'='*80}")
        print(f"Learner ID: {learner_id}")
        print(f"Total Tests: {len(test_results)}")
        
        if not test_results:
            print("No test results found.")
            return
        
        # Generate score summary
        score_summary = get_learner_score_summary(learner_id, test_results)
        
        # Display test results table
        print(f"\nTEST RESULTS:")
        print(f"{'Test ID':<12} {'Type':<10} {'Course':<25} {'Score':<8} {'%':<6} {'Date':<12}")
        print(f"{'-'*12} {'-'*10} {'-'*25} {'-'*8} {'-'*6} {'-'*12}")
        
        for test in test_results:
            print(f"{test.test_id:<12} {test.test_type:<10} {test.course_id[:24]:<25} "
                  f"{test.score:<8.1f} {test.percentage:<6.1f} {test.completed_at.strftime('%Y-%m-%d'):<12}")
        
        # Display performance metrics
        print(f"\nPERFORMANCE SUMMARY:")
        print(f"Average Score: {score_summary.average_score:.1f}%")
        print(f"Latest Score: {score_summary.latest_score:.1f}%")
        print(f"Score Trend: {score_summary.score_trend.title()}")
        print(f"Confidence Score: {score_summary.confidence_score:.1f}/100")
        print(f"Recommendation Level: {score_summary.recommendation_level.title()}")
        print(f"Strongest Subject: {score_summary.strongest_subject}")
        print(f"Weakest Subject: {score_summary.weakest_subject}")
        
        return score_summary
    
    def get_course_recommendations(self, score_summary: LearnerScoreSummary, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get course recommendations based on scoring analysis"""
        print(f"\n{'='*80}")
        print(f"PERSONALIZED COURSE RECOMMENDATIONS")
        print(f"{'='*80}")
        
        # Calculate match scores for all courses
        recommendations = []
        for course in self.courses:
            match_analysis = self.recommender.calculate_course_match_score(course, score_summary)
            
            recommendation = {
                'rank': 0,  # Will be set after sorting
                'course': course,
                'match_score': match_analysis['total_score'],
                'confidence': match_analysis['confidence'],
                'reason': match_analysis['recommendation_reason'],
                'score_breakdown': match_analysis['score_breakdown']
            }
            recommendations.append(recommendation)
        
        # Sort by match score and set ranks
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        for i, rec in enumerate(recommendations[:top_n]):
            rec['rank'] = i + 1
        
        # Display recommendations
        for rec in recommendations[:top_n]:
            course = rec['course']
            print(f"\n{rec['rank']}. {course['title']}")
            print(f"   Course ID: {course['id']}")
            print(f"   Difficulty: {course['difficulty_level'].title()}")
            print(f"   Content Type: {course['content_type'].title()}")
            print(f"   Duration: {course['estimated_duration']} minutes")
            print(f"   Tags: {', '.join(course['tags'])}")
            print(f"   Match Score: {rec['match_score']:.1f}/100")
            print(f"   Confidence: {rec['confidence']:.1f}%")
            print(f"   Reason: {rec['reason']}")
            
            # Estimate completion time based on performance
            estimated_time = self.recommender._estimate_completion_time(course, score_summary)
            print(f"   Estimated Completion: {estimated_time}")
        
        return recommendations
    
    def generate_learning_path(self, score_summary: LearnerScoreSummary) -> Dict[str, Any]:
        """Generate a complete learning path"""
        print(f"\n{'='*80}")
        print(f"PERSONALIZED LEARNING PATH")
        print(f"{'='*80}")
        
        recommendations = self.get_course_recommendations(score_summary, top_n=6)
        
        if not recommendations:
            print("No suitable courses found for your current level.")
            return {}
        
        # Create learning path
        learning_path = []
        total_duration = 0
        
        for i, rec in enumerate(recommendations[:6]):
            course = rec['course']
            duration = course['estimated_duration']
            total_duration += duration
            
            path_item = {
                'sequence': i + 1,
                'course_id': course['id'],
                'title': course['title'],
                'difficulty': course['difficulty_level'],
                'duration_minutes': duration,
                'match_confidence': rec['confidence']
            }
            learning_path.append(path_item)
        
        # Display learning path
        print(f"\nRECOMMENDED LEARNING SEQUENCE:")
        for item in learning_path:
            print(f"{item['sequence']}. {item['title']}")
            print(f"   Difficulty: {item['difficulty'].title()}")
            print(f"   Duration: {item['duration_minutes']} minutes")
            print(f"   Match Confidence: {item['match_confidence']:.1f}%")
            print()
        
        # Learning path summary
        total_hours = total_duration / 60
        print(f"Learning Path Summary:")
        print(f"- Total Courses: {len(learning_path)}")
        print(f"- Estimated Duration: {total_hours:.1f} hours")
        print(f"- Starting Level: {score_summary.recommendation_level.title()}")
        print(f"- Expected Outcome: {self.recommender._generate_learning_outcome(score_summary)}")
        
        return {
            'learning_path': learning_path,
            'total_duration_hours': total_hours,
            'starting_level': score_summary.recommendation_level,
            'expected_outcome': self.recommender._generate_learning_outcome(score_summary)
        }
    
    def run_full_demo(self, learner_id: str = "demo-learner-001"):
        """Run the complete scoring and recommendation demo"""
        print("LEARNING AGENT - SCORING & RECOMMENDATION SYSTEM DEMO")
        print("=" * 80)
        
        # Step 1: Generate sample test results
        print("\nSTEP 1: GENERATING SAMPLE TEST RESULTS")
        print("-" * 50)
        test_results = self.generate_sample_test_results(learner_id)
        print(f"Generated {len(test_results)} sample test results for learner {learner_id}")
        
        # Step 2: Analyze learner performance
        print("\nSTEP 2: ANALYZING LEARNER PERFORMANCE")
        print("-" * 50)
        score_summary = self.display_learner_performance(learner_id, test_results)
        
        # Step 3: Get course recommendations
        print("\nSTEP 3: GENERATING COURSE RECOMMENDATIONS")
        print("-" * 50)
        recommendations = self.get_course_recommendations(score_summary)
        
        # Step 4: Generate learning path
        print("\nSTEP 4: CREATING LEARNING PATH")
        print("-" * 50)
        learning_path = self.generate_learning_path(score_summary)
        
        # Step 5: Export results
        print("\nSTEP 5: EXPORTING RESULTS")
        print("-" * 50)
        export_data = {
            'learner_id': learner_id,
            'test_results': [tr.to_dict() for tr in test_results],
            'score_summary': score_summary.to_dict(),
            'recommendations': recommendations[:5],
            'learning_path': learning_path,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(f'scoring_results_{learner_id}.json', 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Results exported to: scoring_results_{learner_id}.json")
        print(f"\nDEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return export_data

def main():
    """Main demo function"""
    demo = ScoringRecommendationDemo()
    
    print("Welcome to the Learning Agent Scoring & Recommendation System!")
    print("\nThis demo will show you:")
    print("1. How test and quiz marks are converted into performance scores")
    print("2. How performance analysis identifies strengths and weaknesses")
    print("3. How personalized course recommendations are generated")
    print("4. How learning paths are created based on your performance")
    
    # Run demo with a sample learner
    learner_id = "demo-learner-alice"
    demo.run_full_demo(learner_id)
    
    print(f"\nTo run the demo with different learners, modify the learner_id in the script.")
    print(f"To integrate with your system, use the ScoringEngine and ScoreBasedRecommender classes.")

if __name__ == "__main__":
    main()