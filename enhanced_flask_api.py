#!/usr/bin/env python3
"""
Enhanced Flask API server for Learning Agent with comprehensive scoring and recommendations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Import the scoring and recommendation systems
try:
    from enhanced_scoring_system import scoring_system
    from advanced_recommendation_engine import recommendation_engine
    from config.db_config import db
    from models.learner import Learner
    from utils.crud_operations import read_learners, read_learner
    SYSTEMS_LOADED = True
    DB_CONNECTED = True
except Exception as e:
    print(f"System loading failed: {e}")
    SYSTEMS_LOADED = False
    DB_CONNECTED = False

# API Error Handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler for the API"""
    print(f"API Error: {e}")
    traceback.print_exc()
    return jsonify({
        "error": "Internal server error",
        "message": str(e),
        "timestamp": datetime.utcnow().isoformat()
    }), 500

# Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    return jsonify({
        "status": "healthy",
        "systems_loaded": SYSTEMS_LOADED,
        "database_connected": DB_CONNECTED,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0-enhanced"
    })

# Learner Scoring Endpoints

@app.route('/api/learner/<learner_id>/score', methods=['GET'])
def get_learner_score(learner_id):
    """Get comprehensive learner score analysis"""
    try:
        # Get learner data
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        # Calculate comprehensive score
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        return jsonify(score_analysis)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to calculate learner score: {str(e)}",
            "learner_id": learner_id
        }), 500

@app.route('/api/learner/<learner_id>/score/history', methods=['GET'])
def get_score_history(learner_id):
    """Get learner score history (placeholder for future implementation)"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        # For now, return current score with mock history
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        
        # Generate mock historical data
        current_score = score_analysis.get('overall_score', 50)
        history = []
        for i in range(7):  # Last 7 days
            score_variation = (i - 3) * 2  # Simulate score changes
            history.append({
                "date": (datetime.now().date().fromordinal(datetime.now().date().toordinal() - i)).isoformat(),
                "score": max(0, min(100, current_score + score_variation)),
                "day": f"Day {7-i}"
            })
        
        return jsonify({
            "learner_id": learner_id,
            "current_score": current_score,
            "performance_level": score_analysis.get('performance_level', 'unknown'),
            "score_history": history,
            "trend": "improving" if history[0]['score'] < history[-1]['score'] else "stable"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get score history: {str(e)}",
            "learner_id": learner_id
        }), 500

# Course Recommendation Endpoints

@app.route('/api/learner/<learner_id>/recommendations', methods=['GET'])
def get_enhanced_recommendations(learner_id):
    """Get comprehensive course recommendations"""
    try:
        # Get learner data
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        # Calculate learner score
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        # Get comprehensive recommendations
        recommendation_count = request.args.get('count', 10, type=int)
        recommendations = recommendation_engine.get_comprehensive_recommendations(
            learner_data, score_analysis, recommendation_count
        )
        
        if "error" in recommendations:
            return jsonify(recommendations), 500
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate recommendations: {str(e)}",
            "learner_id": learner_id
        }), 500

@app.route('/api/learner/<learner_id>/recommendations/score-based', methods=['GET'])
def get_score_based_recommendations(learner_id):
    """Get recommendations based primarily on learner score"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        recommendation_count = request.args.get('count', 6, type=int)
        recommendations = recommendation_engine._score_based_recommendations(
            learner_data, score_analysis, recommendation_count
        )
        
        return jsonify({
            "learner_id": learner_id,
            "recommendations": recommendations,
            "algorithm": "score_based",
            "total_recommendations": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate score-based recommendations: {str(e)}",
            "learner_id": learner_id
        }), 500

@app.route('/api/learner/<learner_id>/recommendations/interest-based', methods=['GET'])
def get_interest_based_recommendations(learner_id):
    """Get recommendations based on learner interests"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        recommendation_count = request.args.get('count', 6, type=int)
        recommendations = recommendation_engine._interest_matching_recommendations(
            learner_data, score_analysis, recommendation_count
        )
        
        return jsonify({
            "learner_id": learner_id,
            "recommendations": recommendations,
            "algorithm": "interest_matching",
            "total_recommendations": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate interest-based recommendations: {str(e)}",
            "learner_id": learner_id
        }), 500

@app.route('/api/learner/<learner_id>/learning-path', methods=['GET'])
def get_learning_path(learner_id):
    """Get personalized learning path"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        # Get recommendations for path generation
        recommendations = recommendation_engine.get_comprehensive_recommendations(
            learner_data, score_analysis, 6
        )
        
        if "error" in recommendations:
            return jsonify(recommendations), 500
        
        learning_path = recommendations.get('learning_path', {})
        
        return jsonify({
            "learner_id": learner_id,
            "learning_path": learning_path,
            "score_analysis": score_analysis,
            "path_generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate learning path: {str(e)}",
            "learner_id": learner_id
        }), 500

