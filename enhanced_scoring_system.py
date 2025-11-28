#!/usr/bin/env python3
"""
Enhanced Scoring System for Learning Agent
Calculates comprehensive learner scores based on test marks, quiz marks, and learning analytics
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import math

class EnhancedScoringSystem:
    """Advanced scoring system for comprehensive learner assessment"""
    
    def __init__(self):
        self.weight_config = {
            'test_score': 0.4,      # 40% weight for tests
            'quiz_score': 0.3,      # 30% weight for quizzes  
            'engagement_score': 0.2, # 20% weight for engagement
            'consistency_score': 0.1  # 10% weight for consistency
        }
        
        self.performance_thresholds = {
            'excellent': 90,
            'very_good': 80,
            'good': 70,
            'average': 60,
            'below_average': 50,
            'needs_improvement': 40
        }
        
        self.difficulty_multipliers = {
            'beginner': 1.0,
            'intermediate': 1.2,
            'advanced': 1.5,
            'expert': 1.8
        }
    
    def calculate_learner_score(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive learner score based on all activities"""
        try:
            learner_id = learner_data.get('id')
            activities = learner_data.get('activities', [])
            
            if not activities:
                return self._get_new_learner_score()
            
            # Calculate component scores
            test_score = self._calculate_test_score(activities)
            quiz_score = self._calculate_quiz_score(activities)
            engagement_score = self._calculate_engagement_score(activities, learner_data)
            consistency_score = self._calculate_consistency_score(activities)
            
            # Calculate weighted final score
            final_score = (
                test_score * self.weight_config['test_score'] +
                quiz_score * self.weight_config['quiz_score'] +
                engagement_score * self.weight_config['engagement_score'] +
                consistency_score * self.weight_config['consistency_score']
            )
            
            # Determine performance level
            performance_level = self._get_performance_level(final_score)
            
            # Generate insights
            insights = self._generate_score_insights(
                test_score, quiz_score, engagement_score, consistency_score, final_score
            )
            
            return {
                'learner_id': learner_id,
                'overall_score': round(final_score, 2),
                'performance_level': performance_level,
                'component_scores': {
                    'test_score': round(test_score, 2),
                    'quiz_score': round(quiz_score, 2),
                    'engagement_score': round(engagement_score, 2),
                    'consistency_score': round(consistency_score, 2)
                },
                'weighting_used': self.weight_config,
                'insights': insights,
                'recommendations': self._generate_score_based_recommendations(final_score, performance_level),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Scoring calculation failed: {str(e)}'}
    
    def _calculate_test_score(self, activities: List[Dict]) -> float:
        """Calculate weighted test score"""
        test_activities = [a for a in activities 
                          if a.get('activity_type') in ['test_completed', 'exam_taken', 'assessment_completed']]
        
        if not test_activities:
            return 75.0  # Default neutral score
        
        # Get test scores with difficulty consideration
        test_scores = []
        for activity in test_activities:
            score = activity.get('score', 0)
            difficulty = activity.get('difficulty', 'intermediate')
            
            # Apply difficulty multiplier
            adjusted_score = min(score * self.difficulty_multipliers.get(difficulty, 1.0), 100)
            test_scores.append(adjusted_score)
        
        # Use weighted average (recent tests have higher weight)
        if len(test_scores) > 1:
            weights = [0.3 + (i * 0.2) for i in range(len(test_scores))]  # Recent tests get more weight
            weights.reverse()  # Most recent first
            weighted_sum = sum(score * weight for score, weight in zip(test_scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return test_scores[0] if test_scores else 75.0
    
    def _calculate_quiz_score(self, activities: List[Dict]) -> float:
        """Calculate weighted quiz score"""
        quiz_activities = [a for a in activities 
                          if a.get('activity_type') in ['quiz_completed', 'quiz_taken', 'quick_assessment']]
        
        if not quiz_activities:
            return 75.0  # Default neutral score
        
        quiz_scores = []
        for activity in quiz_activities:
            score = activity.get('score', 0)
            # Quizzes are typically easier, so apply less multiplier
            adjusted_score = min(score * 0.95, 100)
            quiz_scores.append(adjusted_score)
        
        # Simple average for quizzes
        return statistics.mean(quiz_scores) if quiz_scores else 75.0
    
    def _calculate_engagement_score(self, activities: List[Dict], learner_data: Dict) -> float:
        """Calculate engagement score based on activity frequency and duration"""
        if not activities:
            return 0.0
        
        # Activity frequency score
        recent_activities = self._get_recent_activities(activities, days=30)
        activity_frequency_score = min(len(recent_activities) * 10, 100)  # Max 10 activities for 100%
        
        # Duration engagement score
        total_duration = sum([a.get('duration', 0) for a in activities if a.get('duration')])
        duration_score = min(total_duration / 60 * 5, 100)  # 5 points per hour, max 100%
        
        # Activity diversity score
        activity_types = set([a.get('activity_type') for a in activities])
        diversity_score = min(len(activity_types) * 15, 100)  # 15 points per activity type
        
        # Combine scores
        engagement_score = (activity_frequency_score * 0.4 + 
                           duration_score * 0.4 + 
                           diversity_score * 0.2)
        
        return min(engagement_score, 100.0)
    
    def _calculate_consistency_score(self, activities: List[Dict]) -> float:
        """Calculate consistency score based on regular learning patterns"""
        if len(activities) < 3:
            return 50.0  # Neutral score for new learners
        
        # Get timestamps and sort
        timestamps = []
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity.get('timestamp', '').replace('Z', '+00:00'))
                timestamps.append(timestamp)
            except:
                continue
        
        if len(timestamps) < 2:
            return 50.0
        
        # Calculate time gaps between activities
        timestamps.sort()
        gaps = [(timestamps[i] - timestamps[i-1]).days for i in range(1, len(timestamps))]
        
        if not gaps:
            return 50.0
        
        # Calculate consistency (lower standard deviation = higher consistency)
        avg_gap = statistics.mean(gaps)
        if avg_gap == 0:
            return 100.0
        
        consistency_factor = 1 / (statistics.stdev(gaps) / avg_gap + 1)
        consistency_score = min(consistency_factor * 100, 100)
        
        return consistency_score
    
    def _get_recent_activities(self, activities: List[Dict], days: int = 30) -> List[Dict]:
        """Get activities from the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_activities = []
        
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity.get('timestamp', '').replace('Z', '+00:00'))
                if timestamp >= cutoff_date:
                    recent_activities.append(activity)
            except:
                continue
        
        return recent_activities
    
    def _get_performance_level(self, score: float) -> str:
        """Determine performance level based on score"""
        for level, threshold in sorted(self.performance_thresholds.items(), 
                                     key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return 'needs_improvement'
    
    def _generate_score_insights(self, test_score: float, quiz_score: float, 
                               engagement_score: float, consistency_score: float, 
                               final_score: float) -> List[str]:
        """Generate insights based on score components"""
        insights = []
        
        # Test performance insights
        if test_score >= 85:
            insights.append("Excellent test performance - strong grasp of concepts")
        elif test_score >= 70:
            insights.append("Good test performance with room for improvement")
        else:
            insights.append("Test scores suggest need for concept review")
        
        # Quiz performance insights
        if quiz_score >= 80:
            insights.append("Strong quiz performance - quick recall and understanding")
        elif quiz_score >= 65:
            insights.append("Steady quiz performance")
        else:
            insights.append("Quiz scores indicate need for more practice")
        
        # Engagement insights
        if engagement_score >= 80:
            insights.append("Highly engaged learner with consistent activity")
        elif engagement_score >= 60:
            insights.append("Good engagement level")
        else:
            insights.append("Consider increasing learning activity frequency")
        
        # Consistency insights
        if consistency_score >= 75:
            insights.append("Consistent learning schedule detected")
        elif consistency_score >= 50:
            insights.append("Moderate learning consistency")
        else:
            insights.append("Irregular learning pattern - consider scheduling")
        
        return insights
    
    def _generate_score_based_recommendations(self, final_score: float, performance_level: str) -> List[Dict]:
        """Generate recommendations based on score and performance level"""
        recommendations = []
        
        if performance_level == 'excellent':
            recommendations.append({
                'type': 'advanced_content',
                'title': 'Challenge Yourself with Advanced Topics',
                'description': 'Your excellent performance suggests you\'re ready for more challenging material.',
                'priority': 'high',
                'suggested_difficulty': 'advanced'
            })
        elif performance_level in ['very_good', 'good']:
            recommendations.append({
                'type': 'skill_building',
                'title': 'Reinforce Core Concepts',
                'description': 'Continue building on your solid foundation with targeted practice.',
                'priority': 'medium',
                'suggested_difficulty': 'intermediate'
            })
        elif performance_level == 'average':
            recommendations.append({
                'type': 'foundational_review',
                'title': 'Strengthen Fundamentals',
                'description': 'Focus on reviewing core concepts to improve overall performance.',
                'priority': 'high',
                'suggested_difficulty': 'beginner'
            })
        else:
            recommendations.append({
                'type': 'remedial_support',
                'title': 'Comprehensive Review Needed',
                'description': 'Consider starting with foundational materials and seeking additional support.',
                'priority': 'urgent',
                'suggested_difficulty': 'beginner'
            })
        
        return recommendations
    
    def _get_new_learner_score(self) -> Dict[str, Any]:
        """Default score for new learners with no activity"""
        return {
            'learner_id': None,
            'overall_score': 50.0,
            'performance_level': 'new_learner',
            'component_scores': {
                'test_score': 50.0,
                'quiz_score': 50.0,
                'engagement_score': 0.0,
                'consistency_score': 50.0
            },
            'weighting_used': self.weight_config,
            'insights': [
                'Welcome! Start with our beginner-friendly courses',
                'Complete your first activities to get a personalized score',
                'Set up your learning preferences for better recommendations'
            ],
            'recommendations': [{
                'type': 'getting_started',
                'title': 'Start Your Learning Journey',
                'description': 'Begin with foundational courses to establish your learning profile.',
                'priority': 'high',
                'suggested_difficulty': 'beginner'
            }],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def compare_learners(self, learner_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple learners and provide ranking/analysis"""
        if not learner_scores:
            return {'error': 'No learner scores provided'}
        
        # Sort by overall score
        ranked_learners = sorted(learner_scores, 
                               key=lambda x: x.get('overall_score', 0), 
                               reverse=True)
        
        scores = [l.get('overall_score', 0) for l in ranked_learners]
        
        return {
            'total_learners': len(ranked_learners),
            'rankings': [
                {
                    'rank': i + 1,
                    'learner_id': l.get('learner_id'),
                    'score': l.get('overall_score', 0),
                    'performance_level': l.get('performance_level')
                }
                for i, l in enumerate(ranked_learners)
            ],
            'statistics': {
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'average_score': statistics.mean(scores),
                'median_score': statistics.median(scores),
                'standard_deviation': statistics.stdev(scores) if len(scores) > 1 else 0
            },
            'performance_distribution': self._get_performance_distribution(ranked_learners)
        }
    
    def _get_performance_distribution(self, learners: List[Dict]) -> Dict[str, int]:
        """Get distribution of performance levels"""
        distribution = {}
        for learner in learners:
            level = learner.get('performance_level', 'unknown')
            distribution[level] = distribution.get(level, 0) + 1
        return distribution

# Global scoring system instance
scoring_system = EnhancedScoringSystem()