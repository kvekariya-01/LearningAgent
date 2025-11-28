# utils/crud_operations.py
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
from models.learner import Learner
from models.content import Content
from models.engagement import Engagement
from models.progress import ProgressLog
from datetime import datetime, timezone

IN_MEMORY_DB = {"learners": {}, "contents": {}, "engagements": {}, "progress_logs": {}}

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

def create_indexes():
    """Create necessary indexes for performance"""
    try:
        from config.db_config import db
        
        if db is None:
            # Silently skip index creation when using in-memory database
            return
            
        # Learner indexes
        db["learners"].create_index([("learner_id", ASCENDING)])

        # Content indexes
        db["contents"].create_index([("course_id", ASCENDING)])

        # Engagement indexes
        db["engagements"].create_index([("learner_id", ASCENDING)])
        db["engagements"].create_index([("course_id", ASCENDING)])
        db["engagements"].create_index([("content_id", ASCENDING)])

        # Progress logs indexes
        db["progress_logs"].create_index([("learner_id", ASCENDING)])
        db["progress_logs"].create_index([("timestamp", ASCENDING)])

        print("[OK] Database indexes created successfully")
    except (PyMongoError, TypeError, KeyError) as e:
        print("⚠ Failed to create indexes:", e)

def create_learner(learner_obj):
    coll = _get_mongo_collection("learners")
    doc = learner_obj.to_dict()
    if coll is not None:
        coll.insert_one(doc)
        return doc
    else:
        IN_MEMORY_DB["learners"][learner_obj.id] = doc
        return doc

def create_content(content_obj):
    coll = _get_mongo_collection("contents")
    doc = content_obj.to_dict()
    if coll is not None:
        coll.insert_one(doc)
        return doc
    else:
        IN_MEMORY_DB["contents"][content_obj.id] = doc
        return doc

def create_engagement(engagement_obj):
    coll = _get_mongo_collection("engagements")
    doc = engagement_obj.to_dict()
    if coll is not None:
        coll.insert_one(doc)
        return doc
    else:
        IN_MEMORY_DB["engagements"][engagement_obj.id] = doc
        return doc

def create_progress_log(progress_log_obj):
    coll = _get_mongo_collection("progress_logs")
    doc = progress_log_obj.to_dict()
    if coll is not None:
        coll.insert_one(doc)
        return doc
    else:
        IN_MEMORY_DB["progress_logs"][progress_log_obj.id] = doc
        return doc

def read_learner(learner_id):
    coll = _get_mongo_collection("learners")
    if coll is not None:
        doc = coll.find_one({"_id": learner_id}, {"_id": 0})
        return doc
    else:
        return IN_MEMORY_DB["learners"].get(learner_id)

def read_learners():
    coll = _get_mongo_collection("learners")
    if coll is not None:
        docs = list(coll.find({}, {"_id": 0}))
        return docs
    else:
        return list(IN_MEMORY_DB["learners"].values())

def read_content(content_id):
    coll = _get_mongo_collection("contents")
    if coll is not None:
        doc = coll.find_one({"_id": content_id}, {"_id": 0})
        return doc
    else:
        return IN_MEMORY_DB["contents"].get(content_id)

def read_contents():
    coll = _get_mongo_collection("contents")
    if coll is not None:
        docs = list(coll.find({}, {"_id": 0}))
        return docs
    else:
        return list(IN_MEMORY_DB["contents"].values())

def read_engagement(engagement_id):
    coll = _get_mongo_collection("engagements")
    if coll is not None:
        doc = coll.find_one({"_id": engagement_id}, {"_id": 0})
        if doc:
            # Convert MongoDB document to Engagement object
            doc["_id"] = engagement_id  # Add back the _id field
            engagement = Engagement(**doc)
            return engagement
        return None
    else:
        doc = IN_MEMORY_DB["engagements"].get(engagement_id)
        if doc:
            engagement = Engagement(**doc)
            return engagement
        return None

def read_engagements():
    coll = _get_mongo_collection("engagements")
    if coll is not None:
        docs = list(coll.find({}, {"_id": 0}))
        # Convert MongoDB documents to Engagement objects
        engagements = []
        for doc in docs:
            doc["_id"] = doc.get("id", doc.get("_id"))  # Ensure _id is available
            engagement = Engagement(**doc)
            engagements.append(engagement)
        return engagements
    else:
        engagements = []
        for doc in IN_MEMORY_DB["engagements"].values():
            engagement = Engagement(**doc)
            engagements.append(engagement)
        return engagements