# Analytics and Comparison Endpoints

@app.route('/api/analytics/learners', methods=['GET'])
def get_learner_analytics():
    """Get analytics for all learners"""
    try:
        learners = read_learners()
        if not learners:
            return jsonify({"message": "No learners found"})
        
        # Calculate scores for all learners
        learner_scores = []
        for learner in learners:
            try:
                score = scoring_system.calculate_learner_score(learner)
                if "error" not in score:
                    learner_scores.append(score)
            except Exception as e:
                print(f"Error calculating score for learner {learner.get('id', 'unknown')}: {e}")
                continue
        
        if not learner_scores:
            return jsonify({"error": "No valid learner scores calculated"})
        
        # Get comparison data
        comparison = scoring_system.compare_learners(learner_scores)
        
        # Generate additional analytics
        performance_levels = {}
        avg_scores = []
        
        for score_data in learner_scores:
            level = score_data.get('performance_level', 'unknown')
            performance_levels[level] = performance_levels.get(level, 0) + 1
            avg_scores.append(score_data.get('overall_score', 0))
        
        analytics = {
            "total_learners": len(learner_scores),
            "learners_with_scores": len(learner_scores),
            "average_score": sum(avg_scores) / len(avg_scores) if avg_scores else 0,
            "score_distribution": {
                "highest": max(avg_scores) if avg_scores else 0,
                "lowest": min(avg_scores) if avg_scores else 0,
                "median": sorted(avg_scores)[len(avg_scores)//2] if avg_scores else 0
            },
            "performance_levels": performance_levels,
            "detailed_comparison": comparison,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate learner analytics: {str(e)}"
        }), 500

