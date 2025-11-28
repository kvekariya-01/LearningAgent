#!/usr/bin/env python3
"""
Flask API server for Learning Agent recommendations
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Import the same functions as the Streamlit app
try:
    from config.db_config import db
    from models.learner import Learner
    from utils.crud_operations import read_learners, read_learner
    DB_CONNECTED = True
except Exception as e:
    print(f"Database connection failed: {e}")
    DB_CONNECTED = False

# Import routes
try:
    from routes.scoring_routes import scoring_bp
    app.register_blueprint(scoring_bp)
    SCORING_ENABLED = True
except Exception as e:
    print(f"Scoring routes import failed: {e}")
    SCORING_ENABLED = False

try:
    from routes.content_routes import content_bp
    app.register_blueprint(content_bp)
    CONTENT_ENABLED = True
except Exception as e:
    print(f"Content routes import failed: {e}")
    CONTENT_ENABLED = False

try:
    from routes.engagement_routes import engagement_bp
    app.register_blueprint(engagement_bp)
    ENGAGEMENT_ENABLED = True
except Exception as e:
    print(f"Engagement routes import failed: {e}")
    ENGAGEMENT_ENABLED = False

def generate_local_recommendations(learner_id):
    """Generate local recommendations when API is not available"""
    try:
        # For demo purposes, return sample recommendations
        return {
            "learner_id": learner_id,
            "is_new_learner": False,
            "recommendations": [
                {
                    "course_id": "python-101",
                    "title": "Introduction to Python Programming",
                    "description": "Learn the basics of Python programming including variables, loops, and functions.",
                    "subject": "Programming",
                    "difficulty": "beginner",
                    "content_type": "video",
                    "duration": 120,
                    "tags": ["python", "programming", "basics"],
                    "reason": "Matches your preferences for programming and Python",
                    "confidence": 0.9,
                    "learning_style_match": "Visual",
                    "preference_match": True
                },
                {
                    "course_id": "data-science-intro",
                    "title": "Data Science Fundamentals",
                    "description": "Introduction to data science concepts, tools, and techniques.",
                    "subject": "Data Science",
                    "difficulty": "beginner",
                    "content_type": "article",
                    "duration": 90,
                    "tags": ["data", "science", "statistics", "analysis"],
                    "reason": "Related to your interest in data science and machine learning",
                    "confidence": 0.8,
                    "learning_style_match": "Visual",
                    "preference_match": True
                }
            ],
            "recommendation_type": "hybrid",
            "learning_profile": {
                "preferences": ["Python", "Data Science", "Machine Learning"],
                "learning_style": "Visual",
                "avg_score": 87.5,
                "total_study_time": 180,
                "total_activities": 5,
                "recommended_subjects": ["Programming", "Data Science"]
            },
            "insights": [
                "Your learning style: Visual",
                "Preferred content types: Video, Article",
                "Performance level: Good",
                "Study consistency: Regular"
            ]
        }
    except Exception as e:
        return {
            "error": f"Failed to generate recommendations: {str(e)}",
            "recommendations": []
        }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "database_connected": DB_CONNECTED,
        "scoring_enabled": SCORING_ENABLED if 'SCORING_ENABLED' in globals() else False,
        "content_enabled": CONTENT_ENABLED if 'CONTENT_ENABLED' in globals() else False,
        "engagement_enabled": ENGAGEMENT_ENABLED if 'ENGAGEMENT_ENABLED' in globals() else False,
        "features": {
            "basic_recommendations": True,
            "score_based_recommendations": SCORING_ENABLED if 'SCORING_ENABLED' in globals() else False,
            "learning_paths": SCORING_ENABLED if 'SCORING_ENABLED' in globals() else False,
            "performance_analytics": SCORING_ENABLED if 'SCORING_ENABLED' in globals() else False,
            "content_management": CONTENT_ENABLED if 'CONTENT_ENABLED' in globals() else False,
            "engagement_tracking": ENGAGEMENT_ENABLED if 'ENGAGEMENT_ENABLED' in globals() else False
        }
    })

@app.route('/api/learner/<learner_id>/recommendations', methods=['GET'])
def get_recommendations(learner_id):
    """Get personalized recommendations for a learner"""
    try:
        # First try to get from database
        if DB_CONNECTED:
            learner_data = read_learner(learner_id)
            if learner_data:
                recommendations = generate_local_recommendations(learner_id)
                return jsonify(recommendations)
        
        # If no database connection or learner not found, use sample data
        print(f"Using sample data for learner: {learner_id}")
        sample_learner = {
            "id": learner_id,
            "name": "Demo Learner",
            "age": 25,
            "gender": "Other",
            "learning_style": "Visual",
            "preferences": ["Python", "Data Science", "Machine Learning"],
            "activity_count": 2,
            "activities": [
                {"activity_type": "module_completed", "timestamp": "2024-01-15T10:00:00", "score": 90},
                {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 85}
            ]
        }
        
        recommendations = generate_local_recommendations(learner_id)
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify({
            "error": str(e),
            "recommendations": [],
            "fallback": True
        }), 500

@app.route('/api/learners', methods=['GET'])
def get_learners():
    """Get all learners"""
    try:
        if DB_CONNECTED:
            learners = read_learners()
            if learners:
                return jsonify({
                    "learners": learners,
                    "count": len(learners)
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
            "sample_data": True
        })
        
    except Exception as e:
        print(f"Error fetching learners: {e}")
        return jsonify({
            "error": str(e),
            "learners": [],
            "count": 0
        }), 500

if __name__ == '__main__':
    print("Starting Learning Agent API Server...")
    print("API will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("Recommendations: http://localhost:5000/api/learner/<id>/recommendations")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Prevent duplicate loading in debug mode
    )