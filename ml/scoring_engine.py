"""Scoring algorithms for calculating learner performance based on test and quiz marks"""

import statistics
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from models.test_result import TestResult, LearnerScoreSummary
from utils.crud_operations import read_engagements

class ScoringEngine:
    """Core scoring engine for calculating learner performance metrics"""
    
    def __init__(self):
        self.weight_config = {
            'quiz': 0.3,      # Quizzes have lower weight
            'test': 0.4,      # Tests have medium weight
            'assignment': 0.5, # Assignments have higher weight
            'exam': 0.7       # Exams have highest weight
        }
        
        self.recency_decay_days = 30  # Scores older than 30 days get reduced weight
        
    def calculate_weighted_score(self, test_results: List[TestResult]) -> float:
        """Calculate weighted average score based on test type and recency"""
        if not test_results:
            return 0.0
            
        weighted_scores = []
        total_weight = 0
        
        for test in test_results:
            # Base weight from test type
            weight = self.weight_config.get(test.test_type, 0.4)
            
            # Apply recency decay
            now = datetime.now(timezone.utc)
            if test.completed_at.tzinfo is None:
                # If test.completed_at is naive, assume it's UTC
                test_time = test.completed_at.replace(tzinfo=timezone.utc)
            else:
                test_time = test.completed_at
            days_old = (now - test_time).days
            if days_old <= self.recency_decay_days:
                recency_factor = 1.0 - (days_old / self.recency_decay_days) * 0.3  # Max 30% decay
            else:
                recency_factor = 0.7  # Minimum weight for old scores
                
            final_weight = weight * recency_factor
            weighted_scores.append(test.percentage * final_weight)
            total_weight += final_weight
            
        if total_weight == 0:
            return 0.0
            
        return round(sum(weighted_scores) / total_weight, 2)
    
    def calculate_score_trend(self, test_results: List[TestResult], window_size: int = 5) -> str:
        """Determine score trend (improving/declining/stable)"""
        if len(test_results) < 3:
            return 'stable'
            
        # Sort by completion date
        sorted_results = sorted(test_results, key=lambda x: x.completed_at)
        
        # Compare recent performance vs earlier performance
        recent_scores = [t.percentage for t in sorted_results[-window_size:]]
        earlier_scores = [t.percentage for t in sorted_results[:-window_size]] if len(sorted_results) > window_size else []
        
        if not earlier_scores:
            return 'stable'
            
        recent_avg = statistics.mean(recent_scores)
        earlier_avg = statistics.mean(earlier_scores)
        difference = recent_avg - earlier_avg
        
        if difference > 5:
            return 'improving'
        elif difference < -5:
            return 'declining'
        else:
            return 'stable'
    
    def calculate_confidence_score(self, test_results: List[TestResult]) -> float:
        """Calculate confidence score based on performance consistency"""
        if len(test_results) < 2:
            return 50.0  # Default confidence for new learners
            
        scores = [t.percentage for t in test_results]
        
        # Calculate coefficient of variation (lower = more consistent)
        mean_score = statistics.mean(scores)
        if mean_score == 0:
            return 0.0
            
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        cv = std_dev / mean_score
        
        # Convert to confidence score (0-100)
        # Lower variation = higher confidence
        confidence = max(0, 100 - (cv * 100))
        return round(confidence, 2)
    
    def determine_recommendation_level(self, weighted_score: float, confidence: float, trend: str) -> str:
        """Determine appropriate recommendation level based on performance metrics"""
        # Adjust score based on confidence and trend
        adjusted_score = weighted_score
        
        if confidence < 50:
            adjusted_score *= 0.9  # Reduce score if inconsistent
        elif confidence > 80:
            adjusted_score *= 1.1  # Boost score if very consistent
            
        if trend == 'improving':
            adjusted_score *= 1.05  # Slight boost for improving trend
        elif trend == 'declining':
            adjusted_score *= 0.95  # Slight reduction for declining trend
            
        if adjusted_score >= 85:
            return 'advanced'
        elif adjusted_score >= 70:
            return 'intermediate'
        else:
            return 'beginner'
    
    def identify_strengths_weaknesses(self, test_results: List[TestResult]) -> Tuple[str, str]:
        """Identify strongest and weakest subjects based on performance"""
        if not test_results:
            return 'General Studies', 'General Studies'
            
        # Group by course_id for subject analysis
        course_scores = {}
        for test in test_results:
            if test.course_id not in course_scores:
                course_scores[test.course_id] = []
            course_scores[test.course_id].append(test.percentage)
            
        if len(course_scores) < 2:
            return 'General Studies', 'General Studies'
            
        # Calculate average scores per subject
        subject_averages = {
            course: statistics.mean(scores) 
            for course, scores in course_scores.items()
        }
        
        # Find strongest and weakest
        strongest = max(subject_averages.items(), key=lambda x: x[1])
        weakest = min(subject_averages.items(), key=lambda x: x[1])
        
        return strongest[0], weakest[0]

def get_learner_score_summary(learner_id: str, test_results: List[TestResult] = None) -> LearnerScoreSummary:
    """Generate comprehensive score summary for a learner"""
    
    if test_results is None:
        # Fetch test results from database (placeholder - implement based on your data storage)
        test_results = []
    
    if not test_results:
        # Return default summary for new learners
        return LearnerScoreSummary(
            learner_id=learner_id,
            total_tests=0,
            average_score=0.0,
            latest_score=0.0,
            score_trend='stable',
            strongest_subject='General Studies',
            weakest_subject='General Studies',
            recommendation_level='beginner',
            confidence_score=50.0,
            recent_performance=[]
        )
    
    # Initialize scoring engine
    engine = ScoringEngine()
    
    # Calculate metrics
    weighted_score = engine.calculate_weighted_score(test_results)
    latest_score = test_results[-1].percentage if test_results else 0.0
    trend = engine.calculate_score_trend(test_results)
    confidence = engine.calculate_confidence_score(test_results)
    recommendation_level = engine.determine_recommendation_level(weighted_score, confidence, trend)
    strongest, weakest = engine.identify_strengths_weaknesses(test_results)
    
    # Get recent performance (last 5 tests)
    recent_performance = sorted(test_results, key=lambda x: x.completed_at, reverse=True)[:5]
    
    return LearnerScoreSummary(
        learner_id=learner_id,
        total_tests=len(test_results),
        average_score=round(statistics.mean([t.percentage for t in test_results]), 2),
        latest_score=latest_score,
        score_trend=trend,
        strongest_subject=strongest,
        weakest_subject=weakest,
        recommendation_level=recommendation_level,
        confidence_score=confidence,
        recent_performance=recent_performance
    )