@app.route('/api/analytics/performance-insights', methods=['GET'])
def get_performance_insights():
    """Get performance insights across all learners"""
    try:
        learners = read_learners()
        if not learners:
            return jsonify({"message": "No learners found"})
        
        # Analyze component scores across all learners
        all_test_scores = []
        all_quiz_scores = []
        all_engagement_scores = []
        all_consistency_scores = []
        
        for learner in learners:
            try:
                score = scoring_system.calculate_learner_score(learner)
                if "error" not in score:
                    components = score.get('component_scores', {})
                    all_test_scores.append(components.get('test_score', 0))
                    all_quiz_scores.append(components.get('quiz_score', 0))
                    all_engagement_scores.append(components.get('engagement_score', 0))
                    all_consistency_scores.append(components.get('consistency_score', 0))
            except:
                continue
        
        insights = {
            "component_analysis": {
                "test_scores": {
                    "average": sum(all_test_scores) / len(all_test_scores) if all_test_scores else 0,
                    "median": sorted(all_test_scores)[len(all_test_scores)//2] if all_test_scores else 0,
                    "distribution": len([s for s in all_test_scores if s >= 80]) / len(all_test_scores) * 100 if all_test_scores else 0
                },
                "quiz_scores": {
                    "average": sum(all_quiz_scores) / len(all_quiz_scores) if all_quiz_scores else 0,
                    "median": sorted(all_quiz_scores)[len(all_quiz_scores)//2] if all_quiz_scores else 0,
                    "distribution": len([s for s in all_quiz_scores if s >= 80]) / len(all_quiz_scores) * 100 if all_quiz_scores else 0
                },
                "engagement_scores": {
                    "average": sum(all_engagement_scores) / len(all_engagement_scores) if all_engagement_scores else 0,
                    "median": sorted(all_engagement_scores)[len(all_engagement_scores)//2] if all_engagement_scores else 0,
                    "distribution": len([s for s in all_engagement_scores if s >= 80]) / len(all_engagement_scores) * 100 if all_engagement_scores else 0
                },
                "consistency_scores": {
                    "average": sum(all_consistency_scores) / len(all_consistency_scores) if all_consistency_scores else 0,
                    "median": sorted(all_consistency_scores)[len(all_consistency_scores)//2] if all_consistency_scores else 0,
                    "distribution": len([s for s in all_consistency_scores if s >= 80]) / len(all_consistency_scores) * 100 if all_consistency_scores else 0
                }
            },
            "recommendations": [
                "Focus on improving test performance across all learners",
                "Enhance engagement through interactive content",
                "Develop consistency tracking and reminder systems",
                "Implement personalized learning paths based on performance gaps"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate performance insights: {str(e)}"
        }), 500

# Course Catalog Endpoints

@app.route('/api/courses', methods=['GET'])
def get_course_catalog():
    """Get the complete course catalog"""
    try:
        catalog = recommendation_engine.course_catalog
        
        # Allow filtering by parameters
        subject_filter = request.args.get('subject')
        difficulty_filter = request.args.get('difficulty')
        content_type_filter = request.args.get('content_type')
        
        filtered_catalog = catalog
        
        if subject_filter:
            filtered_catalog = [c for c in filtered_catalog 
                              if c.get('subject', '').lower() == subject_filter.lower()]
        
        if difficulty_filter:
            filtered_catalog = [c for c in filtered_catalog 
                              if c.get('difficulty', '').lower() == difficulty_filter.lower()]
        
        if content_type_filter:
            filtered_catalog = [c for c in filtered_catalog 
                              if c.get('content_type', '').lower() == content_type_filter.lower()]
        
        return jsonify({
            "courses": filtered_catalog,
            "total_courses": len(filtered_catalog),
            "filters_applied": {
                "subject": subject_filter,
                "difficulty": difficulty_filter,
                "content_type": content_type_filter
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get course catalog: {str(e)}"
        }), 500

@app.route('/api/courses/<course_id>', methods=['GET'])
def get_course_details(course_id):
    """Get detailed information about a specific course"""
    try:
        catalog = recommendation_engine.course_catalog
        course = next((c for c in catalog if c.get('id') == course_id), None)
        
        if not course:
            return jsonify({"error": f"Course {course_id} not found"}), 404
        
        return jsonify({
            "course": course,
            "found": True
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get course details: {str(e)}"
        }), 500

# Batch Operations Endpoints

@app.route('/api/batch/calculate-scores', methods=['POST'])
def batch_calculate_scores():
    """Calculate scores for multiple learners in batch"""
    try:
        data = request.get_json()
        if not data or 'learner_ids' not in data:
            return jsonify({"error": "learner_ids required in request body"}), 400
        
        learner_ids = data['learner_ids']
        results = []
        
        for learner_id in learner_ids:
            try:
                learner_data = read_learner(learner_id)
                if learner_data:
                    score = scoring_system.calculate_learner_score(learner_data)
                    results.append({
                        "learner_id": learner_id,
                        "success": "error" not in score,
                        "score_data": score
                    })
                else:
                    results.append({
                        "learner_id": learner_id,
                        "success": False,
                        "error": "Learner not found"
                    })
            except Exception as e:
                results.append({
                    "learner_id": learner_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = len([r for r in results if r['success']])
        
        return jsonify({
            "batch_results": results,
            "total_requested": len(learner_ids),
            "successful_calculations": successful,
            "failed_calculations": len(learner_ids) - successful,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Batch score calculation failed: {str(e)}"
        }), 500

@app.route('/api/batch/generate-recommendations', methods=['POST'])
def batch_generate_recommendations():
    """Generate recommendations for multiple learners in batch"""
    try:
        data = request.get_json()
        if not data or 'learner_ids' not in data:
            return jsonify({"error": "learner_ids required in request body"}), 400
        
        learner_ids = data['learner_ids']
        recommendation_count = data.get('count', 5)
        results = []
        
        for learner_id in learner_ids:
            try:
                learner_data = read_learner(learner_id)
                if learner_data:
                    score = scoring_system.calculate_learner_score(learner_data)
                    if "error" not in score:
                        recommendations = recommendation_engine.get_comprehensive_recommendations(
                            learner_data, score, recommendation_count
                        )
                        results.append({
                            "learner_id": learner_id,
                            "success": "error" not in recommendations,
                            "recommendations_data": recommendations
                        })
                    else:
                        results.append({
                            "learner_id": learner_id,
                            "success": False,
                            "error": "Score calculation failed"
                        })
                else:
                    results.append({
                        "learner_id": learner_id,
                        "success": False,
                        "error": "Learner not found"
                    })
            except Exception as e:
                results.append({
                    "learner_id": learner_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = len([r for r in results if r['success']])
        
        return jsonify({
            "batch_results": results,
            "total_requested": len(learner_ids),
            "successful_generations": successful,
            "failed_generations": len(learner_ids) - successful,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Batch recommendation generation failed: {str(e)}"
        }), 500

# Legacy API endpoints for backward compatibility

@app.route('/api/learners', methods=['GET'])
def get_learners():
    """Get all learners (legacy endpoint)"""
    try:
        if DB_CONNECTED and SYSTEMS_LOADED:
            learners = read_learners()
            if learners:
                return jsonify({
                    "learners": learners,
                    "count": len(learners),
                    "version": "2.0-enhanced"
                })
        
        # Return sample data if no database connection
        sample_learners = [
            {
                "id": "demo-alice-123",
                "name": "Alice Johnson",
                "age": 28,
                "gender": "Female",
                "learning_style": "Visual",
                "preferences": ["Data Science", "Machine Learning", "Python"],
                "activity_count": 3,
                "activities": [
                    {"activity_type": "module_completed", "timestamp": "2024-01-15T10:00:00", "score": 95},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 88},
                    {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 92}
                ]
            },
            {
                "id": "demo-bob-456", 
                "name": "Bob Smith",
                "age": 35,
                "gender": "Male",
                "learning_style": "Kinesthetic",
                "preferences": ["Web Development", "JavaScript", "React"],
                "activity_count": 2,
                "activities": [
                    {"activity_type": "project_completed", "timestamp": "2024-01-14T16:45:00", "score": 85},
                    {"activity_type": "code_review", "timestamp": "2024-01-18T11:20:00", "score": 90}
                ]
            },
            {
                "id": "demo-carol-789",
                "name": "Carol Davis",
                "age": 22,
                "gender": "Female", 
                "learning_style": "Auditory",
                "preferences": ["Design", "UX/UI", "Figma"],
                "activity_count": 1,
                "activities": [
                    {"activity_type": "portfolio_submitted", "timestamp": "2024-01-19T13:30:00", "score": 96}
                ]
            }
        ]
        
        return jsonify({
            "learners": sample_learners,
            "count": len(sample_learners),
            "sample_data": True,
            "version": "2.0-enhanced"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch learners: {str(e)}",
            "learners": [],
            "count": 0
        }), 500

@app.route('/api/learner/<learner_id>/legacy-recommendations', methods=['GET'])
def get_legacy_recommendations(learner_id):
    """Legacy recommendations endpoint for backward compatibility"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return jsonify({"error": f"Learner {learner_id} not found"}), 404
        
        # Generate comprehensive recommendations using new system
        score_analysis = scoring_system.calculate_learner_score(learner_data)
        if "error" in score_analysis:
            return jsonify(score_analysis), 500
        
        recommendations = recommendation_engine.get_comprehensive_recommendations(
            learner_data, score_analysis, 5
        )
        
        # Convert to legacy format
        legacy_format = {
            "learner_id": learner_id,
            "is_new_learner": False,
            "recommendations": [
                {
                    "course_id": rec['course'].get('id', ''),
                    "title": rec['course'].get('title', ''),
                    "description": rec['course'].get('description', ''),
                    "subject": rec['course'].get('subject', ''),
                    "difficulty": rec['course'].get('difficulty', ''),
                    "content_type": rec['course'].get('content_type', ''),
                    "duration": rec['course'].get('duration', 0),
                    "tags": rec['course'].get('tags', []),
                    "reason": rec.get('reason', 'Recommended based on your profile'),
                    "confidence": rec.get('match_score', 0.5),
                    "learning_style_match": learner_data.get('learning_style', 'Mixed'),
                    "preference_match": True
                }
                for rec in recommendations.get('recommendations', [])
            ],
            "recommendation_type": "enhanced",
            "learning_profile": {
                "preferences": learner_data.get('preferences', []),
                "learning_style": learner_data.get('learning_style', 'Mixed'),
                "avg_score": score_analysis.get('overall_score', 0),
                "performance_level": score_analysis.get('performance_level', 'unknown')
            },
            "insights": recommendations.get('insights', []),
            "version": "2.0-enhanced"
        }
        
        return jsonify(legacy_format)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate legacy recommendations: {str(e)}",
            "learner_id": learner_id
        }), 500

if __name__ == '__main__':
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        import locale
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Starting Enhanced Learning Agent API Server...")
    print("New Features:")
    print("  - Advanced scoring system with component analysis")
    print("  - Comprehensive course recommendations") 
    print("  - Learning path generation")
    print("  - Batch operations support")
    print("  - Performance analytics and insights")
    print("  - Enhanced error handling")
    print("  - Content management with metadata")
    print("  - Engagement tracking with interaction metrics")
    print("\nAPI Endpoints:")
    print("  Health Check: http://localhost:5001/api/health")
    print("  Learner Score: http://localhost:5001/api/learner/<id>/score")
    print("  Enhanced Recommendations: http://localhost:5001/api/learner/<id>/recommendations")
    print("  Learning Path: http://localhost:5001/api/learner/<id>/learning-path")
    print("  Analytics: http://localhost:5001/api/analytics/learners")
    print("  Course Catalog: http://localhost:5001/api/courses")
    print("  Content Management: http://localhost:5001/api/content")
    print("  Engagement Tracking: http://localhost:5001/api/engagement")
    
    app.run(
        host='0.0.0.0',
        port=5001,  # Using different port to avoid conflicts
        debug=True,
        use_reloader=False  # Prevent duplicate loading in debug mode
    )