def read_progress_logs(learner_id=None):
    coll = _get_mongo_collection("progress_logs")
    if coll is not None:
        if learner_id:
            docs = list(coll.find({"learner_id": learner_id}, {"_id": 0}))
        else:
            docs = list(coll.find({}, {"_id": 0}))
        return docs
    else:
        if learner_id:
            return [log for log in IN_MEMORY_DB["progress_logs"].values() if log["learner_id"] == learner_id]
        return list(IN_MEMORY_DB["progress_logs"].values())

def update_learner(learner_id, update_fields: dict):
    coll = _get_mongo_collection("learners")
    if coll is not None:
        res = coll.find_one_and_update(
            {"_id": learner_id}, {"$set": update_fields}, return_document=True
        )
        if res:
            res.pop("_id", None)
        return res
    else:
        doc = IN_MEMORY_DB["learners"].get(learner_id)
        if not doc:
            return None
        doc.update(update_fields)
        return doc

def update_content(content_id, update_fields: dict):
    coll = _get_mongo_collection("contents")
    if coll is not None:
        res = coll.find_one_and_update(
            {"_id": content_id}, {"$set": update_fields}, return_document=True
        )
        if res:
            res.pop("_id", None)
        return res
    else:
        doc = IN_MEMORY_DB["contents"].get(content_id)
        if not doc:
            return None
        doc.update(update_fields)
        return doc

def update_engagement(engagement_id, update_fields: dict):
    coll = _get_mongo_collection("engagements")
    if coll is not None:
        res = coll.find_one_and_update(
            {"_id": engagement_id}, {"$set": update_fields}, return_document=True
        )
        if res:
            res.pop("_id", None)
            # Return as Engagement object for consistency
            if "_id" not in res:
                res["_id"] = engagement_id
            engagement = Engagement(**res)
            return engagement.to_dict()
        return None
    else:
        doc = IN_MEMORY_DB["engagements"].get(engagement_id)
        if not doc:
            return None
        doc.update(update_fields)
        # Return as Engagement object for consistency
        engagement = Engagement(**doc)
        return engagement.to_dict()

def log_activity(learner_id, activity_type, duration, score):
    coll = _get_mongo_collection("learners")
    activity = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "activity_type": str(activity_type),
        "duration": float(duration),
        "score": score if score is not None else None,
    }
    if coll is not None:
        coll.update_one(
            {"_id": learner_id},
            {"$push": {"activities": activity}, "$inc": {"activity_count": 1}},
        )
        return read_learner(learner_id)
    else:
        doc = IN_MEMORY_DB["learners"].get(learner_id)
        if not doc:
            return None
        doc.setdefault("activities", []).append(activity)
        doc["activity_count"] = doc.get("activity_count", 0) + 1
        return doc

def delete_learner(learner_id):
    coll = _get_mongo_collection("learners")
    if coll is not None:
        result = coll.delete_one({"_id": learner_id})
        return result.deleted_count > 0
    else:
        return IN_MEMORY_DB["learners"].pop(learner_id, None) is not None

def delete_content(content_id):
    coll = _get_mongo_collection("contents")
    if coll is not None:
        result = coll.delete_one({"_id": content_id})
        return result.deleted_count > 0
    else:
        return IN_MEMORY_DB["contents"].pop(content_id, None) is not None

def delete_engagement(engagement_id):
    coll = _get_mongo_collection("engagements")
    if coll is not None:
        result = coll.delete_one({"_id": engagement_id})
        return result.deleted_count > 0
    else:
        return IN_MEMORY_DB["engagements"].pop(engagement_id, None) is not None

def read_learner_activities(learner_id):
    """Read all activities for a specific learner"""
    learner_data = read_learner(learner_id)
    if not learner_data:
        return None
    return learner_data.get("activities", [])

