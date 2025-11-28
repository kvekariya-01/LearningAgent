from flask import Blueprint, request, jsonify
import logging
from utils.crud_operations import (
    create_engagement, read_engagement, read_engagements, update_engagement, delete_engagement,
    get_engagement_metrics, update_engagement_metrics
)
from utils.schemas import (
    validate_engagement_data, validate_engagement_update_data
)
from utils.response import success, error
from models.engagement import Engagement

# Configure logging
logger = logging.getLogger(__name__)

# Try to import marshmallow's ValidationError (preferred)
try:
    from marshmallow import ValidationError
except Exception:
    # Fallback ValidationError if marshmallow is not installed or unresolved by static analysis
    class ValidationError(Exception):
        """Fallback ValidationError used when marshmallow is unavailable."""
        def __init__(self, messages=None):
            super().__init__(messages)
            # Keep the .messages attribute to match code that expects e.messages
            self.messages = messages

engagement_bp = Blueprint("engagement_bp", __name__, url_prefix="/api")

# Engagement CRUD Operations
@engagement_bp.route("/engagement", methods=["POST"])
def create_engagement_route():
    """Create new engagement with comprehensive interaction metrics"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_engagement_data(data)
        engagement = Engagement(**validated_data)
        result = create_engagement(engagement)

        if not result:
            return error("Failed to create engagement", 500)

        return success(result.to_dict(), "Engagement created successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagement/<id>", methods=["GET"])
def get_engagement(id):
    """Get engagement by ID with metrics"""
    try:
        engagement = read_engagement(id)
        if not engagement:
            return error("Engagement not found", 404)

        return success(engagement.to_dict(), "Engagement retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagement/<id>", methods=["PUT"])
def update_engagement_route(id):
    """Update engagement with metrics validation"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_engagement_update_data(data)
        result = update_engagement(id, validated_data)

        if not result:
            return error("Engagement not found or update failed", 404)

        return success(result, "Engagement updated successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagement/<id>", methods=["DELETE"])
def delete_engagement_route(id):
    """Delete engagement"""
    try:
        result = delete_engagement(id)
        if not result:
            return error("Engagement not found", 404)

        return success(None, "Engagement deleted successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagements", methods=["GET"])
