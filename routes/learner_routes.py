from flask import Blueprint, request, jsonify
import logging
from utils.crud_operations import (
    log_activity, read_learner, create_progress_log, get_progress_summary,
    create_learner, update_learner, delete_learner, read_learners
)
from utils.schemas import (
    validate_learner_data, validate_learner_update_data, validate_activity_data,
    validate_progress_data, validate_prediction_data, validate_difficulty_adjustment_data
)
from utils.response import success, error
from utils.adaptive_logic import adjust_difficulty, read_interventions
from utils.analytics import get_learner_insights, get_cohort_comparison, get_analytics_summary
# Import enhanced intelligence engine
from utils.intelligence_engine import (
    MotivationalMessagingSystem, 
    WeeklyProgressReportGenerator, 
    StrengthWeaknessAnalyzer,
    get_enhanced_intelligence_features
)
from ml.progress_model import evaluate_progress
from ml.linear_reg import predict_completion_time
from ml.recommender import hybrid_recommend, recommend_for_new_learner
# Enhanced recommendation engine for better course recommendations
from enhanced_recommendation_engine import get_enhanced_recommendations

# Configure logging
logger = logging.getLogger(__name__)
from models.progress import ProgressLog
from models.learner import Learner
try:
    # Try to import marshmallow's ValidationError (preferred)
    from marshmallow import ValidationError
except Exception:
    # Fallback ValidationError if marshmallow is not installed or unresolved by static analysis
    class ValidationError(Exception):
        """Fallback ValidationError used when marshmallow is unavailable."""
        def __init__(self, messages=None):
            super().__init__(messages)
            # Keep the .messages attribute to match code that expects e.messages
            self.messages = messages

