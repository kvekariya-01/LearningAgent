from datetime import datetime, timezone
from utils.crud_operations import read_learners, read_progress_logs, calculate_cumulative_engagement_score
from typing import Dict, List, Any
import statistics

# Disable pandas for Hugging Face deployment
PANDAS_AVAILABLE = False
print("Using fallback analytics without pandas")

def calculate_learner_velocity(learner_data: Dict) -> float:
    """
    Calculate learning velocity = total_modules_completed / time_active_in_weeks
    """
    activities = learner_data.get("activities", [])
    if not activities:
        return 0.0

    # Count module completions
    modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])

    # Calculate time active
    timestamps = [a["timestamp"] for a in activities]
    if len(timestamps) < 2:
        return 0.0  # Not enough data for velocity calculation

    # Convert timestamps to datetime objects
    try:
        timestamps_dt = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
        first_activity = min(timestamps_dt)
        last_activity = max(timestamps_dt)

        # Calculate weeks active (minimum 0.1 to avoid division by zero)
        weeks_active = max((last_activity - first_activity).days / 7, 0.1)

        velocity = modules_completed / weeks_active
        return round(velocity, 2)
    except Exception:
        return 0.0

def get_learner_insights(learner_id: str) -> Dict[str, Any]:
    """
    Generate comprehensive insights for a single learner
    """
    from utils.crud_operations import read_learner

    learner_data = read_learner(learner_id)
    if not learner_data:
        return {"error": "Learner not found"}

    activities = learner_data.get("activities", [])
    progress_logs = read_progress_logs(learner_id)

    # Basic metrics
    total_activities = len(activities)
    modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])

    # Score analysis
    scores = [a.get("score") for a in activities if a.get("score") is not None]
    avg_score = round(statistics.mean(scores), 2) if scores else 0.0
    min_score = min(scores) if scores else 0.0
    max_score = max(scores) if scores else 0.0

    # Time analysis
    total_time = sum(a.get("duration", 0) for a in activities)
    avg_session_time = round(total_time / total_activities, 2) if total_activities > 0 else 0.0

    # Velocity calculation
    velocity = calculate_learner_velocity(learner_data)

    # Engagement score
    engagement_score = calculate_cumulative_engagement_score(learner_id)

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

    return {
        "learner_id": learner_id,
        "basic_metrics": {
            "total_activities": total_activities,
            "modules_completed": modules_completed,
            "total_time_spent": round(total_time, 2),
            "average_session_time": avg_session_time
        },
        "performance_metrics": {
            "average_score": avg_score,
            "min_score": min_score,
            "max_score": max_score,
            "score_trend": score_trend,
            "engagement_score": engagement_score
        },
        "learning_velocity": velocity,
        "activity_distribution": activity_types,
        "recent_milestones": progress_logs[-3:] if progress_logs else []
    }