def calculate_cumulative_engagement_score(learner_id):
    """Calculate cumulative engagement score = weighted(avg_score, activity_freq)"""
    activities = read_learner(learner_id)
    if not activities or "activities" not in activities:
        return 0.0

    activities_list = activities["activities"]
    if not activities_list:
        return 0.0

    # Calculate average score
    scores = [a.get("score") for a in activities_list if a.get("score") is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Calculate activity frequency (activities per day over the period)
    if len(activities_list) < 2:
        activity_freq = 1.0  # Default for few activities
    else:
        timestamps = sorted([a["timestamp"] for a in activities_list])
        first = datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))
        last = datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00'))
        days_diff = max((last - first).days, 1)  # Avoid division by zero
        activity_freq = len(activities_list) / days_diff

    # Weighted score: 70% avg_score, 30% activity_freq (normalized)
    # Normalize activity_freq to 0-100 scale (assuming max 5 activities/day)
    normalized_freq = min(activity_freq * 20, 100)
    cumulative_score = (0.7 * avg_score) + (0.3 * normalized_freq)

    return round(cumulative_score, 2)

def get_progress_summary(learner_id):
    """Get progress summary including milestones, engagement, and learning velocity"""
    progress_logs = read_progress_logs(learner_id)
    learner_data = read_learner(learner_id)

    if not learner_data:
        return None

    activities = learner_data.get("activities", [])
    total_activities = len(activities)

    # Calculate learning velocity (modules completed per week)
    modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])
    if total_activities > 0 and len(activities) >= 2:
        timestamps = sorted([a["timestamp"] for a in activities])
        first = datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))
        last = datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00'))
        weeks_diff = max((last - first).days / 7, 0.1)  # Avoid division by zero
        learning_velocity = modules_completed / weeks_diff
    else:
        learning_velocity = 0.0

    cumulative_engagement = calculate_cumulative_engagement_score(learner_id)

    # Get recent milestones from progress logs
    recent_milestones = sorted(progress_logs, key=lambda x: x["timestamp"], reverse=True)[:5]

    return {
        "learner_id": learner_id,
        "total_activities": total_activities,
        "modules_completed": modules_completed,
        "learning_velocity": round(learning_velocity, 2),
        "cumulative_engagement_score": cumulative_engagement,
        "recent_milestones": recent_milestones
    }

# === MISSING CRUD OPERATIONS FOR COMPREHENSIVE SCHEMA ===

def create_learner_profile(learner_id: str, profile_data: dict):
    """Create or update learner profile with enhanced learning data"""
    return update_learner(learner_id, {"profile": profile_data})

def read_learner_profile(learner_id: str):
    """Read learner profile data"""
    learner = read_learner(learner_id)
    return learner.get("profile", {}) if learner else None

def create_learning_metrics(learner_id: str, metrics_data: dict):
    """Create or update learning metrics"""
    return update_learner(learner_id, {"learning_metrics": metrics_data})

def read_learning_metrics(learner_id: str):
    """Read learning metrics data"""
    learner = read_learner(learner_id)
    return learner.get("learning_metrics", {}) if learner else None

def create_content_metadata(content_id: str, metadata_data: dict):
    """Create or update content metadata"""
    return update_content(content_id, {"metadata": metadata_data})

def read_content_metadata(content_id: str):
    """Read content metadata"""
    content = read_content(content_id)
    return content.get("metadata", {}) if content else None

def update_learning_history(learner_id: str, history_data: dict):
    """Update learning history with new data"""
    learner = read_learner(learner_id)
    if not learner:
        return None
    
    current_history = learner.get("learning_metrics", {}).get("learning_history", {})
    updated_history = {**current_history, **history_data}
    
    return update_learner(learner_id, {
        "learning_metrics.learning_history": updated_history
    })

def get_learning_history(learner_id: str):
    """Get complete learning history"""
    learner = read_learner(learner_id)
    if not learner:
        return None
    return learner.get("learning_metrics", {}).get("learning_history", {})

def update_engagement_metrics(learner_id: str, content_id: str, metrics_data: dict):
    """Update engagement metrics with interaction patterns"""
    engagements = read_engagements()
    learner_engagements = [e for e in engagements if e.learner_id == learner_id and e.content_id == content_id]
    
    if not learner_engagements:
        return None
    
    engagement = learner_engagements[-1]  # Get latest engagement
    current_metrics = engagement.interaction_metrics.model_dump() if engagement.interaction_metrics else {}
    updated_metrics = {**current_metrics, **metrics_data}
    
    return update_engagement(engagement.id, {"interaction_metrics": updated_metrics})

