from flask import Blueprint, request, jsonify
import logging
from utils.crud_operations import (
    create_content, read_content, read_contents, update_content, delete_content,
    search_content_by_criteria, bulk_create_content
)
from utils.schemas import (
    validate_content_data, validate_content_update_data, validate_analytics_query_data
)
from utils.response import success, error
from models.content import Content

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

content_bp = Blueprint("content_bp", __name__, url_prefix="/api")

# Content CRUD Operations
@content_bp.route("/content", methods=["POST"])
def create_content_route():
    """Create new content with comprehensive metadata"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_content_data(data)
        content = Content(**validated_data)
        result = create_content(content)

        if not result:
            return error("Failed to create content", 500)

        return success(result, "Content created successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@content_bp.route("/content/<id>", methods=["GET"])
def get_content(id):
    """Get content by ID with metadata"""
    try:
        content = read_content(id)
        if not content:
            return error("Content not found", 404)

        return success(content, "Content retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@content_bp.route("/content/<id>", methods=["PUT"])
def update_content_route(id):
    """Update content with metadata validation"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_content_update_data(data)
        result = update_content(id, validated_data)

        if not result:
            return error("Content not found or update failed", 404)

        return success(result, "Content updated successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@content_bp.route("/content/<id>", methods=["DELETE"])
def delete_content_route(id):
    """Delete content"""
    try:
        result = delete_content(id)
        if not result:
            return error("Content not found", 404)

        return success(None, "Content deleted successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@content_bp.route("/contents", methods=["GET"])
def list_contents():
    """List all content with filtering options"""
    try:
        # Get query parameters for filtering
        course_id = request.args.get('course_id')
        content_type = request.args.get('content_type')
        difficulty_level = request.args.get('difficulty_level')
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None

        # Start with all content
        contents = read_contents()

        # Apply filters if provided
        if course_id:
            contents = [c for c in contents if c.get('course_id') == course_id]
        if content_type:
            contents = [c for c in contents if c.get('content_type') == content_type]
        if difficulty_level:
            contents = [c for c in contents if c.get('difficulty_level') == difficulty_level]
        if tags:
            contents = [c for c in contents if any(tag.lower() in [t.lower() for t in c.get('tags', [])] for tag in tags)]

        return success({
            "contents": contents,
            "total": len(contents),
            "filters_applied": {
                "course_id": course_id,
                "content_type": content_type,
                "difficulty_level": difficulty_level,
                "tags": tags
            }
        }, "Contents retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Metadata Operations
@content_bp.route("/content/<id>/metadata", methods=["GET"])
def get_content_metadata(id):
    """Get content metadata specifically"""
    try:
        content = read_content(id)
        if not content:
            return error("Content not found", 404)

        metadata = content.get('metadata', {})
        return success({
            "content_id": id,
            "metadata": metadata
        }, "Content metadata retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@content_bp.route("/content/<id>/metadata", methods=["PUT"])
def update_content_metadata(id):
    """Update content metadata"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        # Validate metadata fields
        validated_metadata = validate_content_update_data({"metadata": data})['metadata']
        
        result = update_content(id, {"metadata": validated_metadata})
        if not result:
            return error("Content not found or update failed", 404)

        return success({
            "content_id": id,
            "metadata": result.get('metadata', {})
        }, "Content metadata updated successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Search and Discovery
@content_bp.route("/content/search", methods=["POST"])
def search_content():
    """Advanced content search with multiple criteria"""
    try:
        data = request.get_json()
        if not data:
            return error("No search criteria provided", 400)

        # Build search criteria
        criteria = {}
        if data.get('difficulty_level'):
            criteria['difficulty_level'] = data['difficulty_level']
        if data.get('content_type'):
            criteria['content_type'] = data['content_type']
        if data.get('tags'):
            criteria['tags'] = data['tags']
        if data.get('course_id'):
            criteria['course_id'] = data['course_id']

        results = search_content_by_criteria(criteria)
        
        return success({
            "results": results,
            "total_found": len(results),
            "search_criteria": criteria
        }, "Content search completed successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Analytics
@content_bp.route("/content/<id>/analytics", methods=["GET"])
def get_content_analytics(id):
    """Get content usage analytics"""
    try:
        content = read_content(id)
        if not content:
            return error("Content not found", 404)

        # This would typically involve complex analytics queries
        # For now, returning basic content info
        analytics = {
            "content_id": id,
            "title": content.get('title'),
            "metadata": content.get('metadata', {}),
            "difficulty_level": content.get('difficulty_level'),
            "content_type": content.get('content_type'),
            "estimated_completion_time": content.get('metadata', {}).get('estimated_completion_time'),
            "topics": content.get('metadata', {}).get('topics', []),
            "prerequisites": content.get('metadata', {}).get('prerequisites', [])
        }

        return success(analytics, "Content analytics retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Bulk Operations
@content_bp.route("/content/bulk", methods=["POST"])
def bulk_create_content_route():
    """Bulk create multiple content items"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return error("Expected list of content data", 400)

        results = bulk_create_content(data)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        return success({
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f"Bulk create completed: {len(successful)} successful, {len(failed)} failed", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Recommendations (for learners)
@content_bp.route("/content/<id>/learners", methods=["GET"])
def get_learners_for_content(id):
    """Get learners who might benefit from this content (based on prerequisites and difficulty)"""
    try:
        content = read_content(id)
        if not content:
            return error("Content not found", 404)

        # This would typically involve ML recommendations
        # For now, returning content info
        return success({
            "content_id": id,
            "recommendation_criteria": {
                "difficulty_level": content.get('difficulty_level'),
                "prerequisites": content.get('metadata', {}).get('prerequisites', []),
                "topics": content.get('metadata', {}).get('topics', [])
            }
        }, "Content recommendation criteria retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Content Assessment Integration
@content_bp.route("/content/<id>/assessments", methods=["GET"])
def get_content_assessments(id):
    """Get assessment criteria for content"""
    try:
        content = read_content(id)
        if not content:
            return error("Content not found", 404)

        assessment_criteria = content.get('metadata', {}).get('assessment_criteria', [])
        
        return success({
            "content_id": id,
            "assessment_criteria": assessment_criteria
        }, "Content assessment criteria retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)