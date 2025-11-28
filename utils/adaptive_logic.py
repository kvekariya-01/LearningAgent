from utils.crud_operations import read_learner, create_progress_log, log_activity
from models.progress import ProgressLog
from models.intervention import Intervention
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
import statistics

IN_MEMORY_DB = {"interventions": {}}

def _get_mongo_collection(collection_name):
    from config.db_config import db
    try:
        if db is not None:
            return db[collection_name]
        else:
            return None
    except (PyMongoError, TypeError, KeyError) as e:
        print("MongoDB Atlas connection error:", e)
        return None

def create_intervention(intervention_obj):
    coll = _get_mongo_collection("interventions")
    doc = intervention_obj.to_dict()
    if coll is not None:
        coll.insert_one(doc)
        return doc
    else:
        IN_MEMORY_DB["interventions"][intervention_obj.id] = doc
        return doc

def read_interventions(learner_id=None):
    coll = _get_mongo_collection("interventions")
    if coll is not None:
        if learner_id:
            docs = list(coll.find({"learner_id": learner_id}, {"_id": 0}))
        else:
            docs = list(coll.find({}, {"_id": 0}))
        return docs
    else:
        if learner_id:
            return [item for item in IN_MEMORY_DB["interventions"].values() if item["learner_id"] == learner_id]
        return list(IN_MEMORY_DB["interventions"].values())

def adjust_difficulty(learner_id, recent_score):
    """
    Adjust difficulty based on recent performance and learning patterns.
    Returns new difficulty level and triggers interventions if needed.
    """
    learner_data = read_learner(learner_id)
    if not learner_data:
        return {"error": "Learner not found"}, None

    activities = learner_data.get("activities", [])
    if not activities:
        return {"difficulty": 2, "reason": "No activities yet, default intermediate"}, None

    # Get recent activities (last 10)
    recent_activities = sorted(activities, key=lambda x: x["timestamp"], reverse=True)[:10]

    # Calculate recent performance metrics
    recent_scores = [a.get("score") for a in recent_activities if a.get("score") is not None]
    if not recent_scores:
        avg_recent_score = 0
    else:
        avg_recent_score = statistics.mean(recent_scores)

    # Calculate score trend (improvement over time)
    if len(recent_scores) >= 3:
        first_half = statistics.mean(recent_scores[:len(recent_scores)//2])
        second_half = statistics.mean(recent_scores[len(recent_scores)//2:])
        score_trend = second_half - first_half
    else:
        score_trend = 0

    # Current difficulty estimation (based on average score)
    all_scores = [a.get("score") for a in activities if a.get("score") is not None]
    if not all_scores:
        current_difficulty = 2
    else:
        avg_all_scores = statistics.mean(all_scores)
        if avg_all_scores >= 85:
            current_difficulty = 3  # Advanced
        elif avg_all_scores >= 70:
            current_difficulty = 2  # Intermediate
        else:
            current_difficulty = 1  # Beginner

    # Adjust difficulty based on recent performance
    new_difficulty = current_difficulty

    if recent_score >= 90 and score_trend > 5:
        # Excellent performance and improving - increase difficulty
        new_difficulty = min(current_difficulty + 1, 3)
        reason = "Excellent performance and improving trend"
    elif recent_score >= 80 and score_trend > 0:
        # Good performance - maintain or slight increase
        reason = "Good performance, maintaining difficulty"
    elif recent_score < 60 and score_trend < -5:
        # Struggling and declining - decrease difficulty
        new_difficulty = max(current_difficulty - 1, 1)
        reason = "Struggling performance, reducing difficulty"
    elif recent_score < 70:
        # Below average - maintain or slight decrease
        new_difficulty = max(current_difficulty - 0.5, 1)
        reason = "Below average performance, adjusting difficulty"
    else:
        reason = "Performance stable, maintaining difficulty"

    # Trigger interventions based on patterns
    interventions = []

    # High improvement intervention
    if score_trend > 10:
        intervention = Intervention(
            learner_id=learner_id,
            intervention_type="motivational_message",
            message="You're improving fast! Keep up the great work!",
            triggered_by="high_improvement"
        )
        create_intervention(intervention)
        interventions.append(intervention.to_dict())

    # Struggling intervention
    if recent_score < 50 and len(recent_scores) >= 5:
        avg_last_5 = statistics.mean(recent_scores[:5])
        if avg_last_5 < 50:
            intervention = Intervention(
                learner_id=learner_id,
                intervention_type="motivational_message",
                message="Don't worry, everyone struggles sometimes. Let's review the basics together.",
                triggered_by="low_score"
            )
            create_intervention(intervention)
            interventions.append(intervention.to_dict())

    # Log difficulty adjustment as progress
    progress_log = ProgressLog(
        learner_id=learner_id,
        milestone="difficulty_adjusted",
        engagement_score=recent_score,
        learning_velocity=score_trend,
        metadata={
            "old_difficulty": current_difficulty,
            "new_difficulty": new_difficulty,
            "reason": reason,
            "avg_recent_score": avg_recent_score
        }
    )
    create_progress_log(progress_log)

    return {
        "difficulty": new_difficulty,
        "reason": reason,
        "metrics": {
            "recent_score": recent_score,
            "avg_recent_score": avg_recent_score,
            "score_trend": score_trend,
            "current_difficulty": current_difficulty
        }
    }, interventions