learner_bp = Blueprint("learner_bp", __name__, url_prefix="/api")
@learner_bp.route("/learner", methods=["POST"])
def create_learner_route():
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_learner_data(data)
        learner = Learner(**validated_data)
        result = create_learner(learner)

        if not result:
            return error("Failed to create learner", 500)

        return success(result, "Learner created successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Registration endpoint alias for Day 3 requirements
@learner_bp.route("/learner/register", methods=["POST"])
def register_learner_route():
    """Alias for learner registration to match Day 3 requirements"""
    return create_learner_route()

@learner_bp.route("/learner/<id>", methods=["GET"])
def get_learner(id):
    try:
        learner = read_learner(id)
        if not learner:
            return error("Learner not found", 404)

        return success(learner, "Learner retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>", methods=["PUT"])
def update_learner_route(id):
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_learner_update_data(data)
        result = update_learner(id, validated_data)

        if not result:
            return error("Learner not found or update failed", 404)

        return success(result, "Learner updated successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>", methods=["DELETE"])
def delete_learner_route(id):
    try:
        result = delete_learner(id)
        if not result:
            return error("Learner not found", 404)

        return success(None, "Learner deleted successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/profile", methods=["GET"])
def get_learner_profile(id):
    try:
        learner_data = read_learner(id)
        if not learner_data:
            return error("Learner not found", 404)

        # Calculate profile metrics
        activities = learner_data.get("activities", [])
        
        # Basic metrics
        total_activities = len(activities)
        modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])
        
        # Score analysis
        scores = [a.get("score") for a in activities if a.get("score") is not None]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        min_score = min(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        
        # Time analysis
        total_time = sum(a.get("duration", 0) for a in activities)
        avg_session_time = round(total_time / total_activities, 2) if total_activities > 0 else 0.0
        
        # Calculate learning velocity
        from utils.analytics import calculate_learner_velocity
        velocity = calculate_learner_velocity(learner_data)
        
        # Performance trend (last 5 activities)
        recent_scores = scores[-5:] if len(scores) >= 5 else scores
        score_trend = "stable"
        if len(recent_scores) >= 3:
            first_half = statistics.mean(recent_scores[:len(recent_scores)//2])
            second_half = statistics.mean(recent_scores[len(recent_scores)//2:])
            if second_half > first_half + 5:
                score_trend = "improving"
            elif second_half < first_half - 5:
                score_trend = "declining"
        
        # Activity distribution
        activity_types = {}
        for activity in activities:
            act_type = activity.get("activity_type", "Unknown")
            activity_types[act_type] = activity_types.get(act_type, 0) + 1
        
        # Learning profile information
        profile = learner_data.get("profile", {})
        learning_metrics = learner_data.get("learning_metrics", {})
        
        # Construct comprehensive profile response
        profile_data = {
            "id": learner_data.get("id"),
            "personal_info": {
                "name": learner_data.get("name"),
                "age": learner_data.get("age"),
                "gender": learner_data.get("gender"),
                "learning_style": learner_data.get("learning_style"),
                "preferences": learner_data.get("preferences", []),
                "created_at": learner_data.get("created_at"),
                "updated_at": learner_data.get("updated_at")
            },
            "learning_profile": {
                "total_activities": total_activities,
                "modules_completed": modules_completed,
                "total_time_spent": round(total_time, 2),
                "average_session_time": avg_session_time,
                "learning_velocity": velocity,
                "score_trend": score_trend,
                "activity_distribution": activity_types
            },
            "performance_metrics": {
                "average_score": avg_score,
                "min_score": min_score,
                "max_score": max_score,
                "total_score_points": sum(scores) if scores else 0,
                "score_improvement": round(max_score - min_score, 2) if scores and len(scores) > 1 else 0,
                "strongest_areas": [],  # To be calculated by analytics
                "weakest_areas": []   # To be calculated by analytics
            },
            "detailed_profile": profile,
            "learning_metrics": learning_metrics,
            "meta": learner_data.get("meta", {})
        }
        
        # Get recent activities (last 10)
        recent_activities = sorted(activities, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        profile_data["recent_activities"] = recent_activities
        
        # Calculate engagement score
        from utils.crud_operations import calculate_cumulative_engagement_score
        engagement_score = calculate_cumulative_engagement_score(id)
        profile_data["performance_metrics"]["engagement_score"] = engagement_score
        
        return success(profile_data, "Profile retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learners", methods=["GET"])
def list_learners():
    try:
        learners = read_learners()
        return success(learners, "Learners retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Activity and Analytics Routes

@learner_bp.route("/learner/<id>/activity", methods=["POST"])
def log_learner_activity(id):
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        # Check if data is a list (array of activities) or a single object
        if isinstance(data, list):
            # Handle array of activities
            logged_activities = []
            for activity_data in data:
                validated_data = validate_activity_data(activity_data)
                activity_type = validated_data["activity_type"]
                duration = validated_data["duration"]
                score = validated_data.get("score")

                # Log each activity
                logged_learner = log_activity(id, activity_type, duration, score)
                if not logged_learner:
                    return error(f"Learner not found for activity: {activity_data}", 404)
                logged_activities.append(logged_learner)

                # Auto-log progress for milestones
                if activity_type == "module_completed":
                    from models.progress import LearningVelocity
                    learning_velocity_obj = LearningVelocity(
                        current_velocity=1.0,  # Placeholder, could be calculated
                        velocity_trend="stable"
                    )
                    progress_log = ProgressLog(
                        learner_id=id,
                        milestone="module_completed",
                        engagement_score=score if score else 0.0,
                        learning_velocity=learning_velocity_obj
                    )
                    create_progress_log(progress_log)

            return success({
                "count": len(logged_activities),
                "learners": logged_activities
            }, f"{len(logged_activities)} activities logged successfully", 201)
        else:
            # Handle single activity
            validated_data = validate_activity_data(data)
            activity_type = validated_data["activity_type"]
            duration = validated_data["duration"]
            score = validated_data.get("score")

            logged_learner = log_activity(id, activity_type, duration, score)
            if not logged_learner:
                return error("Learner not found", 404)

            # Auto-log progress for milestones
            if activity_type == "module_completed":
                from models.progress import LearningVelocity
                learning_velocity_obj = LearningVelocity(
                    current_velocity=1.0,  # Placeholder, could be calculated
                    velocity_trend="stable"
                )
                progress_log = ProgressLog(
                    learner_id=id,
                    milestone="module_completed",
                    engagement_score=score if score else 0.0,
                    learning_velocity=learning_velocity_obj
                )
                create_progress_log(progress_log)

            # Trigger adaptive difficulty adjustment and interventions
            if score is not None:
                adjustment_result, interventions = adjust_difficulty(id, score)
                if "error" not in adjustment_result:
                    logged_learner["difficulty_adjustment"] = adjustment_result
                    if interventions:
                        logged_learner["interventions"] = interventions

            return success(logged_learner, "Activity logged successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/activities", methods=["GET"])
def get_learner_activities(id):
    try:
        learner_data = read_learner(id)
        if not learner_data:
            return error("Learner not found", 404)

        activities = learner_data.get("activities", [])
        return success({
            "learner_id": id,
            "activities": activities
        }, "Activities retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/recommendations", methods=["GET"])
def get_learner_recommendations(id):
    try:
        learner_data = read_learner(id)
        if not learner_data:
            return error("Learner not found", 404)

        activities = learner_data.get("activities", [])

        # Check if new learner (no activities)
        if not activities:
            fallback_recs = recommend_for_new_learner(learner_data)
            return success({
                "learner_id": id,
                "is_new_learner": True,
                "recommendations": [
                    {
                        "content_id": c['id'],
                        "title": c['title'],
                        "reason": "Recommended for new learners"
                    } for c in fallback_recs
                ]
            }, "Recommendations retrieved successfully")

        # Use enhanced recommendation engine for better recommendations
        try:
            enhanced_recs = get_enhanced_recommendations(id, learner_data)
            return success(enhanced_recs, "Enhanced recommendations retrieved successfully")
        except Exception as e:
            logger.warning(f"Enhanced recommendation failed: {e}. Falling back to basic recommender.")
            
            # Fallback to hybrid recommender
            total_hours = sum(activity.get("duration", 0) for activity in activities)
            modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])
            avg_score = sum(activity.get("score", 0) for activity in activities if activity.get("score") is not None) / len([a for a in activities if a.get("score") is not None]) if activities else 0

            # Prepare recent_scores for hybrid recommender
            recent_scores = {
                'avg_score': avg_score,
                'time_spent': total_hours,
                'difficulty': 2  # Default intermediate, could be derived from courses
            }

            try:
                hybrid_recs = hybrid_recommend(id, learner_data, recent_scores)
                return success(hybrid_recs, "Recommendations retrieved successfully")
            except Exception as fallback_e:
                # Ultimate fallback to basic recommendations
                progress = evaluate_progress(total_hours, modules_completed, avg_score)
                recommendations = []
                if progress["progress"] < 50:
                    recommendations.append("Focus on completing more modules to improve progress.")
                if total_hours < 10:
                    recommendations.append("Increase study hours to accelerate learning.")
                if avg_score < 70:
                    recommendations.append("Practice more assignments to boost scores.")

                return success({
                    "learner_id": id,
                    "progress": progress,
                    "recommendations": recommendations,
                    "recommendation_type": "basic_fallback",
                    "error": f"Both enhanced and hybrid recommenders failed: {str(fallback_e)}"
                }, "Basic recommendations retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/predict/completion-time", methods=["POST"])
def predict_completion():
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_prediction_data(data)
        avg_score = validated_data['avg_score']
        time_spent = validated_data['time_spent']
        difficulty = validated_data['difficulty']

        prediction = predict_completion_time(avg_score, time_spent, difficulty)
        return success({
            "predicted_completion_time": prediction,
            "features": {
                "avg_score": avg_score,
                "time_spent": time_spent,
                "difficulty": difficulty
            }
        }, "Prediction completed successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/progress", methods=["GET"])
def get_learner_progress_summary(id):
    try:
        summary = get_progress_summary(id)
        if not summary:
            return error("Learner not found", 404)
        return success(summary, "Progress summary retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/progress/log", methods=["POST"])
def log_progress(id):
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_progress_data(data)
        milestone = validated_data['milestone']
        engagement_score = validated_data.get('engagement_score', 0.0)
        learning_velocity_data = validated_data.get('learning_velocity', 0.0)
        
        # Create LearningVelocity object
        from models.progress import LearningVelocity
        if isinstance(learning_velocity_data, (int, float)):
            learning_velocity_obj = LearningVelocity(
                current_velocity=float(learning_velocity_data),
                velocity_trend="stable" if learning_velocity_data >= 1.0 else "decelerating"
            )
        elif isinstance(learning_velocity_data, dict):
            learning_velocity_obj = LearningVelocity(**learning_velocity_data)
        else:
            learning_velocity_obj = LearningVelocity()  # Default object

        progress_log = ProgressLog(
            learner_id=id,
            milestone=milestone,
            engagement_score=engagement_score,
            learning_velocity=learning_velocity_obj
        )

        result = create_progress_log(progress_log)
        if not result:
            return error("Failed to log progress", 500)

        return success({"id": progress_log.id}, "Progress logged successfully", 201)
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Adaptive Logic Routes

@learner_bp.route("/learner/<id>/adjust-difficulty", methods=["POST"])
def adjust_learner_difficulty(id):
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)

        validated_data = validate_difficulty_adjustment_data(data)
        recent_score = validated_data["recent_score"]

        adjustment_result, interventions = adjust_difficulty(id, recent_score)

        if "error" in adjustment_result:
            return error(adjustment_result["error"], 404)

        response_data = {
            "adjustment": adjustment_result,
            "interventions": interventions if interventions else []
        }

        return success(response_data, "Difficulty adjusted successfully")
    except ValidationError as e:
        return error("Validation error", 400, e.messages)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/interventions", methods=["GET"])
def get_learner_interventions(id):
    try:
        interventions = read_interventions(id)
        return success({
            "learner_id": id,
            "interventions": interventions
        }, "Interventions retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Analytics Routes

@learner_bp.route("/analytics/learner/<id>", methods=["GET"])
def get_learner_analytics(id):
    try:
        insights = get_learner_insights(id)
        if "error" in insights:
            return error(insights["error"], 404)
        return success(insights, "Learner analytics retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/analytics/cohort", methods=["GET"])
def get_cohort_analytics():
    try:
        group_by = request.args.get("group_by", "learning_style")
        learner_id = request.args.get("learner_id")

        comparison = get_cohort_comparison(learner_id, group_by)
        if "error" in comparison:
            return error(comparison["error"], 404)
        return success(comparison, "Cohort analytics retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/analytics/summary", methods=["GET"])
def get_analytics_summary_route():
    try:
        summary = get_analytics_summary()
        if "error" in summary:
            return error(summary["error"], 404)
        return success(summary, "Analytics summary retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

# Enhanced Intelligence Engine Routes

@learner_bp.route("/learner/<id>/weekly-report", methods=["GET"])
def get_weekly_progress_report(id):
    """Generate comprehensive weekly progress report for a learner"""
    try:
        # Get week start date from query parameter
        week_start_date = request.args.get("week_start")
        
        # Generate weekly report
        report = WeeklyProgressReportGenerator.generate_weekly_report(id, week_start_date)
        
        if "error" in report:
            return error(report["error"], 404)
        
        return success(report, "Weekly progress report generated successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/motivation", methods=["POST"])
def trigger_motivational_intervention(id):
    """Trigger personalized motivational intervention for a learner"""
    try:
        data = request.get_json()
        if not data:
            return error("No data provided", 400)
        
        context = data.get("context", "general")
        recent_score = data.get("recent_score")
        
        # Generate and trigger motivational intervention
        result = MotivationalMessagingSystem.trigger_motivational_intervention(
            id, context, recent_score
        )
        
        if "error" in result:
            return error(result["error"], 404)
        
        return success({
            "intervention_id": result["intervention_id"],
            "message": result["message"],
            "type": result["type"],
            "priority": result["priority"]
        }, "Motivational intervention triggered successfully", 201)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/analysis", methods=["GET"])
def get_strength_weakness_analysis(id):
    """Get comprehensive strength and weakness analysis for a learner"""
    try:
        # Analyze strengths and weaknesses
        analysis = StrengthWeaknessAnalyzer.analyze_strengths_weaknesses(id)
        
        if "error" in analysis:
            return error(analysis["error"], 404)
        
        return success(analysis, "Strength and weakness analysis completed successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/learner/<id>/motivational-messages", methods=["GET"])
def get_motivational_messages(id):
    """Get available motivational messages for a learner without triggering interventions"""
    try:
        learner_data = read_learner(id)
        if not learner_data:
            return error("Learner not found", 404)
        
        # Generate different types of motivational messages
        messages = {
            "general": MotivationalMessagingSystem.generate_motivational_message(learner_data, None, "general"),
            "struggling": MotivationalMessagingSystem.generate_motivational_message(learner_data, None, "struggling"),
            "achievement": MotivationalMessagingSystem.generate_motivational_message(learner_data, None, "achievement"),
            "weekly": MotivationalMessagingSystem.generate_motivational_message(learner_data, None, "weekly_report")
        }
        
        return success(messages, "Motivational messages retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

@learner_bp.route("/intelligence/features", methods=["GET"])
def get_intelligence_features():
    """Get information about available intelligence features"""
    try:
        features = {
            "real_time_difficulty_adjustment": {
                "description": "Automatically adjusts content difficulty based on learner performance",
                "thresholds": {
                    "decrease_difficulty": "score < 60",
                    "increase_difficulty": "score > 85"
                }
            },
            "intervention_trigger_logic": {
                "description": "Intelligent intervention system that triggers support based on learning patterns",
                "triggers": [
                    "low_score",
                    "high_improvement", 
                    "declining_trend",
                    "new_learner",
                    "milestone"
                ]
            },
            "motivational_messaging_system": {
                "description": "Personalized motivational messages based on performance and context",
                "message_types": [
                    "achievement",
                    "encouragement", 
                    "motivation",
                    "support",
                    "momentum",
                    "reassurance"
                ]
            },
            "strength_weakness_analyzer": {
                "description": "Analyzes learner performance to identify strengths and areas for improvement",
                "analysis_areas": [
                    "activity_type_performance",
                    "learning_patterns",
                    "time_preferences",
                    "session_preferences"
                ]
            },
            "learning_velocity_calculation": {
                "description": "Calculates learning velocity as modules completed per week",
                "formula": "total_modules_completed / weeks_active"
            },
            "weekly_progress_report_generator": {
                "description": "Generates comprehensive weekly progress reports with insights",
                "components": [
                    "weekly_summary",
                    "performance_metrics", 
                    "trends",
                    "achievements",
                    "recommendations"
                ]
            },
            "cohort_comparison_metrics": {
                "description": "Compares learner performance against peers in similar groups",
                "metrics": [
                    "percentile_rankings",
                    "group_averages",
                    "individual_comparisons"
                ]
            }
        }
        
        return success(features, "Intelligence features information retrieved successfully")
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)
