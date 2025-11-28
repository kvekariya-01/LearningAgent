"""Enhanced recommendation engine based on learner scoring system"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from models.test_result import LearnerScoreSummary
from ml.scoring_engine import ScoringEngine
from utils.crud_operations import read_learner, read_contents, read_engagements
from models.content import Content
from models.learner import Learner

class ScoreBasedRecommender:
    """Advanced recommender using learner test scores and performance metrics"""
    
    def __init__(self):
        self.scoring_engine = ScoringEngine()
        
        # Difficulty mapping for recommendations
        self.difficulty_mapping = {
            'beginner': ['beginner', 'easy'],
            'intermediate': ['beginner', 'intermediate', 'medium'],
            'advanced': ['intermediate', 'advanced', 'difficult']
        }
        
        # Performance thresholds
        self.thresholds = {
            'excellent': 90,
            'good': 80,
            'satisfactory': 70,
            'needs_improvement': 60
        }
    
    def calculate_course_match_score(self, course: Dict[str, Any], score_summary: LearnerScoreSummary) -> Dict[str, Any]:
        """Calculate detailed match score for a course based on learner's performance"""
        
        score_details = {
            'base_score': 0,
            'difficulty_match': 0,
            'performance_alignment': 0,
            'progression_score': 0,
            'subject_strength_bonus': 0,
            'recommendation_confidence': 0
        }
        
        # Difficulty matching (40% weight)
        course_difficulty = course.get('difficulty_level', 'intermediate').lower()
        recommendation_level = score_summary.recommendation_level
        
        if recommendation_level in self.difficulty_mapping:
            suitable_difficulties = self.difficulty_mapping[recommendation_level]
            
            if course_difficulty in suitable_difficulties:
                score_details['difficulty_match'] = 40
                if course_difficulty == recommendation_level:
                    score_details['difficulty_match'] = 45  # Perfect match bonus
            else:
                # Penalty for wrong difficulty
                score_details['difficulty_match'] = 10
        
        # Performance alignment (30% weight)
        latest_score = score_summary.latest_score
        if latest_score >= self.thresholds['excellent']:
            score_details['performance_alignment'] = 30
        elif latest_score >= self.thresholds['good']:
            score_details['performance_alignment'] = 25
        elif latest_score >= self.thresholds['satisfactory']:
            score_details['performance_alignment'] = 20
        elif latest_score >= self.thresholds['needs_improvement']:
            score_details['performance_alignment'] = 15
        else:
            score_details['performance_alignment'] = 10
            
        # Progression scoring (20% weight)
        trend = score_summary.score_trend
        confidence = score_summary.confidence_score
        
        if trend == 'improving':
            score_details['progression_score'] = 20
        elif trend == 'stable':
            score_details['progression_score'] = 15
        else:  # declining
            score_details['progression_score'] = 10
            
        # Subject strength bonus (10% weight)
        strongest_subject = score_summary.strongest_subject
        course_subject = course.get('course_id', '')
        
        if strongest_subject in course_subject or course_subject in strongest_subject:
            score_details['subject_strength_bonus'] = 10
        
        # Calculate total score
        total_score = sum(score_details.values())
        
        # Calculate recommendation confidence
        confidence_factor = score_summary.confidence_score / 100
        score_details['recommendation_confidence'] = total_score * confidence_factor
        
        return {
            'total_score': round(total_score, 2),
            'confidence': round(score_details['recommendation_confidence'], 2),
            'score_breakdown': score_details,
            'recommendation_reason': self._generate_recommendation_reason(score_details, recommendation_level, course_difficulty)
        }
    
    def _generate_recommendation_reason(self, score_details: Dict[str, Any], recommendation_level: str, course_difficulty: str) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if score_details['difficulty_match'] >= 40:
            reasons.append(f"Perfect difficulty match for {recommendation_level} level learners")
        elif score_details['difficulty_match'] >= 25:
            reasons.append(f"Good difficulty match for {recommendation_level} level learners")
            
        if score_details['performance_alignment'] >= 25:
            reasons.append("Strong performance alignment")
        elif score_details['performance_alignment'] >= 20:
            reasons.append("Good performance match")
            
        if score_details['progression_score'] >= 18:
            reasons.append("Supports current learning momentum")
        elif score_details['progression_score'] >= 15:
            reasons.append("Appropriate progression level")
            
        if score_details['subject_strength_bonus'] > 0:
            reasons.append("Builds on your strongest subject area")
            
        return "; ".join(reasons) if reasons else "General recommendation based on your learning profile"
    
    def get_personalized_recommendations(self, learner_id: str, score_summary: LearnerScoreSummary, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get personalized course recommendations based on scoring analysis"""
        
        # Get all available courses
        all_courses = read_contents()
        if not all_courses:
            return []
            
        # Calculate match scores for all courses
        scored_courses = []
        for course in all_courses:
            match_analysis = self.calculate_course_match_score(course, score_summary)
            scored_courses.append({
                'course': course,
                'match_score': match_analysis['total_score'],
                'confidence': match_analysis['confidence'],
                'reason': match_analysis['recommendation_reason'],
                'score_breakdown': match_analysis['score_breakdown']
            })
        
        # Sort by match score (descending)
        scored_courses.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top N recommendations
        recommendations = []
        for i, course_data in enumerate(scored_courses[:top_n]):
            recommendation = {
                'rank': i + 1,
                'course': course_data['course'],  # Include the full course object
                'course_id': course_data['course']['id'],
                'title': course_data['course']['title'],
                'description': course_data['course']['description'],
                'difficulty_level': course_data['course'].get('difficulty_level', 'intermediate'),
                'content_type': course_data['course'].get('content_type', 'video'),
                'tags': course_data['course'].get('tags', []),
                'match_score': course_data['match_score'],
                'confidence': course_data['confidence'],
                'recommendation_reason': course_data['reason'],
                'estimated_completion_time': self._estimate_completion_time(course_data['course'], score_summary),
                'prerequisites_met': self._check_prerequisites(course_data['course'], score_summary),
                'next_steps': self._suggest_next_steps(course_data['course'], score_summary)
            }
            recommendations.append(recommendation)
            
        return recommendations
    
    def _estimate_completion_time(self, course: Dict[str, Any], score_summary: LearnerScoreSummary) -> str:
        """Estimate completion time based on learner performance"""
        base_time = course.get('estimated_duration', 60)  # Default 60 minutes
        
        # Adjust based on performance
        if score_summary.confidence_score >= 80:
            # High confidence - may complete faster
            estimated_time = base_time * 0.8
        elif score_summary.confidence_score <= 50:
            # Low confidence - may need more time
            estimated_time = base_time * 1.2
        else:
            estimated_time = base_time
            
        # Round to nearest 5 minutes
        estimated_time = round(estimated_time / 5) * 5
        
        return f"{int(estimated_time)} minutes"
    
    def _check_prerequisites(self, course: Dict[str, Any], score_summary: LearnerScoreSummary) -> bool:
        """Check if learner meets course prerequisites"""
        # This is a simplified version - in reality, you'd have a proper prerequisite system
        course_difficulty = course.get('difficulty_level', 'intermediate').lower()
        recommendation_level = score_summary.recommendation_level
        
        difficulty_hierarchy = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        
        course_level = difficulty_hierarchy.get(course_difficulty, 2)
        learner_level = difficulty_hierarchy.get(recommendation_level, 1)
        
        # Allow up to one level above current performance
        return course_level <= learner_level + 1
    
    def _suggest_next_steps(self, course: Dict[str, Any], score_summary: LearnerScoreSummary) -> List[str]:
        """Suggest next steps after this course"""
        next_steps = []
        
        current_difficulty = course.get('difficulty_level', 'intermediate').lower()
        
        if current_difficulty == 'beginner' and score_summary.recommendation_level == 'beginner':
            next_steps.append("Focus on completing practice exercises")
            next_steps.append("Take regular quizzes to reinforce learning")
        elif current_difficulty == 'intermediate':
            next_steps.append("Apply concepts through hands-on projects")
            if score_summary.score_trend == 'improving':
                next_steps.append("Consider advancing to advanced topics soon")
        elif current_difficulty == 'advanced':
            next_steps.append("Engage in complex problem-solving activities")
            next_steps.append("Consider teaching or mentoring others")
            
        return next_steps
    
    def generate_learning_path(self, learner_id: str, score_summary: LearnerScoreSummary, target_skills: List[str] = None) -> Dict[str, Any]:
        """Generate a complete learning path based on scoring analysis"""
        
        recommendations = self.get_personalized_recommendations(learner_id, score_summary, top_n=10)
        
        if not recommendations:
            return {
                'learning_path': [],
                'path_summary': 'No suitable courses found for your current level',
                'estimated_duration': '0 hours',
                'skill_coverage': []
            }
        
        # Organize recommendations into a learning path
        learning_path = []
        covered_skills = set()
        
        for rec in recommendations:
            path_item = {
                'sequence': len(learning_path) + 1,
                'course_id': rec['course_id'],
                'title': rec['title'],
                'difficulty': rec['difficulty_level'],
                'estimated_time': rec['estimated_completion_time'],
                'focus_skills': rec['tags'],
                'prerequisites_met': rec['prerequisites_met'],
                'match_confidence': rec['confidence']
            }
            learning_path.append(path_item)
            covered_skills.update(rec['tags'])
        
        # Calculate total estimated duration
        total_minutes = sum(int(item['estimated_time'].split()[0]) for item in learning_path)
        total_hours = round(total_minutes / 60, 1)
        
        return {
            'learning_path': learning_path,
            'path_summary': f"Personalized learning path with {len(learning_path)} courses covering {len(covered_skills)} skill areas",
            'estimated_duration': f"{total_hours} hours",
            'skill_coverage': list(covered_skills),
            'starting_level': score_summary.recommendation_level,
            'expected_outcome': self._generate_learning_outcome(score_summary)
        }
    
    def _generate_learning_outcome(self, score_summary: LearnerScoreSummary) -> str:
        """Generate expected learning outcome description"""
        if score_summary.recommendation_level == 'beginner':
            return "Foundation knowledge and basic competency in core concepts"
        elif score_summary.recommendation_level == 'intermediate':
            return "Solid understanding with ability to apply concepts practically"
        else:
            return "Advanced proficiency with expertise in complex problem-solving"

# Convenience function for easy integration
def get_score_based_recommendations(learner_id: str, test_results: List = None) -> Dict[str, Any]:
    """Get score-based recommendations for a learner"""
    
    # Get learner data
    learner_data = read_learner(learner_id)
    if not learner_data:
        return {'error': 'Learner not found'}
    
    # Generate score summary
    if test_results is None:
        test_results = []  # Placeholder - implement actual test result retrieval
        
    score_summary = get_learner_score_summary(learner_id, test_results)
    
    # Get recommendations
    recommender = ScoreBasedRecommender()
    recommendations = recommender.get_personalized_recommendations(learner_id, score_summary)
    learning_path = recommender.generate_learning_path(learner_id, score_summary)
    
    return {
        'learner_id': learner_id,
        'score_summary': score_summary.to_dict(),
        'recommendations': recommendations,
        'learning_path': learning_path,
        'generated_at': datetime.now().isoformat()
    }