def list_engagements():
    """List all engagements with filtering"""
    try:
        # Get query parameters for filtering
        learner_id = request.args.get('learner_id')
        content_id = request.args.get('content_id')
        course_id = request.args.get('course_id')
        engagement_type = request.args.get('engagement_type')

        # Start with all engagements
        engagements = read_engagements()

        # Apply filters if provided
        if learner_id:
            engagements = [e for e in engagements if e.learner_id == learner_id]
        if content_id:
            engagements = [e for e in engagements if e.content_id == content_id]
        if course_id:
            engagements = [e for e in engagements if e.course_id == course_id]
        if engagement_type:
            engagements = [e for e in engagements if e.engagement_type == engagement_type]

        return success({
            "engagements": [e.to_dict() for e in engagements],
            "total": len(engagements),
            "filters_applied": {
                "learner_id": learner_id,
                "content_id": content_id,
                "course_id": course_id,
                "engagement_type": engagement_type
            }
        }, "Engagements retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Engagement Metrics Operations
@engagement_bp.route("/engagement/<id>/metrics", methods=["GET"])
def get_engagement_metrics_route(id):
    """Get engagement interaction metrics"""
    try:
        engagement = read_engagement(id)
        if not engagement:
            return error("Engagement not found", 404)

        interaction_metrics = engagement.interaction_metrics.model_dump() if engagement.interaction_metrics else {}
        engagement_pattern = engagement.engagement_pattern.model_dump() if engagement.engagement_pattern else {}
        
        return success({
            "engagement_id": id,
            "interaction_metrics": interaction_metrics,
            "engagement_pattern": engagement_pattern
        }, "Engagement metrics retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagement/<id>/metrics", methods=["PUT"])
def update_engagement_metrics_route(id):
    """Update engagement interaction metrics"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        # Update metrics
        result = update_engagement(id, {"interaction_metrics": data})
        if not result:
            return error("Engagement not found or update failed", 404)

        return success({
            "engagement_id": id,
            "interaction_metrics": result.get('interaction_metrics', {})
        }, "Engagement metrics updated successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Learner Engagement Analytics
@engagement_bp.route("/learner/<learner_id>/engagements", methods=["GET"])
def get_learner_engagements(learner_id):
    """Get all engagements for a learner with analytics"""
    try:
        engagements = read_engagements()
        learner_engagements = [e for e in engagements if e.learner_id == learner_id]
        
        # Calculate analytics
        total_engagements = len(learner_engagements)
        avg_duration = 0
        engagement_types = {}
        
        if learner_engagements:
            durations = [e.duration for e in learner_engagements if e.duration]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            for engagement in learner_engagements:
                etype = engagement.engagement_type
                engagement_types[etype] = engagement_types.get(etype, 0) + 1
        
        return success({
            "learner_id": learner_id,
            "total_engagements": total_engagements,
            "average_duration": round(avg_duration, 2),
            "engagement_types": engagement_types,
            "engagements": [e.to_dict() for e in learner_engagements]
        }, "Learner engagements retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/learner/<learner_id>/engagement-metrics", methods=["GET"])
def get_learner_engagement_metrics(learner_id):
    """Get comprehensive engagement metrics for learner"""
    try:
        metrics = get_engagement_metrics(learner_id)
        
        if not metrics:
            return error("No engagement data found for learner", 404)
        
        # Aggregate metrics
        total_sessions = len(metrics)
        high_engagement = 0
        medium_engagement = 0
        low_engagement = 0
        
        for metric in metrics:
            completion = metric.get('metrics', {}).get('completion_percentage', 0)
            if completion > 0.8:
                high_engagement += 1
            elif completion > 0.5:
                medium_engagement += 1
            else:
                low_engagement += 1
        
        return success({
            "learner_id": learner_id,
            "total_sessions": total_sessions,
            "engagement_distribution": {
                "high": high_engagement,
                "medium": medium_engagement,
                "low": low_engagement
            },
            "detailed_metrics": metrics
        }, "Learner engagement metrics retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Engagement Analytics
@engagement_bp.route("/content/<content_id>/engagements", methods=["GET"])
def get_content_engagements(content_id):
    """Get all engagements for a content"""
    try:
        engagements = read_engagements()
        content_engagements = [e for e in engagements if e.content_id == content_id]
        
        return success({
            "content_id": content_id,
            "total_engagements": len(content_engagements),
            "engagements": [e.to_dict() for e in content_engagements]
        }, "Content engagements retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Real-time Engagement Tracking
@engagement_bp.route("/engagement/track", methods=["POST"])
def track_engagement():
    """Track real-time engagement with interaction metrics"""
    try:
        data = request.get_json()
        if not data:
            return error("No engagement data provided", 400)

        required_fields = ['learner_id', 'content_id', 'course_id', 'engagement_type']
        for field in required_fields:
            if field not in data:
                return error(f"Missing required field: {field}", 400)

        # Create engagement with interaction metrics
        validated_data = validate_engagement_data(data)
        engagement = Engagement(**validated_data)
        result = create_engagement(engagement)

        if not result:
            return error("Failed to track engagement", 500)

        return success({
            "engagement_id": result['id'],
            "tracking_status": "success"
        }, "Engagement tracked successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@engagement_bp.route("/engagement/<id>/interaction", methods=["POST"])
def update_interaction_metrics(id):
    """Update real-time interaction metrics"""
    try:
        data = request.get_json()
        if not data:
            return error("No interaction data provided", 400)

        # Expected metrics
        interaction_data = {
            "click_count": data.get("click_count", 0),
            "scroll_depth": data.get("scroll_depth", 0.0),
            "pause_count": data.get("pause_count", 0),
            "replay_count": data.get("replay_count", 0),
            "completion_percentage": data.get("completion_percentage", 0.0),
            "attention_span": data.get("attention_span", 0.0),
            "interaction_frequency": data.get("interaction_frequency", 0.0),
            "device_type": data.get("device_type", "unknown"),
            "browser_type": data.get("browser_type", "unknown")
        }

        result = update_engagement_metrics(None, None, interaction_data)
        if not result:
            # If engagement ID specific update fails, try direct update
            result = update_engagement(id, {"interaction_metrics": interaction_data})
            
        if not result:
            return error("Engagement not found or update failed", 404)

        return success({
            "engagement_id": id,
            "interaction_metrics": result.get('interaction_metrics', {})
        }, "Interaction metrics updated successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Engagement Pattern Analysis
@engagement_bp.route("/learner/<learner_id>/engagement-patterns", methods=["GET"])
def analyze_engagement_patterns(learner_id):
    """Analyze engagement patterns for a learner"""
    try:
        metrics = get_engagement_metrics(learner_id)
        
        if not metrics:
            return error("No engagement data found", 404)
        
        # Pattern analysis
        patterns = {
            "session_frequency": "daily",  # Could be calculated from timestamps
            "engagement_consistency": 0.8,  # Could be calculated from consistency_score
            "preferred_content_types": {},
            "optimal_study_times": [],
            "completion_rates": {}
        }
        
        # Analyze content types and completion rates
        for metric in metrics:
            engagement_data = metric.get('metrics', {})
            # This would involve more complex analysis in a real implementation
            
        return success({
            "learner_id": learner_id,
            "pattern_analysis": patterns,
            "raw_metrics": metrics
        }, "Engagement pattern analysis completed")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Engagement History
@engagement_bp.route("/learner/<learner_id>/engagement-history", methods=["GET"])
def get_engagement_history(learner_id):
    """Get comprehensive engagement history for learner"""
    try:
        engagements = read_engagements()
        learner_engagements = [e for e in engagements if e.learner_id == learner_id]
        
        # Sort by timestamp
        learner_engagements.sort(key=lambda x: x.timestamp, reverse=True)
        
        return success({
            "learner_id": learner_id,
            "total_engagements": len(learner_engagements),
            "engagement_history": [e.to_dict() for e in learner_engagements]
        }, "Engagement history retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)