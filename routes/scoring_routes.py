"""API routes for scoring and recommendations based on test marks"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from typing import Dict, Any
import traceback

# Import our scoring and recommendation modules
from ml.scoring_engine import get_learner_score_summary, ScoringEngine
from ml.score_based_recommender import get_score_based_recommendations, ScoreBasedRecommender
from models.test_result import TestResult, LearnerScoreSummary
from utils.crud_operations import (
    create_engagement, 
    read_learner, 
    read_learners,
    log_activity,
    read_engagements
)

# Create blueprint
scoring_bp = Blueprint('scoring', __name__, url_prefix='/api/scoring')

@scoring_bp.route('/test-result', methods=['POST'])
def submit_test_result():
    """Submit a test/quiz result and update learner scoring"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['learner_id', 'test_id', 'test_type', 'course_id', 'score', 'max_score']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required_fields': required_fields
            }), 400
        
        # Create TestResult object
        test_result = TestResult(
            learner_id=data['learner_id'],
            test_id=data['test_id'],
            test_type=data['test_type'],
            course_id=data['course_id'],
            content_id=data.get('content_id'),
            score=float(data['score']),
            max_score=float(data['max_score']),
            time_taken=data.get('time_taken'),
            attempts=data.get('attempts', 1),
            metadata=data.get('metadata', {})
        )
        
        # Log as engagement in the system
        engagement_data = {
            'learner_id': data['learner_id'],
            'content_id': data.get('content_id', data['test_id']),
            'course_id': data['course_id'],
            'engagement_type': f"{data['test_type']}_attempt",
            'duration': data.get('time_taken', 0),
            'score': test_result.percentage,
            'feedback': data.get('feedback'),
            'metadata': {
                'test_id': data['test_id'],
                'test_type': data['test_type'],
                'max_score': float(data['max_score']),
                'attempts': data.get('attempts', 1)
            }
        }
        
        # Create engagement record
        engagement = create_engagement(type('Engagement', (), engagement_data)())
        
        # Log activity for the learner
        activity_data = log_activity(
            learner_id=data['learner_id'],
            activity_type=f"{data['test_type']}_completed",
            duration=data.get('time_taken', 0),
            score=test_result.percentage
        )
        
        return jsonify({
            'success': True,
            'test_result': test_result.to_dict(),
            'engagement_created': True,
            'activity_logged': activity_data is not None,
            'message': f'Test result recorded successfully. Score: {test_result.percentage:.1f}%'
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to submit test result',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500

@scoring_bp.route('/learner/<learner_id>/score-summary', methods=['GET'])
def get_learner_score_summary_route(learner_id):
    """Get comprehensive score summary for a learner"""
    try:
        # Fetch test results from engagements (assuming test results are stored as engagements)
        engagements = read_engagements()
        test_engagements = [
            e for e in engagements 
            if e.get('learner_id') == learner_id 
            and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
        ]
        
        # Convert engagements to TestResult objects
        test_results = []
        for engagement in test_engagements:
            try:
                test_result = TestResult(
                    learner_id=engagement['learner_id'],
                    test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                    test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                    course_id=engagement['course_id'],
                    content_id=engagement['content_id'],
                    score=engagement.get('score', 0),
                    max_score=engagement.get('metadata', {}).get('max_score', 100),
                    time_taken=engagement.get('duration'),
                    attempts=engagement.get('metadata', {}).get('attempts', 1),
                    completed_at=engagement['timestamp']
                )
                test_results.append(test_result)
            except Exception as e:
                # Skip invalid engagements
                continue
        
        # Generate score summary
        score_summary = get_learner_score_summary(learner_id, test_results)
        
        return jsonify({
            'success': True,
            'learner_id': learner_id,
            'score_summary': score_summary.to_dict(),
            'total_test_results': len(test_results),
            'generated_at': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate score summary',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500

@scoring_bp.route('/learner/<learner_id>/recommendations', methods=['GET'])
def get_score_based_recommendations_route(learner_id):
    """Get course recommendations based on learner scoring"""
    try:
        # Get recommendations using our scoring system
        recommendations_data = get_score_based_recommendations(learner_id)
        
        if 'error' in recommendations_data:
            return jsonify(recommendations_data), 404
            
        return jsonify({
            'success': True,
            'recommendations': recommendations_data
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate recommendations',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500

@scoring_bp.route('/learner/<learner_id>/learning-path', methods=['GET'])
def get_learning_path_route(learner_id):
    """Get personalized learning path based on scoring analysis"""
    try:
        # Get current score summary
        engagements = read_engagements()
        test_engagements = [
            e for e in engagements 
            if e.get('learner_id') == learner_id 
            and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
        ]
        
        test_results = []
        for engagement in test_engagements:
            try:
                test_result = TestResult(
                    learner_id=engagement['learner_id'],
                    test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                    test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                    course_id=engagement['course_id'],
                    content_id=engagement['content_id'],
                    score=engagement.get('score', 0),
                    max_score=engagement.get('metadata', {}).get('max_score', 100),
                    time_taken=engagement.get('duration'),
                    attempts=engagement.get('metadata', {}).get('attempts', 1),
                    completed_at=engagement['timestamp']
                )
                test_results.append(test_result)
            except Exception:
                continue
        
        score_summary = get_learner_score_summary(learner_id, test_results)
        
        # Generate learning path
        recommender = ScoreBasedRecommender()
        learning_path = recommender.generate_learning_path(learner_id, score_summary)
        
        return jsonify({
            'success': True,
            'learner_id': learner_id,
            'learning_path': learning_path,
            'current_performance': {
                'level': score_summary.recommendation_level,
                'confidence': score_summary.confidence_score,
                'trend': score_summary.score_trend
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate learning path',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500

@scoring_bp.route('/batch-score-update', methods=['POST'])
def batch_update_scores():
    """Batch update scores for multiple learners (admin function)"""
    try:
        data = request.get_json()
        learner_ids = data.get('learner_ids', [])
        
        if not learner_ids:
            return jsonify({'error': 'No learner IDs provided'}), 400
        
        results = []
        for learner_id in learner_ids:
            try:
                # Generate score summary for each learner
                engagements = read_engagements()
                test_engagements = [
                    e for e in engagements 
                    if e.get('learner_id') == learner_id 
                    and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
                ]
                
                test_results = []
                for engagement in test_engagements:
                    try:
                        test_result = TestResult(
                            learner_id=engagement['learner_id'],
                            test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                            test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                            course_id=engagement['course_id'],
                            content_id=engagement['content_id'],
                            score=engagement.get('score', 0),
                            max_score=engagement.get('metadata', {}).get('max_score', 100),
                            time_taken=engagement.get('duration'),
                            attempts=engagement.get('metadata', {}).get('attempts', 1),
                            completed_at=engagement['timestamp']
                        )
                        test_results.append(test_result)
                    except Exception:
                        continue
                
                score_summary = get_learner_score_summary(learner_id, test_results)
                
                results.append({
                    'learner_id': learner_id,
                    'score_summary': score_summary.to_dict(),
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'learner_id': learner_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'processed_learners': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to batch update scores',
            'details': str(e)
        }), 500

@scoring_bp.route('/analytics/performance-trends', methods=['GET'])
def get_performance_analytics():
    """Get analytics on learner performance trends (admin function)"""
    try:
        # This would typically query your database for analytics
        # For now, return a placeholder response
        
        analytics = {
            'total_learners': len(read_learners()),
            'average_score_distribution': {
                'excellent_90_100': 0,  # Would calculate from data
                'good_80_89': 0,
                'satisfactory_70_79': 0,
                'needs_improvement_60_69': 0,
                'poor_below_60': 0
            },
            'most_common_recommendation_level': 'intermediate',
            'performance_trends': {
                'improving': 0,
                'stable': 0,
                'declining': 0
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'generated_at': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate analytics',
            'details': str(e)
        }), 500