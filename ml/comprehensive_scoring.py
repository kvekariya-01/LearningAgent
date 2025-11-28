#!/usr/bin/env python3
"""
🎯 Comprehensive Scoring System for Learning Agent
Calculates advanced learner scores based on test and quiz marks with course recommendations
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import math

class ComprehensiveScoringSystem:
    """🎯 Advanced scoring system for comprehensive learner assessment"""
    
    def __init__(self):
        # 🎨 Emojis for better UX
        self.emoji_scores = {
            'excellent': '🌟',
            'very_good': '⭐', 
            'good': '✅',
            'satisfactory': '👍',
            'needs_improvement': '⚠️',
            'poor': '❌'
        }
        
        # 📊 Weighted configuration (60% tests, 40% quizzes as requested)
        self.weight_config = {
            'test_score': 0.6,      # 60% weight for tests
            'quiz_score': 0.4,      # 40% weight for quizzes
            'engagement_bonus': 0.1  # 10% bonus for consistency
        }
        
        # 📈 Performance thresholds
        self.performance_thresholds = {
            'excellent': 90,
            'very_good': 80,
            'good': 70,
            'satisfactory': 60,
            'needs_improvement': 50,
            'poor': 40
        }
        
        # 🎯 Difficulty multipliers
        self.difficulty_multipliers = {
            'beginner': 1.0,
            'intermediate': 1.2,
            'advanced': 1.5,
            'expert': 1.8
        }
    
    def calculate_learner_score(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Calculate comprehensive learner score based on test and quiz marks"""
        try:
            learner_id = learner_data.get('id') or learner_data.get('_id')
            activities = learner_data.get('activities', [])
            
            if not activities:
                return self._get_new_learner_score()
            
            # 📊 Calculate component scores
            test_score = self._calculate_test_average(activities)
            quiz_score = self._calculate_quiz_average(activities)
            engagement_score = self._calculate_engagement_consistency(activities, learner_data)
            
            # 🧮 Calculate weighted final score
            overall_score = (
                test_score * self.weight_config['test_score'] +
                quiz_score * self.weight_config['quiz_score']
            )
            
            # 🎯 Apply engagement bonus
            engagement_bonus = min(engagement_score / 100 * self.weight_config['engagement_bonus'] * 100, 5)
            overall_score += engagement_bonus
            
            # 🎨 Determine performance level with emojis
            performance_level = self._get_performance_level(overall_score)
            performance_emoji = self.emoji_scores.get(performance_level, '📊')
            
            # 💡 Generate insights and recommendations
            insights = self._generate_score_insights(test_score, quiz_score, engagement_score, overall_score)
            recommendations = self._generate_score_based_recommendations(overall_score, performance_level)
            
            # 🎯 Course recommendations based on performance
            course_recommendations = self._get_course_recommendations_by_performance(performance_level)
            
            return {
                'learner_id': learner_id,
                'overall_score': round(overall_score, 2),
                'performance_level': performance_level,
                'performance_emoji': performance_emoji,
                'component_scores': {
                    'test_average': round(test_score, 2),
                    'quiz_average': round(quiz_score, 2),
                    'engagement_score': round(engagement_score, 2),
                    'engagement_bonus': round(engagement_bonus, 2)
                },
                'weighting_used': self.weight_config,
                'insights': insights,
                'recommendations': recommendations,
                'course_recommendations': course_recommendations,
                'learning_path': self._suggest_learning_path(performance_level),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'🎯 Scoring calculation failed: {str(e)}'}
    
    def _calculate_test_average(self, activities: List[Dict]) -> float:
        """📝 Calculate weighted test score average"""
        test_activities = [a for a in activities 
                          if a.get('activity_type') in ['test_completed', 'exam_taken', 'assessment_completed']]
        
        if not test_activities:
            return 75.0  # Default neutral score
        
        test_scores = []
        for activity in test_activities:
            score = activity.get('score', 0)
            difficulty = activity.get('difficulty', 'intermediate')
            
            # Apply difficulty multiplier
            adjusted_score = min(score * self.difficulty_multipliers.get(difficulty, 1.0), 100)
            test_scores.append(adjusted_score)
        
        # Recent tests get higher weight
        if len(test_scores) > 1:
            weights = [0.3 + (i * 0.2) for i in range(len(test_scores))]
            weights.reverse()  # Most recent first
            weighted_sum = sum(score * weight for score, weight in zip(test_scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return test_scores[0] if test_scores else 75.0
    
    def _calculate_quiz_average(self, activities: List[Dict]) -> float:
        """❓ Calculate quiz score average"""
        quiz_activities = [a for a in activities 
                          if a.get('activity_type') in ['quiz_completed', 'quiz_taken', 'quick_assessment']]
        
        if not quiz_activities:
            return 75.0  # Default neutral score
        
        quiz_scores = [activity.get('score', 0) for activity in quiz_activities]
        return statistics.mean(quiz_scores) if quiz_scores else 75.0
    
    def _calculate_engagement_consistency(self, activities: List[Dict], learner_data: Dict) -> float:
        """🔥 Calculate engagement and consistency score"""
        if not activities:
            return 0.0
        
        # 📅 Recent activity frequency
        recent_activities = self._get_recent_activities(activities, days=30)
        activity_frequency_score = min(len(recent_activities) * 10, 100)
        
        # ⏱️ Duration engagement
        total_duration = sum([a.get('duration', 0) for a in activities if a.get('duration')])
        duration_score = min(total_duration / 60 * 5, 100)  # 5 points per hour
        
        # 🎯 Activity diversity
        activity_types = set([a.get('activity_type') for a in activities])
        diversity_score = min(len(activity_types) * 15, 100)  # 15 points per activity type
        
        # 📈 Consistency calculation
        consistency_score = self._calculate_consistency_score(activities)
        
        # Combine scores
        engagement_score = (
            activity_frequency_score * 0.3 + 
            duration_score * 0.3 + 
            diversity_score * 0.2 + 
            consistency_score * 0.2
        )
        
        return min(engagement_score, 100.0)
    
    def _calculate_consistency_score(self, activities: List[Dict]) -> float:
        """📅 Calculate learning consistency score"""
        if len(activities) < 3:
            return 50.0  # Neutral for new learners
        
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
        
        # Calculate time gaps
        timestamps.sort()
        gaps = [(timestamps[i] - timestamps[i-1]).days for i in range(1, len(timestamps))]
        
        if not gaps:
            return 50.0
        
        # Consistency factor (lower std dev = higher consistency)
        avg_gap = statistics.mean(gaps)
        if avg_gap == 0:
            return 100.0
        
        consistency_factor = 1 / (statistics.stdev(gaps) / avg_gap + 1)
        consistency_score = min(consistency_factor * 100, 100)
        
        return consistency_score
    
    def _get_recent_activities(self, activities: List[Dict], days: int = 30) -> List[Dict]:
        """📅 Get activities from the last N days"""
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
        """📊 Determine performance level based on score"""
        for level, threshold in sorted(self.performance_thresholds.items(), 
                                     key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return 'poor'
    
    def _generate_score_insights(self, test_score: float, quiz_score: float, 
                               engagement_score: float, overall_score: float) -> List[str]:
        """💡 Generate personalized insights"""
        insights = []
        
        # 📝 Test performance insights
        if test_score >= 85:
            insights.append("🎯 Excellent test performance - strong grasp of concepts")
        elif test_score >= 70:
            insights.append("✅ Good test performance with room for improvement")
        else:
            insights.append("⚠️ Test scores suggest need for concept review")
        
        # ❓ Quiz performance insights
        if quiz_score >= 80:
            insights.append("🧠 Strong quiz performance - quick recall and understanding")
        elif quiz_score >= 65:
            insights.append("📈 Steady quiz performance")
        else:
            insights.append("💪 Quiz scores indicate need for more practice")
        
        # 🔥 Engagement insights
        if engagement_score >= 80:
            insights.append("🚀 Highly engaged learner with consistent activity")
        elif engagement_score >= 60:
            insights.append("👍 Good engagement level")
        else:
            insights.append("📈 Consider increasing learning activity frequency")
        
        # 📊 Overall performance
        if overall_score >= 85:
            insights.append("🌟 Outstanding overall performance!")
        elif overall_score >= 70:
            insights.append("⭐ Solid performance across all areas")
        else:
            insights.append("🎯 Focus on consistent practice and improvement")
        
        return insights
    
    def _generate_score_based_recommendations(self, overall_score: float, performance_level: str) -> List[Dict]:
        """🎯 Generate performance-based recommendations"""
        recommendations = []
        
        if performance_level == 'excellent':
            recommendations.append({
                'type': 'advanced_challenge',
                'title': '🚀 Challenge Yourself with Advanced Topics',
                'description': 'Your excellent performance suggests you\'re ready for more challenging material.',
                'priority': 'high',
                'suggested_difficulty': 'advanced',
                'emoji': '🚀'
            })
        elif performance_level in ['very_good', 'good']:
            recommendations.append({
                'type': 'skill_building',
                'title': '⭐ Reinforce Core Concepts',
                'description': 'Continue building on your solid foundation with targeted practice.',
                'priority': 'medium',
                'suggested_difficulty': 'intermediate',
                'emoji': '⭐'
            })
        elif performance_level == 'satisfactory':
            recommendations.append({
                'type': 'foundational_review',
                'title': '👍 Strengthen Fundamentals',
                'description': 'Focus on reviewing core concepts to improve overall performance.',
                'priority': 'high',
                'suggested_difficulty': 'beginner',
                'emoji': '👍'
            })
        else:
            recommendations.append({
                'type': 'remedial_support',
                'title': '📚 Comprehensive Review Needed',
                'description': 'Consider starting with foundational materials and seeking additional support.',
                'priority': 'urgent',
                'suggested_difficulty': 'beginner',
                'emoji': '📚'
            })
        
        return recommendations
    
    def _get_course_recommendations_by_performance(self, performance_level: str) -> List[Dict]:
        """📚 Get course recommendations based on performance level"""
        
        # 📚 Course catalog with performance-based filtering
        course_catalog = {
            'poor': [
                {'id': 'foundations-101', 'title': '🎯 Learning Foundations', 'difficulty': 'beginner', 'emoji': '🎯'},
                {'id': 'basics-review', 'title': '📝 Concept Review Basics', 'difficulty': 'beginner', 'emoji': '📝'},
                {'id': 'study-skills', 'title': '📖 Study Skills Workshop', 'difficulty': 'beginner', 'emoji': '📖'}
            ],
            'needs_improvement': [
                {'id': 'core-concepts', 'title': '💡 Core Concepts Mastery', 'difficulty': 'beginner', 'emoji': '💡'},
                {'id': 'practice-track', 'title': '🏃 Practice Track', 'difficulty': 'beginner', 'emoji': '🏃'},
                {'id': 'skill-building', 'title': '🔨 Skill Building Basics', 'difficulty': 'intermediate', 'emoji': '🔨'}
            ],
            'satisfactory': [
                {'id': 'intermediate-track', 'title': '📈 Intermediate Learning Path', 'difficulty': 'intermediate', 'emoji': '📈'},
                {'id': 'project-basics', 'title': '🛠️ Project Basics', 'difficulty': 'intermediate', 'emoji': '🛠️'},
                {'id': 'applied-learning', 'title': '🎯 Applied Learning', 'difficulty': 'intermediate', 'emoji': '🎯'}
            ],
            'good': [
                {'id': 'advanced-concepts', 'title': '🚀 Advanced Concepts', 'difficulty': 'intermediate', 'emoji': '🚀'},
                {'id': 'specialization-track', 'title': '🎓 Specialization Track', 'difficulty': 'advanced', 'emoji': '🎓'},
                {'id': 'leadership-skills', 'title': '👑 Leadership Skills', 'difficulty': 'advanced', 'emoji': '👑'}
            ],
            'very_good': [
                {'id': 'expert-level', 'title': '🌟 Expert Level Challenge', 'difficulty': 'advanced', 'emoji': '🌟'},
                {'id': 'mastery-track', 'title': '👑 Mastery Track', 'difficulty': 'expert', 'emoji': '👑'},
                {'id': 'innovation-projects', 'title': '💡 Innovation Projects', 'difficulty': 'expert', 'emoji': '💡'}
            ],
            'excellent': [
                {'id': 'expert-mastery', 'title': '🏆 Expert Mastery Program', 'difficulty': 'expert', 'emoji': '🏆'},
                {'id': 'mentorship-track', 'title': '🎯 Mentorship Program', 'difficulty': 'expert', 'emoji': '🎯'},
                {'id': 'research-projects', 'title': '🔬 Research Projects', 'difficulty': 'expert', 'emoji': '🔬'}
            ]
        }
        
        return course_catalog.get(performance_level, course_catalog['satisfactory'])
    
    def _suggest_learning_path(self, performance_level: str) -> List[str]:
        """🛤️ Suggest personalized learning path"""
        paths = {
            'poor': [
                "📚 Start with foundational courses",
                "📝 Complete basic assessments", 
                "💪 Focus on daily practice",
                "🤝 Seek additional support",
                "📈 Track progress regularly"
            ],
            'needs_improvement': [
                "🔍 Review weak areas",
                "📖 Study core concepts thoroughly",
                "🎯 Practice with guided exercises",
                "📊 Monitor improvement",
                "🌟 Celebrate small wins"
            ],
            'satisfactory': [
                "💡 Strengthen understanding",
                "🛠️ Apply concepts practically", 
                "📈 Challenge with intermediate content",
                "🤝 Join study groups",
                "🎯 Set intermediate goals"
            ],
            'good': [
                "🚀 Explore advanced topics",
                "🎓 Specialize in areas of interest",
                "🔨 Work on complex projects",
                "👥 Teach or mentor others",
                "🏆 Aim for mastery"
            ],
            'very_good': [
                "🌟 Tackle expert-level challenges",
                "💡 Innovate and create",
                "🎯 Lead learning initiatives", 
                "🔬 Conduct research",
                "👑 Become a subject expert"
            ],
            'excellent': [
                "🏆 Push boundaries of knowledge",
                "🎯 Mentor high performers",
                "🔬 Lead research initiatives",
                "💡 Innovate new methodologies",
                "🌟 Inspire learning excellence"
            ]
        }
        
        return paths.get(performance_level, paths['satisfactory'])
    
    def _get_new_learner_score(self) -> Dict[str, Any]:
        """🆕 Default score for new learners"""
        return {
            'learner_id': None,
            'overall_score': 50.0,
            'performance_level': 'new_learner',
            'performance_emoji': '🆕',
            'component_scores': {
                'test_average': 50.0,
                'quiz_average': 50.0,
                'engagement_score': 0.0,
                'engagement_bonus': 0.0
            },
            'weighting_used': self.weight_config,
            'insights': [
                '🆕 Welcome! Start with our beginner-friendly courses',
                '📝 Complete your first activities to get a personalized score',
                '🎯 Set up your learning preferences for better recommendations'
            ],
            'recommendations': [{
                'type': 'getting_started',
                'title': '🚀 Start Your Learning Journey',
                'description': 'Begin with foundational courses to establish your learning profile.',
                'priority': 'high',
                'suggested_difficulty': 'beginner',
                'emoji': '🚀'
            }],
            'course_recommendations': [
                {'id': 'welcome-course', 'title': '🎯 Welcome to Learning', 'difficulty': 'beginner', 'emoji': '🎯'},
                {'id': 'orientation', 'title': '📚 Learning Orientation', 'difficulty': 'beginner', 'emoji': '📚'},
                {'id': 'goal-setting', 'title': '🎯 Goal Setting Workshop', 'difficulty': 'beginner', 'emoji': '🎯'}
            ],
            'learning_path': [
                "🆕 Complete orientation course",
                "📝 Take initial assessments",
                "🎯 Set learning goals",
                "📚 Start with beginner courses",
                "📈 Track your progress"
            ],
            'timestamp': datetime.utcnow().isoformat()
        }

# 🌍 Global scoring system instance
comprehensive_scoring_system = ComprehensiveScoringSystem()