#!/usr/bin/env python3
"""
Advanced Course Recommendation Engine
Provides personalized course recommendations based on learner scores and performance analytics
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from enhanced_scoring_system import scoring_system

class AdvancedRecommendationEngine:
    """Advanced recommendation engine for personalized course suggestions"""
    
    def __init__(self):
        self.course_catalog = self._load_course_catalog()
        self.recommendation_algorithms = {
            'score_based': self._score_based_recommendations,
            'difficulty_progression': self._difficulty_progression_recommendations,
            'interest_matching': self._interest_matching_recommendations,
            'performance_gap': self._performance_gap_recommendations,
            'comprehensive': self._comprehensive_recommendations
        }
    
    def _load_course_catalog(self) -> List[Dict[str, Any]]:
        """Load comprehensive course catalog"""
        return [
            # Programming Courses
            {
                'id': 'python-fundamentals',
                'title': 'Python Programming Fundamentals',
                'description': 'Complete introduction to Python programming including syntax, data structures, and basic algorithms.',
                'subject': 'Programming',
                'difficulty': 'beginner',
                'content_type': 'interactive',
                'duration': 180,
                'tags': ['python', 'programming', 'fundamentals', 'syntax'],
                'skills': ['problem_solving', 'logical_thinking', 'basic_programming'],
                'prerequisites': [],
                'learning_outcomes': ['Write basic Python programs', 'Understand data types', 'Use control structures'],
                'rating': 4.8,
                'enrollment_count': 1250
            },
            {
                'id': 'python-advanced',
                'title': 'Advanced Python Programming',
                'description': 'Advanced Python concepts including OOP, decorators, generators, and design patterns.',
                'subject': 'Programming',
                'difficulty': 'advanced',
                'content_type': 'video',
                'duration': 240,
                'tags': ['python', 'oop', 'design_patterns', 'advanced'],
                'skills': ['object_oriented_programming', 'code_optimization', 'software_design'],
                'prerequisites': ['python-fundamentals'],
                'learning_outcomes': ['Implement design patterns', 'Write optimized code', 'Build complex applications'],
                'rating': 4.9,
                'enrollment_count': 800
            },
            {
                'id': 'web-development-html-css',
                'title': 'Web Development: HTML & CSS',
                'description': 'Learn to create beautiful and responsive websites using HTML5 and CSS3.',
                'subject': 'Web Development',
                'difficulty': 'beginner',
                'content_type': 'interactive',
                'duration': 150,
                'tags': ['html', 'css', 'web', 'responsive', 'design'],
                'skills': ['web_design', 'responsive_design', 'ui_design'],
                'prerequisites': [],
                'learning_outcomes': ['Create responsive web pages', 'Use CSS frameworks', 'Implement modern layouts'],
                'rating': 4.7,
                'enrollment_count': 2100
            },
            {
                'id': 'javascript-mastery',
                'title': 'JavaScript Mastery',
                'description': 'Master JavaScript from basics to advanced concepts including ES6+, async programming, and frameworks.',
                'subject': 'Web Development',
                'difficulty': 'intermediate',
                'content_type': 'video',
                'duration': 300,
                'tags': ['javascript', 'es6', 'async', 'programming', 'web'],
                'skills': ['modern_javascript', 'async_programming', 'dom_manipulation'],
                'prerequisites': ['web-development-html-css'],
                'learning_outcomes': ['Write modern JavaScript', 'Handle asynchronous operations', 'Build interactive UIs'],
                'rating': 4.8,
                'enrollment_count': 1850
            },
            {
                'id': 'react-complete-guide',
                'title': 'Complete React Development Guide',
                'description': 'Learn React from scratch including hooks, state management, and building full applications.',
                'subject': 'Web Development',
                'difficulty': 'intermediate',
                'content_type': 'project',
                'duration': 360,
                'tags': ['react', 'hooks', 'state_management', 'frontend'],
                'skills': ['react_development', 'component_design', 'spa_development'],
                'prerequisites': ['javascript-mastery'],
                'learning_outcomes': ['Build React applications', 'Use hooks effectively', 'Manage application state'],
                'rating': 4.9,
                'enrollment_count': 2200
            },
            
            # Data Science & Machine Learning
            {
                'id': 'data-science-intro',
                'title': 'Introduction to Data Science',
                'description': 'Fundamental concepts of data science including statistics, data manipulation, and visualization.',
                'subject': 'Data Science',
                'difficulty': 'beginner',
                'content_type': 'article',
                'duration': 200,
                'tags': ['data_science', 'statistics', 'pandas', 'numpy', 'visualization'],
                'skills': ['data_analysis', 'statistical_thinking', 'data_visualization'],
                'prerequisites': ['python-fundamentals'],
                'learning_outcomes': ['Analyze datasets', 'Create visualizations', 'Apply statistical methods'],
                'rating': 4.8,
                'enrollment_count': 1600
            },
            {
                'id': 'machine-learning-foundations',
                'title': 'Machine Learning Foundations',
                'description': 'Core machine learning concepts including supervised/unsupervised learning and model evaluation.',
                'subject': 'Machine Learning',
                'difficulty': 'intermediate',
                'content_type': 'video',
                'duration': 280,
                'tags': ['machine_learning', 'algorithms', 'scikit-learn', 'models'],
                'skills': ['algorithm_understanding', 'model_training', 'performance_evaluation'],
                'prerequisites': ['data-science-intro'],
                'learning_outcomes': ['Implement ML algorithms', 'Train and evaluate models', 'Select appropriate algorithms'],
                'rating': 4.7,
                'enrollment_count': 1200
            },
            {
                'id': 'deep-learning-specialization',
                'title': 'Deep Learning Specialization',
                'description': 'Advanced deep learning concepts including neural networks, CNNs, RNNs, and transfer learning.',
                'subject': 'Machine Learning',
                'difficulty': 'advanced',
                'content_type': 'project',
                'duration': 400,
                'tags': ['deep_learning', 'neural_networks', 'tensorflow', 'pytorch'],
                'skills': ['neural_network_design', 'deep_learning_frameworks', 'model_optimization'],
                'prerequisites': ['machine-learning-foundations'],
                'learning_outcomes': ['Build neural networks', 'Implement CNNs/RNNs', 'Deploy ML models'],
                'rating': 4.9,
                'enrollment_count': 750
            },
            
            # Mathematics
            {
                'id': 'calculus-essentials',
                'title': 'Essential Calculus',
                'description': 'Fundamental calculus concepts including limits, derivatives, integrals, and applications.',
                'subject': 'Mathematics',
                'difficulty': 'intermediate',
                'content_type': 'video',
                'duration': 320,
                'tags': ['calculus', 'derivatives', 'integrals', 'mathematical_analysis'],
                'skills': ['mathematical_reasoning', 'problem_solving', 'analytical_thinking'],
                'prerequisites': ['algebra-basics'],
                'learning_outcomes': ['Calculate derivatives', 'Solve integration problems', 'Apply calculus concepts'],
                'rating': 4.6,
                'enrollment_count': 980
            },
            {
                'id': 'linear-algebra-programmers',
                'title': 'Linear Algebra for Programmers',
                'description': 'Linear algebra concepts essential for machine learning and computer graphics.',
                'subject': 'Mathematics',
                'difficulty': 'intermediate',
                'content_type': 'interactive',
                'duration': 240,
                'tags': ['linear_algebra', 'matrices', 'vectors', 'ml_foundations'],
                'skills': ['matrix_operations', 'vector_math', 'mathematical_modeling'],
                'prerequisites': ['calculus-essentials'],
                'learning_outcomes': ['Perform matrix operations', 'Understand vector spaces', 'Apply linear transformations'],
                'rating': 4.7,
                'enrollment_count': 850
            },
            
            # Business & Management
            {
                'id': 'project-management-fundamentals',
                'title': 'Project Management Fundamentals',
                'description': 'Essential project management skills including planning, execution, and risk management.',
                'subject': 'Business',
                'difficulty': 'beginner',
                'content_type': 'article',
                'duration': 180,
                'tags': ['project_management', 'planning', 'leadership', 'business'],
                'skills': ['project_planning', 'team_leadership', 'risk_management'],
                'prerequisites': [],
                'learning_outcomes': ['Plan and execute projects', 'Manage project risks', 'Lead project teams'],
                'rating': 4.5,
                'enrollment_count': 1100
            },
            {
                'id': 'agile-scrum-master',
                'title': 'Agile & Scrum Master Certification',
                'description': 'Master agile methodologies and Scrum framework for modern software development.',
                'subject': 'Business',
                'difficulty': 'intermediate',
                'content_type': 'interactive',
                'duration': 200,
                'tags': ['agile', 'scrum', 'methodology', 'software_development'],
                'skills': ['agile_methodology', 'scrum_framework', 'team_facilitation'],
                'prerequisites': ['project-management-fundamentals'],
                'learning_outcomes': ['Implement agile practices', 'Facilitate Scrum events', 'Lead agile teams'],
                'rating': 4.8,
                'enrollment_count': 920
            },
            
            # Design & UX
            {
                'id': 'ui-ux-design-principles',
                'title': 'UI/UX Design Principles',
                'description': 'Fundamental principles of user interface and user experience design.',
                'subject': 'Design',
                'difficulty': 'beginner',
                'content_type': 'interactive',
                'duration': 160,
                'tags': ['ui_design', 'ux_design', 'user_experience', 'prototyping'],
                'skills': ['user_research', 'wireframing', 'prototyping', 'visual_design'],
                'prerequisites': [],
                'learning_outcomes': ['Conduct user research', 'Create wireframes', 'Design user interfaces'],
                'rating': 4.9,
                'enrollment_count': 1800
            },
            {
                'id': 'figma-advanced-design',
                'title': 'Advanced Figma Design Techniques',
                'description': 'Master advanced Figma features for professional UI/UX design work.',
                'subject': 'Design',
                'difficulty': 'intermediate',
                'content_type': 'video',
                'duration': 220,
                'tags': ['figma', 'advanced_design', 'prototyping', 'collaboration'],
                'skills': ['advanced_figma', 'complex_prototyping', 'design_systems'],
                'prerequisites': ['ui-ux-design-principles'],
                'learning_outcomes': ['Create complex prototypes', 'Design design systems', 'Collaborate effectively'],
                'rating': 4.8,
                'enrollment_count': 750
            },
            
            # Language & Communication
            {
                'id': 'technical-writing',
                'title': 'Technical Writing & Documentation',
                'description': 'Learn to write clear, effective technical documentation and communication.',
                'subject': 'Language',
                'difficulty': 'intermediate',
                'content_type': 'article',
                'duration': 140,
                'tags': ['technical_writing', 'documentation', 'communication', 'writing'],
                'skills': ['technical_writing', 'documentation_design', 'clear_communication'],
                'prerequisites': [],
                'learning_outcomes': ['Write technical documentation', 'Create user guides', 'Communicate technical concepts'],
                'rating': 4.6,
                'enrollment_count': 650
            },
            
            # Assessment Courses
            {
                'id': 'comprehensive-programming-assessment',
                'title': 'Comprehensive Programming Skills Assessment',
                'description': 'Complete assessment covering programming fundamentals, algorithms, and problem-solving.',
                'subject': 'Assessment',
                'difficulty': 'mixed',
                'content_type': 'assessment',
                'duration': 120,
                'tags': ['programming', 'assessment', 'algorithms', 'problem_solving'],
                'skills': ['programming_logic', 'algorithm_design', 'problem_solving'],
                'prerequisites': ['python-fundamentals'],
                'learning_outcomes': ['Assess programming skills', 'Identify knowledge gaps', 'Measure progress'],
                'rating': 4.7,
                'enrollment_count': 500
            },
            {
                'id': 'data-science-certification',
                'title': 'Data Science Certification Exam',
                'description': 'Comprehensive certification exam covering all aspects of data science.',
                'subject': 'Assessment',
                'difficulty': 'advanced',
                'content_type': 'assessment',
                'duration': 180,
                'tags': ['data_science', 'certification', 'statistics', 'machine_learning'],
                'skills': ['data_analysis', 'statistical_modeling', 'ml_implementation'],
                'prerequisites': ['data-science-intro', 'machine-learning-foundations'],
                'learning_outcomes': ['Validate data science skills', 'Gain industry recognition', 'Career advancement'],
                'rating': 4.8,
                'enrollment_count': 300
            }
        ]
    
    def get_comprehensive_recommendations(self, learner_data: Dict[str, Any], 
                                        learner_score: Dict[str, Any], 
                                        recommendation_count: int = 10) -> Dict[str, Any]:
        """Get comprehensive course recommendations based on multiple factors"""
        try:
            learner_id = learner_data.get('id')
            overall_score = learner_score.get('overall_score', 50)
            performance_level = learner_score.get('performance_level', 'new_learner')
            component_scores = learner_score.get('component_scores', {})
            
            # Get recommendations from all algorithms
            all_recommendations = {}
            for algorithm_name, algorithm_func in self.recommendation_algorithms.items():
                try:
                    recommendations = algorithm_func(learner_data, learner_score, recommendation_count)
                    if recommendations:
                        all_recommendations[algorithm_name] = recommendations
                except Exception as e:
                    print(f"Error in {algorithm_name}: {e}")
            
            # Combine and rank recommendations
            final_recommendations = self._combine_recommendations(all_recommendations, recommendation_count)
            
            # Generate learning path
            learning_path = self._generate_learning_path(learner_data, learner_score, final_recommendations)
            
            # Generate insights
            insights = self._generate_recommendation_insights(learner_score, final_recommendations)
            
            return {
                'learner_id': learner_id,
                'recommendations': final_recommendations,
                'learning_path': learning_path,
                'insights': insights,
                'score_analysis': {
                    'overall_performance': performance_level,
                    'strengths': self._identify_strengths(component_scores),
                    'improvement_areas': self._identify_improvement_areas(component_scores),
                    'recommended_focus': self._get_score_focus(component_scores)
                },
                'recommendation_metadata': {
                    'total_courses_evaluated': len(self.course_catalog),
                    'recommendations_generated': len(final_recommendations),
                    'algorithms_used': list(all_recommendations.keys()),
                    'personalization_level': self._calculate_personalization_level(learner_score),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {'error': f'Recommendation generation failed: {str(e)}'}
    
    def _score_based_recommendations(self, learner_data: Dict, learner_score: Dict, count: int) -> List[Dict]:
        """Generate recommendations based on learner score"""
        recommendations = []
        score = learner_score.get('overall_score', 50)
        performance_level = learner_score.get('performance_level', 'new_learner')
        
        for course in self.course_catalog:
            course_difficulty = course.get('difficulty', 'beginner')
            score_match = self._calculate_score_difficulty_match(score, course_difficulty)
            
            if score_match > 0.3:  # Only include reasonably matching courses
                recommendation = {
                    'course': course,
                    'match_score': score_match,
                    'reason': self._get_score_based_reason(performance_level, course_difficulty),
                    'algorithm': 'score_based'
                }
                recommendations.append(recommendation)
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:count]
    
    def _difficulty_progression_recommendations(self, learner_data: Dict, learner_score: Dict, count: int) -> List[Dict]:
        """Generate recommendations for progressive difficulty increase"""
        recommendations = []
        current_score = learner_score.get('overall_score', 50)
        
        # Determine appropriate difficulty progression
        if current_score >= 85:
            target_difficulties = ['advanced', 'expert']
        elif current_score >= 70:
            target_difficulties = ['intermediate', 'advanced']
        elif current_score >= 60:
            target_difficulties = ['beginner', 'intermediate']
        else:
            target_difficulties = ['beginner']
        
        for course in self.course_catalog:
            if course.get('difficulty') in target_difficulties:
                # Check prerequisites are met
                prerequisites = course.get('prerequisites', [])
                if self._check_prerequisites(prerequisites, learner_data):
                    progression_score = self._calculate_progression_score(course, current_score)
                    
                    recommendation = {
                        'course': course,
                        'match_score': progression_score,
                        'reason': f"Progressive difficulty match for {course.get('difficulty')} level",
                        'algorithm': 'difficulty_progression'
                    }
                    recommendations.append(recommendation)
        
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:count]
    
    def _interest_matching_recommendations(self, learner_data: Dict, learner_score: Dict, count: int) -> List[Dict]:
        """Generate recommendations based on learner interests"""
        recommendations = []
        learner_preferences = learner_data.get('preferences', [])
        learning_style = learner_data.get('learning_style', 'Mixed')
        
        # Convert preferences to lowercase for matching
        if isinstance(learner_preferences, str):
            preferences = [p.strip().lower() for p in learner_preferences.split(',')]
        elif isinstance(learner_preferences, list):
            preferences = [str(p).lower() for p in learner_preferences]
        else:
            preferences = []
        
        for course in self.course_catalog:
            interest_score = self._calculate_interest_score(course, preferences, learning_style)
            
            if interest_score > 0.2:  # Include courses with some interest match
                recommendation = {
                    'course': course,
                    'match_score': interest_score,
                    'reason': self._get_interest_based_reason(course, preferences),
                    'algorithm': 'interest_matching'
                }
                recommendations.append(recommendation)
        
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:count]
    
    def _performance_gap_recommendations(self, learner_data: Dict, learner_score: Dict, count: int) -> List[Dict]:
        """Generate recommendations to fill performance gaps"""
        recommendations = []
        component_scores = learner_score.get('component_scores', {})
        
        # Identify weakest areas
        weak_areas = []
        for component, score in component_scores.items():
            if score < 65:  # Consider scores below 65 as weak areas
                weak_areas.append((component, score))
        
        if not weak_areas:
            # No weak areas, recommend advanced content
            return self._score_based_recommendations(learner_data, learner_score, count)
        
        for course in self.course_catalog:
            gap_score = self._calculate_gap_score(course, weak_areas)
            
            if gap_score > 0.1:  # Include courses that address gaps
                recommendation = {
                    'course': course,
                    'match_score': gap_score,
                    'reason': self._get_gap_based_reason(course, weak_areas),
                    'algorithm': 'performance_gap'
                }
                recommendations.append(recommendation)
        
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:count]
    
    def _comprehensive_recommendations(self, learner_data: Dict, learner_score: Dict, count: int) -> List[Dict]:
        """Generate recommendations using comprehensive analysis"""
        # Get a balanced mix from different approaches
        score_recs = self._score_based_recommendations(learner_data, learner_score, count // 2)
        interest_recs = self._interest_matching_recommendations(learner_data, learner_score, count // 2)
        
        # Combine and deduplicate
        all_courses = {}
        
        for rec in score_recs + interest_recs:
            course_id = rec['course']['id']
            if course_id not in all_courses:
                all_courses[course_id] = rec
            else:
                # Average the match scores for duplicate courses
                all_courses[course_id]['match_score'] = (
                    all_courses[course_id]['match_score'] + rec['match_score']
                ) / 2
                all_courses[course_id]['algorithm'] = 'comprehensive'
        
        return list(all_courses.values())[:count]
    
    def _combine_recommendations(self, recommendations_dict: Dict[str, List], count: int) -> List[Dict]:
        """Combine recommendations from multiple algorithms"""
        combined = {}
        
        for algorithm, recs in recommendations_dict.items():
            weight = self._get_algorithm_weight(algorithm)
            
            for rec in recs:
                course_id = rec['course']['id']
                if course_id not in combined:
                    combined[course_id] = rec.copy()
                    combined[course_id]['match_score'] = rec['match_score'] * weight
                    combined[course_id]['algorithms'] = [algorithm]
                else:
                    # Combine scores and algorithms
                    combined[course_id]['match_score'] += rec['match_score'] * weight
                    combined[course_id]['algorithms'].append(algorithm)
                    combined[course_id]['match_score'] /= len(combined[course_id]['algorithms'])
        
        # Sort by combined score and return top recommendations
        sorted_recommendations = sorted(
            combined.values(), 
            key=lambda x: x['match_score'], 
            reverse=True
        )
        
        return sorted_recommendations[:count]
    
    def _get_algorithm_weight(self, algorithm: str) -> float:
        """Get weight for each recommendation algorithm"""
        weights = {
            'score_based': 1.0,
            'difficulty_progression': 0.8,
            'interest_matching': 0.9,
            'performance_gap': 0.7,
            'comprehensive': 1.2
        }
        return weights.get(algorithm, 0.5)
    
    def _calculate_score_difficulty_match(self, score: float, difficulty: str) -> float:
        """Calculate how well a score matches a course difficulty"""
        difficulty_thresholds = {
            'beginner': (0, 70),
            'intermediate': (60, 85),
            'advanced': (75, 100),
            'expert': (85, 100),
            'mixed': (50, 100)
        }
        
        if difficulty not in difficulty_thresholds:
            return 0.5
        
        min_score, max_score = difficulty_thresholds[difficulty]
        
        # Calculate match score (higher = better match)
        if min_score <= score <= max_score:
            # Perfect match within range
            if difficulty in ['beginner']:
                return 1.0 - (score - min_score) / (max_score - min_score) * 0.3
            else:
                return 1.0 - abs(score - (min_score + max_score) / 2) / (max_score - min_score) * 0.5
        else:
            # Partial match outside range
            if score < min_score:
                return max(0.1, 1.0 - (min_score - score) / min_score)
            else:
                return max(0.1, 1.0 - (score - max_score) / 30)  # More forgiving for high scores
    
    def _calculate_progression_score(self, course: Dict, current_score: float) -> float:
        """Calculate how well a course fits the learner's progression"""
        difficulty = course.get('difficulty', 'beginner')
        
        # Calculate ideal progression
        if current_score < 60:
            ideal_difficulty = 'beginner'
            progression_bonus = 1.0
        elif current_score < 75:
            ideal_difficulty = 'intermediate'
            progression_bonus = 1.0
        elif current_score < 90:
            ideal_difficulty = 'advanced'
            progression_bonus = 0.9
        else:
            ideal_difficulty = 'expert'
            progression_bonus = 0.8
        
        base_score = 1.0 if difficulty == ideal_difficulty else 0.6
        
        # Bonus for appropriate progression
        difficulty_order = ['beginner', 'intermediate', 'advanced', 'expert']
        if difficulty in difficulty_order:
            current_index = difficulty_order.index(ideal_difficulty)
            course_index = difficulty_order.index(difficulty)
            if course_index <= current_index + 1:  # Allow one level ahead
                progression_bonus += 0.2
        
        return min(base_score * progression_bonus, 1.0)
    
    def _calculate_interest_score(self, course: Dict, preferences: List[str], learning_style: str) -> float:
        """Calculate interest-based match score"""
        score = 0.0
        
        # Subject matching
        course_subject = course.get('subject', '').lower()
        for pref in preferences:
            if pref in course_subject or course_subject in pref:
                score += 0.3
        
        # Tag matching
        course_tags = [tag.lower() for tag in course.get('tags', [])]
        for pref in preferences:
            if any(pref in tag for tag in course_tags):
                score += 0.2
        
        # Learning style matching
        content_type = course.get('content_type', '').lower()
        style_matches = {
            'Visual': ['video', 'interactive', 'infographic'],
            'Auditory': ['video', 'audio', 'discussion'],
            'Kinesthetic': ['interactive', 'project', 'assignment'],
            'Reading/Writing': ['article', 'assignment', 'quiz'],
            'Mixed': ['video', 'article', 'interactive', 'project']
        }
        
        preferred_types = style_matches.get(learning_style, ['video', 'article'])
        if content_type in preferred_types:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_gap_score(self, course: Dict, weak_areas: List[Tuple[str, float]]) -> float:
        """Calculate how well a course addresses performance gaps"""
        score = 0.0
        
        # Map weak areas to course subjects/tags
        course_subject = course.get('subject', '').lower()
        course_tags = [tag.lower() for tag in course.get('tags', [])]
        
        gap_keywords = {
            'test_score': ['assessment', 'exam', 'test', 'evaluation'],
            'quiz_score': ['quiz', 'practice', 'assessment', 'interactive'],
            'engagement_score': ['interactive', 'project', 'hands-on', 'practical'],
            'consistency_score': ['fundamentals', 'basics', 'structure', 'regular']
        }
        
        for component, weak_score in weak_areas:
            keywords = gap_keywords.get(component, [])
            
            # Check if course addresses this gap
            for keyword in keywords:
                if (keyword in course_subject or 
                    any(keyword in tag for tag in course_tags)):
                    gap_addressed = (70 - weak_score) / 70  # Higher score for more severe gaps
                    score += gap_addressed * 0.25
                    break
        
        return min(score, 1.0)
    
    def _check_prerequisites(self, prerequisites: List[str], learner_data: Dict) -> bool:
        """Check if learner has completed prerequisites"""
        if not prerequisites:
            return True
        
        learner_activities = learner_data.get('activities', [])
        completed_courses = []
        
        # Extract completed courses from activities
        for activity in learner_activities:
            if activity.get('activity_type') == 'course_completed':
                completed_courses.append(activity.get('course_id', '').lower())
        
        # Check if all prerequisites are met
        for prereq in prerequisites:
            if prereq.lower() not in completed_courses:
                return False
        
        return True
    
    def _generate_learning_path(self, learner_data: Dict, learner_score: Dict, 
                              recommendations: List[Dict]) -> Dict[str, Any]:
        """Generate a structured learning path"""
        if not recommendations:
            return {'error': 'No recommendations available for path generation'}
        
        path = {
            'pathway_name': f"{learner_score.get('performance_level', 'general').title()} Learning Path",
            'total_estimated_duration': 0,
            'courses': [],
            'milestones': [],
            'assessment_points': []
        }
        
        # Sort recommendations by match score and logical progression
        sorted_courses = sorted(recommendations, key=lambda x: x['match_score'], reverse=True)
        
        for i, rec in enumerate(sorted_courses[:6]):  # Top 6 courses for the path
            course = rec['course']
            
            course_info = {
                'sequence': i + 1,
                'course_id': course.get('id'),
                'title': course.get('title'),
                'difficulty': course.get('difficulty'),
                'duration': course.get('duration'),
                'reason': rec.get('reason', ''),
                'prerequisites_met': self._check_prerequisites(course.get('prerequisites', []), learner_data),
                'estimated_completion': f"Week {i + 1}"
            }
            
            path['courses'].append(course_info)
            path['total_estimated_duration'] += course.get('duration', 0)
            
            # Add milestone every 2 courses
            if (i + 1) % 2 == 0:
                path['milestones'].append({
                    'milestone': f"Complete {i + 1} courses",
                    'description': f"Assessment and review after completing {i + 1} courses",
                    'sequence': (i + 1) // 2
                })
            
            # Add assessment point every 3 courses
            if (i + 1) % 3 == 0:
                path['assessment_points'].append({
                    'assessment': f"Progress Check {((i + 1) // 3)}",
                    'description': f"Comprehensive assessment after {i + 1} courses",
                    'sequence': (i + 1) // 3
                })
        
        return path
    
    def _generate_recommendation_insights(self, learner_score: Dict, 
                                        recommendations: List[Dict]) -> List[str]:
        """Generate insights about the recommendations"""
        insights = []
        
        performance_level = learner_score.get('performance_level', 'new_learner')
        component_scores = learner_score.get('component_scores', {})
        
        # Performance-based insights
        if performance_level == 'excellent':
            insights.append("[STAR] Your excellent performance opens doors to advanced specialized content")
        elif performance_level in ['very_good', 'good']:
            insights.append("[GROWTH] Your solid performance qualifies you for intermediate and advanced courses")
        elif performance_level == 'average':
            insights.append("[POWER] Focus on strengthening fundamentals with our recommended beginner courses")
        else:
            insights.append("[TARGET] Personalized foundational content will help build your knowledge base")
        
        # Component-based insights
        test_score = component_scores.get('test_score', 0)
        quiz_score = component_scores.get('quiz_score', 0)
        engagement_score = component_scores.get('engagement_score', 0)
        
        if test_score < 60:
            insights.append("[NOTE] Recommended courses include more practice opportunities to improve test performance")
        
        if quiz_score < 60:
            insights.append("⚡ Interactive content and quick assessments will boost your quiz scores")
        
        if engagement_score < 50:
            insights.append("[GAME] Highly engaging, interactive courses recommended to increase participation")
        
        # Recommendation diversity
        if len(recommendations) > 5:
            insights.append("[EDU] Diverse course mix covering multiple subjects and skill levels")
        
        # Content type variety
        content_types = set([rec['course'].get('content_type') for rec in recommendations])
        if len(content_types) > 3:
            insights.append("[BOOK] Varied content types (videos, interactive, projects) to match different learning preferences")
        
        return insights
    
    def _identify_strengths(self, component_scores: Dict) -> List[str]:
        """Identify learner strengths based on component scores"""
        strengths = []
        
        for component, score in component_scores.items():
            if score >= 80:
                if component == 'test_score':
                    strengths.append("Strong test-taking abilities")
                elif component == 'quiz_score':
                    strengths.append("Excellent quick learning and recall")
                elif component == 'engagement_score':
                    strengths.append("High learning engagement and activity")
                elif component == 'consistency_score':
                    strengths.append("Consistent learning habits")
        
        return strengths
    
    def _identify_improvement_areas(self, component_scores: Dict) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        for component, score in component_scores.items():
            if score < 65:
                if component == 'test_score':
                    improvements.append("Test performance and concept retention")
                elif component == 'quiz_score':
                    improvements.append("Quick knowledge assessment and recall")
                elif component == 'engagement_score':
                    improvements.append("Learning activity and participation")
                elif component == 'consistency_score':
                    improvements.append("Regular learning schedule")
        
        return improvements
    
    def _get_score_focus(self, component_scores: Dict) -> str:
        """Get primary focus area based on lowest score"""
        if not component_scores:
            return "General skill building"
        
        min_score = min(component_scores.values())
        for component, score in component_scores.items():
            if score == min_score:
                if component == 'test_score':
                    return "Practice tests and concept reinforcement"
                elif component == 'quiz_score':
                    return "Quick assessments and interactive learning"
                elif component == 'engagement_score':
                    return "Hands-on projects and interactive content"
                elif component == 'consistency_score':
                    return "Structured learning schedule and routine"
        
        return "Balanced skill development"
    
    def _calculate_personalization_level(self, learner_score: Dict) -> str:
        """Calculate how personalized the recommendations are"""
        component_scores = learner_score.get('component_scores', {})
        
        # Count how many components have substantial data
        data_rich_components = sum(1 for score in component_scores.values() if score > 0)
        
        if data_rich_components >= 3:
            return "Highly Personalized"
        elif data_rich_components >= 2:
            return "Moderately Personalized"
        else:
            return "Basic Personalization"
    
    def _get_score_based_reason(self, performance_level: str, difficulty: str) -> str:
        """Get reason for score-based recommendation"""
        if performance_level == 'excellent':
            return f"Advanced {difficulty} content suitable for excellent performers"
        elif performance_level in ['very_good', 'good']:
            return f"Challenging {difficulty} content matched to your skill level"
        elif performance_level == 'average':
            return f"Skill-building {difficulty} content to enhance performance"
        else:
            return f"Foundational {difficulty} content to build core skills"
    
    def _get_interest_based_reason(self, course: Dict, preferences: List[str]) -> str:
        """Get reason for interest-based recommendation"""
        subject = course.get('subject', '')
        if preferences:
            return f"Matches your interests in {', '.join(preferences[:2])}"
        return f"Recommended based on your learning profile in {subject}"
    
    def _get_gap_based_reason(self, course: Dict, weak_areas: List[Tuple[str, float]]) -> str:
        """Get reason for gap-based recommendation"""
        subject = course.get('subject', '')
        if weak_areas:
            weak_components = [area[0].replace('_', ' ') for area in weak_areas[:2]]
            return f"Addresses performance gaps in {', '.join(weak_components)}"
        return f"Comprehensive {subject} content for skill development"

# Global recommendation engine instance
recommendation_engine = AdvancedRecommendationEngine()