def get_cohort_comparison(learner_id: str = None, group_by: str = "learning_style") -> Dict[str, Any]:
    """
    Compare learner performance against cohort using fallback implementation
    """
    learners = read_learners()
    if not learners:
        return {"error": "No learners found"}

    # Convert to DataFrame or dict list
    df_data = []
    for learner in learners:
        activities = learner.get("activities", [])
        if not activities:
            continue

        # Calculate metrics for each learner
        scores = [a.get("score") for a in activities if a.get("score") is not None]
        modules_completed = len([a for a in activities if a.get("activity_type") == "module_completed"])
        total_time = sum(a.get("duration", 0) for a in activities)
        velocity = calculate_learner_velocity(learner)
        engagement = calculate_cumulative_engagement_score(learner["id"])

        df_data.append({
            "learner_id": learner["id"],
            "name": learner.get("name", "Unknown"),
            "age": learner.get("age", 0),
            "gender": learner.get("gender", "unknown"),
            "learning_style": learner.get("learning_style", "unknown"),
            "total_activities": len(activities),
            "modules_completed": modules_completed,
            "total_time": total_time,
            "avg_score": statistics.mean(scores) if scores else 0.0,
            "velocity": velocity,
            "engagement_score": engagement
        })

    if not df_data:
        return {"error": "No activity data available"}

    # Fallback implementation without pandas
    from collections import defaultdict
    grouped_data = defaultdict(list)

    for learner in df_data:
        group_value = learner[group_by]
        grouped_data[group_value].append(learner)

    cohort_comparison = []
    for group_value, group_learners in grouped_data.items():
        if not group_learners:
            continue

        # Calculate group statistics manually
        avg_scores = [l['avg_score'] for l in group_learners]
        velocities = [l['velocity'] for l in group_learners]
        engagements = [l['engagement_score'] for l in group_learners]
        modules = [l['modules_completed'] for l in group_learners]
        times = [l['total_time'] for l in group_learners]
        activities = [l['total_activities'] for l in group_learners]

        def calc_stats(values):
            if not values:
                return {"mean": 0.0, "std": 0.0}
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0.0
            return {"mean": round(mean_val, 2), "std": round(std_val, 2)}

        stats = {
            group_by: group_value,
            "avg_score_mean": calc_stats(avg_scores)["mean"],
            "avg_score_std": calc_stats(avg_scores)["std"],
            "velocity_mean": calc_stats(velocities)["mean"],
            "velocity_std": calc_stats(velocities)["std"],
            "engagement_score_mean": calc_stats(engagements)["mean"],
            "engagement_score_std": calc_stats(engagements)["std"],
            "modules_completed_mean": calc_stats(modules)["mean"],
            "modules_completed_std": calc_stats(modules)["std"],
            "total_time_mean": calc_stats(times)["mean"],
            "total_time_std": calc_stats(times)["std"],
            "total_activities_mean": calc_stats(activities)["mean"],
            "total_activities_std": calc_stats(activities)["std"],
            "count": len(group_learners)
        }
        cohort_comparison.append(stats)

    individual_comparison = None
    if learner_id:
        learner_data = next((l for l in df_data if l['learner_id'] == learner_id), None)
        if learner_data:
            group_value = learner_data[group_by]
            group_learners = grouped_data.get(group_value, [])

            if group_learners:
                cohort_avg = {
                    'avg_score': round(statistics.mean([l['avg_score'] for l in group_learners]), 2),
                    'velocity': round(statistics.mean([l['velocity'] for l in group_learners]), 2),
                    'engagement_score': round(statistics.mean([l['engagement_score'] for l in group_learners]), 2),
                    'modules_completed': round(statistics.mean([l['modules_completed'] for l in group_learners]), 2),
                    'total_time': round(statistics.mean([l['total_time'] for l in group_learners]), 2)
                }

                # Calculate percentile rankings
                all_scores = [l['avg_score'] for l in df_data]
                all_velocities = [l['velocity'] for l in df_data]
                all_engagements = [l['engagement_score'] for l in df_data]

                individual_comparison = {
                    "learner_id": learner_id,
                    "group_value": group_value,
                    "learner_metrics": {
                        "avg_score": learner_data['avg_score'],
                        "velocity": learner_data['velocity'],
                        "engagement_score": learner_data['engagement_score'],
                        "modules_completed": learner_data['modules_completed'],
                        "total_time": learner_data['total_time']
                    },
                    "cohort_averages": cohort_avg,
                    "percentile_rankings": {
                        "avg_score": round(sum(1 for s in all_scores if learner_data['avg_score'] > s) / len(all_scores) * 100, 1),
                        "velocity": round(sum(1 for v in all_velocities if learner_data['velocity'] > v) / len(all_velocities) * 100, 1),
                        "engagement_score": round(sum(1 for e in all_engagements if learner_data['engagement_score'] > e) / len(all_engagements) * 100, 1)
                    }
                }

    return {
        "cohort_comparison": cohort_comparison,
        "total_learners": len(df_data),
        "group_by": group_by,
        "individual_comparison": individual_comparison
    }

def get_analytics_summary() -> Dict[str, Any]:
    """
    Generate overall analytics summary for instructor dashboard
    """
    learners = read_learners()
    if not learners:
        return {"error": "No learners found"}

    # Calculate system-wide metrics
    total_learners = len(learners)
    active_learners = len([l for l in learners if l.get("activities")])

    all_scores = []
    all_velocities = []
    all_engagements = []

    for learner in learners:
        activities = learner.get("activities", [])
        if not activities:
            continue

        scores = [a.get("score") for a in activities if a.get("score") is not None]
        if scores:
            all_scores.extend(scores)

        velocity = calculate_learner_velocity(learner)
        all_velocities.append(velocity)

        engagement = calculate_cumulative_engagement_score(learner["id"])
        all_engagements.append(engagement)

    # Calculate aggregates
    avg_score_system = round(statistics.mean(all_scores), 2) if all_scores else 0.0
    avg_velocity_system = round(statistics.mean(all_velocities), 2) if all_velocities else 0.0
    avg_engagement_system = round(statistics.mean(all_engagements), 2) if all_engagements else 0.0

    return {
        "system_overview": {
            "total_learners": total_learners,
            "active_learners": active_learners,
            "activity_rate": round(active_learners / total_learners * 100, 1) if total_learners > 0 else 0
        },
        "performance_averages": {
            "average_score": avg_score_system,
            "average_velocity": avg_velocity_system,
            "average_engagement": avg_engagement_system
        },
        "distribution_stats": {
            "score_std": round(statistics.stdev(all_scores), 2) if len(all_scores) > 1 else 0.0,
            "velocity_std": round(statistics.stdev(all_velocities), 2) if len(all_velocities) > 1 else 0.0,
            "engagement_std": round(statistics.stdev(all_engagements), 2) if len(all_engagements) > 1 else 0.0
        }
    }