def get_engagement_metrics(learner_id: str, content_id: str = None):
    """Get engagement metrics for learner"""
    engagements = read_engagements()
    learner_engagements = [e for e in engagements if e.learner_id == learner_id]
    
    if content_id:
        learner_engagements = [e for e in learner_engagements if e.content_id == content_id]
    
    return [{"engagement_id": e.id, "metrics": e.interaction_metrics.model_dump() if e.interaction_metrics else {}, "timestamp": e.timestamp} 
            for e in learner_engagements]

def bulk_create_learners(learners_data: list):
    """Bulk create multiple learners"""
    results = []
    for learner_data in learners_data:
        try:
            from models.learner import Learner
            learner = Learner(**learner_data)
            result = create_learner(learner)
            results.append({"success": True, "learner_id": result["id"], "data": result})
        except Exception as e:
            results.append({"success": False, "error": str(e), "data": learner_data})
    return results

def bulk_create_content(content_data_list: list):
    """Bulk create multiple content items"""
    results = []
    for content_data in content_data_list:
        try:
            from models.content import Content
            content = Content(**content_data)
            result = create_content(content)
            results.append({"success": True, "content_id": result["id"], "data": result})
        except Exception as e:
            results.append({"success": False, "error": str(e), "data": content_data})
    return results

def search_learners_by_criteria(criteria: dict):
    """Search learners by various criteria"""
    learners = read_learners()
    results = []
    
    for learner in learners:
        match = True
        for key, value in criteria.items():
            if key in ["learning_style", "gender"]:
                if learner.get(key) != value:
                    match = False
                    break
            elif key == "preferences":
                learner_prefs = learner.get("preferences", [])
                if not any(pref.lower() in [p.lower() for p in learner_prefs] for pref in value):
                    match = False
                    break
            elif key == "age_range":
                age = learner.get("age", 0)
                if not (value[0] <= age <= value[1]):
                    match = False
                    break
        
        if match:
            results.append(learner)
    
    return results

def search_content_by_criteria(criteria: dict):
    """Search content by various criteria"""
    contents = read_contents()
    results = []
    
    for content in contents:
        match = True
        for key, value in criteria.items():
            if key == "difficulty_level":
                if content.get(key) != value:
                    match = False
                    break
            elif key == "content_type":
                if content.get(key) != value:
                    match = False
                    break
            elif key == "tags":
                content_tags = content.get("tags", [])
                if not any(tag.lower() in [t.lower() for t in content_tags] for tag in value):
                    match = False
                    break
            elif key == "course_id":
                if content.get(key) != value:
                    match = False
                    break
        
        if match:
            results.append(content)
    
    return results

def get_learner_analytics(learner_id: str):
    """Get comprehensive analytics for a learner"""
    learner = read_learner(learner_id)
    if not learner:
        return None
    
    activities = learner.get("activities", [])
    progress_logs = read_progress_logs(learner_id)
    engagements = get_engagement_metrics(learner_id)
    
    # Calculate analytics
    total_time = sum([a.get("duration", 0) for a in activities])
    avg_score = sum([a.get("score", 0) for a in activities if a.get("score")]) / max(len([a for a in activities if a.get("score")]), 1)
    
    # Engagement patterns
    engagement_types = {}
    for engagement in engagements:
        metrics = engagement.get("metrics", {})
        completion = metrics.get("completion_percentage", 0)
        if completion > 0.8:
            engagement_types["high_engagement"] = engagement_types.get("high_engagement", 0) + 1
        elif completion > 0.5:
            engagement_types["medium_engagement"] = engagement_types.get("medium_engagement", 0) + 1
        else:
            engagement_types["low_engagement"] = engagement_types.get("low_engagement", 0) + 1
    
    return {
        "learner_id": learner_id,
        "total_study_time": round(total_time, 2),
        "average_score": round(avg_score, 2),
        "total_activities": len(activities),
        "total_engagements": len(engagements),
        "engagement_distribution": engagement_types,
        "recent_milestones": len(progress_logs),
        "learning_velocity": get_progress_summary(learner_id).get("learning_velocity", 0) if get_progress_summary(learner_id) else 0
    }