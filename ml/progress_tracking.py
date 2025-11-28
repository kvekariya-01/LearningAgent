"""
Progress Tracking Modules
Comprehensive system for tracking learner progress, milestones, and engagement
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from utils.crud_operations import read_learner, read_progress_logs, get_engagement_metrics

class MilestoneTracker:
    """Tracks learning milestones and achievements"""
    
    def __init__(self):
        self.milestone_definitions = {
            "first_activity": {
                "name": "Getting Started",
                "description": "Complete your first learning activity",
                "threshold": 1,
                "points": 10,
                "category": "engagement"
            },
            "week_streak": {
                "name": "Consistent Learner",
                "description": "Study for 7 consecutive days",
                "threshold": 7,
                "points": 25,
                "category": "consistency"
            },
            "ten_activities": {
                "name": "Active Learner",
                "description": "Complete 10 learning activities",
                "threshold": 10,
                "points": 50,
                "category": "engagement"
            },
            "perfect_score": {
                "name": "Perfectionist",
                "description": "Achieve a perfect score (100%)",
                "threshold": 100,
                "points": 30,
                "category": "performance"
            },
            "subject_mastery": {
                "name": "Subject Master",
                "description": "Achieve 85%+ average in a subject",
                "threshold": 85,
                "points": 100,
                "category": "mastery"
            },
            "rapid_learner": {
                "name": "Speed Learner",
                "description": "Complete 5 activities in one day",
                "threshold": 5,
                "points": 40,
                "category": "velocity"
            },
            "persistent_learner": {
                "name": "Persistent",
                "description": "Continue learning after initial difficulty",
                "threshold": 50,  # 50% score improvement
                "points": 60,
                "category": "resilience"
            },
            "diverse_learner": {
                "name": "Versatile Mind",
                "description": "Engage with 5 different content types",
                "threshold": 5,
                "points": 45,
                "category": "diversity"
            }
        }
    
    def track_learner_milestones(self, learner_id: str) -> Dict[str, any]:
        """Track all milestones for a learner"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            if not activities:
                return self._get_initial_milestone_status(learner_id)
            
            # Evaluate each milestone
            milestone_status = {}
            new_milestones = []
            
            for milestone_key, milestone_def in self.milestone_definitions.items():
                status = self._evaluate_milestone(learner_id, milestone_key, milestone_def, activities)
                milestone_status[milestone_key] = status
                
                if status["achieved"] and not status["previously_achieved"]:
                    new_milestones.append(milestone_key)
            
            # Calculate overall progress
            total_points = sum(status["points"] for status in milestone_status.values() if status["achieved"])
            completion_rate = len([s for s in milestone_status.values() if s["achieved"]]) / len(milestone_status)
            
            # Generate milestone recommendations
            recommendations = self._generate_milestone_recommendations(milestone_status)
            
            return {
                "learner_id": learner_id,
                "milestone_status": milestone_status,
                "progress_summary": {
                    "total_milestones": len(self.milestone_definitions),
                    "achieved_milestones": len([s for s in milestone_status.values() if s["achieved"]]),
                    "completion_rate": round(completion_rate * 100, 1),
                    "total_points": total_points,
                    "new_milestones": new_milestones
                },
                "recommendations": recommendations,
                "tracking_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Milestone tracking failed: {str(e)}"}
    
    def _evaluate_milestone(self, learner_id: str, milestone_key: str, milestone_def: Dict, activities: List[Dict]) -> Dict[str, any]:
        """Evaluate if a specific milestone has been achieved"""
        
        if milestone_key == "first_activity":
            achieved = len(activities) >= 1
            progress = min(len(activities), milestone_def["threshold"])
            
        elif milestone_key == "week_streak":
            achieved, progress = self._calculate_streak(activities, milestone_def["threshold"])
            
        elif milestone_key == "ten_activities":
            achieved = len(activities) >= milestone_def["threshold"]
            progress = min(len(activities), milestone_def["threshold"])
            
        elif milestone_key == "perfect_score":
            scores = [a.get("score", 0) for a in activities if a.get("score") is not None]
            achieved = any(score >= milestone_def["threshold"] for score in scores)
            progress = max(scores) if scores else 0
            
        elif milestone_key == "subject_mastery":
            achieved, progress = self._check_subject_mastery(activities, milestone_def["threshold"])
            
        elif milestone_key == "rapid_learner":
            achieved, progress = self._check_rapid_learning(activities, milestone_def["threshold"])
            
        elif milestone_key == "persistent_learner":
            achieved, progress = self._check_persistence(activities, milestone_def["threshold"])
            
        elif milestone_key == "diverse_learner":
            achieved, progress = self._check_content_diversity(activities, milestone_def["threshold"])
            
        else:
            achieved = False
            progress = 0
        
        # Check if previously achieved (simplified - in real implementation, check historical data)
        previously_achieved = achieved and len(activities) > milestone_def["threshold"]
        
        return {
            "achieved": achieved,
            "progress": progress,
            "threshold": milestone_def["threshold"],
            "points": milestone_def["points"],
            "category": milestone_def["category"],
            "previously_achieved": previously_achieved,
            "completion_percentage": round((progress / milestone_def["threshold"]) * 100, 1)
        }
    
    def _calculate_streak(self, activities: List[Dict], threshold: int) -> Tuple[bool, int]:
        """Calculate consecutive day streak"""
        if not activities:
            return False, 0
        
        # Extract unique days with activities
        activity_days = set()
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00')).date()
                activity_days.add(activity_date)
            except (ValueError, TypeError):
                continue
        
        if not activity_days:
            return False, 0
        
        # Sort days and find longest streak
        sorted_days = sorted(activity_days)
        current_streak = 1
        max_streak = 1
        
        for i in range(1, len(sorted_days)):
            if (sorted_days[i] - sorted_days[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak >= threshold, max_streak
    
    def _check_subject_mastery(self, activities: List[Dict], threshold: float) -> Tuple[bool, float]:
        """Check if learner has achieved mastery in any subject"""
        if not activities:
            return False, 0
        
        # Group activities by subject
        subject_scores = defaultdict(list)
        for activity in activities:
            subject = self._extract_subject(activity)
            if subject and activity.get("score") is not None:
                subject_scores[subject].append(activity["score"])
        
        # Check each subject
        max_mastery = 0
        for subject, scores in subject_scores.items():
            if len(scores) >= 3:  # Need at least 3 scores
                avg_score = np.mean(scores)
                max_mastery = max(max_mastery, avg_score)
        
        return max_mastery >= threshold, max_mastery
    
    def _check_rapid_learning(self, activities: List[Dict], threshold: int) -> Tuple[bool, int]:
        """Check if learner completed many activities in one day"""
        if not activities:
            return False, 0
        
        # Count activities per day
        daily_counts = Counter()
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00')).date()
                daily_counts[activity_date] += 1
            except (ValueError, TypeError):
                continue
        
        max_daily_count = max(daily_counts.values()) if daily_counts else 0
        return max_daily_count >= threshold, max_daily_count
    
    def _check_persistence(self, activities: List[Dict], threshold: float) -> Tuple[bool, float]:
        """Check if learner improved after initial difficulty"""
        if len(activities) < 4:
            return False, 0
        
        # Get scores in chronological order
        scored_activities = [a for a in activities if a.get("score") is not None]
        if len(scored_activities) < 4:
            return False, 0
        
        # Compare first quarter vs last quarter
        quarter_size = len(scored_activities) // 4
        first_quarter_avg = np.mean([a["score"] for a in scored_activities[:quarter_size]])
        last_quarter_avg = np.mean([a["score"] for a in scored_activities[-quarter_size:]])
        
        improvement = ((last_quarter_avg - first_quarter_avg) / first_quarter_avg * 100) if first_quarter_avg > 0 else 0
        
        return improvement >= threshold, improvement
    
    def _check_content_diversity(self, activities: List[Dict], threshold: int) -> Tuple[bool, int]:
        """Check diversity of content types"""
        if not activities:
            return False, 0
        
        # Extract content types
        content_types = set()
        for activity in activities:
            activity_type = activity.get("activity_type", "").lower()
            # Categorize content types
            if any(keyword in activity_type for keyword in ["video", "watch"]):
                content_types.add("video")
            elif any(keyword in activity_type for keyword in ["quiz", "test"]):
                content_types.add("assessment")
            elif any(keyword in activity_type for keyword in ["assignment", "project"]):
                content_types.add("project")
            elif any(keyword in activity_type for keyword in ["reading", "article"]):
                content_types.add("reading")
            elif any(keyword in activity_type for keyword in ["discussion", "forum"]):
                content_types.add("discussion")
        
        diversity_count = len(content_types)
        return diversity_count >= threshold, diversity_count
    
    def _extract_subject(self, activity: Dict) -> Optional[str]:
        """Extract subject from activity"""
        activity_type = activity.get("activity_type", "").lower()
        
        subject_mapping = {
            "programming": ["python", "code", "programming"],
            "data_science": ["data", "analytics", "statistics"],
            "web_development": ["web", "html", "css"],
            "mathematics": ["math", "algebra", "calculus"],
            "language": ["english", "writing"]
        }
        
        for subject, keywords in subject_mapping.items():
            if any(keyword in activity_type for keyword in keywords):
                return subject
        
        return "general"
    
    def _generate_milestone_recommendations(self, milestone_status: Dict) -> List[str]:
        """Generate recommendations for achieving upcoming milestones"""
        recommendations = []
        
        for milestone_key, status in milestone_status.items():
            if not status["achieved"] and status["completion_percentage"] > 50:
                if milestone_key == "week_streak":
                    recommendations.append(f"Continue your daily study habit to achieve the week streak milestone")
                elif milestone_key == "ten_activities":
                    remaining = status["threshold"] - status["progress"]
                    recommendations.append(f"Complete {remaining} more activities to become an 'Active Learner'")
                elif milestone_key == "perfect_score":
                    recommendations.append("Focus on thorough understanding to achieve a perfect score")
                elif milestone_key == "subject_mastery":
                    recommendations.append("Practice more in your strongest subject to achieve mastery")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _get_initial_milestone_status(self, learner_id: str) -> Dict[str, any]:
        """Initial milestone status for new learners"""
        milestone_status = {}
        for key, definition in self.milestone_definitions.items():
            milestone_status[key] = {
                "achieved": False,
                "progress": 0,
                "threshold": definition["threshold"],
                "points": definition["points"],
                "category": definition["category"],
                "previously_achieved": False,
                "completion_percentage": 0.0
            }
        
        return {
            "learner_id": learner_id,
            "milestone_status": milestone_status,
            "progress_summary": {
                "total_milestones": len(self.milestone_definitions),
                "achieved_milestones": 0,
                "completion_rate": 0.0,
                "total_points": 0,
                "new_milestones": []
            },
            "recommendations": ["Complete your first activity to start tracking milestones"],
            "tracking_timestamp": datetime.now().isoformat()
        }


class EngagementScoreCalculator:
    """Calculates comprehensive engagement scores"""
    
    def __init__(self):
        self.engagement_weights = {
            "activity_frequency": 0.25,      # How often learner engages
            "session_quality": 0.25,         # Quality of learning sessions
            "completion_rate": 0.20,         # Rate of completing activities
            "interaction_depth": 0.15,       # Depth of interaction with content
            "consistency": 0.15             # Consistency of engagement over time
        }
    
    def calculate_comprehensive_engagement(self, learner_id: str) -> Dict[str, any]:
        """Calculate comprehensive engagement score"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            engagements = get_engagement_metrics(learner_id)
            
            if not activities:
                return self._get_initial_engagement_assessment(learner_id)
            
            # Calculate individual engagement components
            activity_frequency = self._calculate_activity_frequency(activities)
            session_quality = self._calculate_session_quality(activities, engagements)
            completion_rate = self._calculate_completion_rate(activities)
            interaction_depth = self._calculate_interaction_depth(activities, engagements)
            consistency = self._calculate_consistency(activities)
            
            # Calculate weighted overall score
            overall_score = (
                activity_frequency * self.engagement_weights["activity_frequency"] +
                session_quality * self.engagement_weights["session_quality"] +
                completion_rate * self.engagement_weights["completion_rate"] +
                interaction_depth * self.engagement_weights["interaction_depth"] +
                consistency * self.engagement_weights["consistency"]
            )
            
            # Determine engagement level
            engagement_level = self._determine_engagement_level(overall_score)
            
            # Generate engagement insights
            insights = self._generate_engagement_insights({
                "activity_frequency": activity_frequency,
                "session_quality": session_quality,
                "completion_rate": completion_rate,
                "interaction_depth": interaction_depth,
                "consistency": consistency
            })
            
            return {
                "learner_id": learner_id,
                "overall_engagement_score": round(overall_score * 100, 2),  # Convert to 0-100 scale
                "engagement_level": engagement_level,
                "component_scores": {
                    "activity_frequency": round(activity_frequency * 100, 2),
                    "session_quality": round(session_quality * 100, 2),
                    "completion_rate": round(completion_rate * 100, 2),
                    "interaction_depth": round(interaction_depth * 100, 2),
                    "consistency": round(consistency * 100, 2)
                },
                "insights": insights,
                "recommendations": self._generate_engagement_recommendations(overall_score),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Engagement calculation failed: {str(e)}"}
    
    def _calculate_activity_frequency(self, activities: List[Dict]) -> float:
        """Calculate how frequently learner engages with content"""
        if len(activities) < 2:
            return 0.5  # Neutral score for new learners
        
        # Sort activities by timestamp
        sorted_activities = sorted(activities, key=lambda x: x.get("timestamp", ""))
        
        # Calculate time span
        try:
            first_date = datetime.fromisoformat(sorted_activities[0].get("timestamp", "").replace('Z', '+00:00'))
            last_date = datetime.fromisoformat(sorted_activities[-1].get("timestamp", "").replace('Z', '+00:00'))
            time_span_days = (last_date - first_date).days
            
            if time_span_days == 0:
                return 1.0  # All activities in one day = high frequency
            
            # Calculate activities per week
            activities_per_week = len(activities) / (time_span_days / 7)
            
            # Normalize: ideal frequency is 3-5 activities per week
            if 3 <= activities_per_week <= 5:
                return 1.0
            elif 1 <= activities_per_week < 3:
                return activities_per_week / 3
            elif 5 < activities_per_week <= 10:
                return 0.8  # Slight penalty for overactivity
            else:
                return max(0.2, 0.5 - abs(activities_per_week - 4) * 0.1)
                
        except (ValueError, TypeError):
            return 0.5
    
    def _calculate_session_quality(self, activities: List[Dict], engagements: List[Dict]) -> float:
        """Calculate quality of learning sessions"""
        scores = [a.get("score", 0) for a in activities if a.get("score") is not None]
        
        if not scores:
            return 0.5
        
        # Base score from average performance
        avg_score = np.mean(scores)
        base_quality = avg_score / 100.0
        
        # Adjust based on score consistency
        if len(scores) > 1:
            score_variance = np.var(scores)
            consistency_bonus = max(0, 1 - (score_variance / 1000))  # Penalty for high variance
        else:
            consistency_bonus = 0.5
        
        # Adjust based on durations (optimal session length)
        durations = [a.get("duration", 0) for a in activities if a.get("duration")]
        if durations:
            avg_duration = np.mean(durations)
            # Optimal duration is 45-90 minutes
            if 45 <= avg_duration <= 90:
                duration_bonus = 1.0
            elif 30 <= avg_duration < 45 or 90 < avg_duration <= 120:
                duration_bonus = 0.7
            else:
                duration_bonus = 0.4
        else:
            duration_bonus = 0.5
        
        # Factor in engagement quality from engagement metrics
        engagement_quality = 0.5
        if engagements:
            completion_percentages = [e.get("metrics", {}).get("completion_percentage", 0) for e in engagements]
            if completion_percentages:
                engagement_quality = np.mean(completion_percentages)
        
        # Weighted combination
        quality_score = (
            base_quality * 0.4 +
            consistency_bonus * 0.3 +
            duration_bonus * 0.2 +
            engagement_quality * 0.1
        )
        
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_completion_rate(self, activities: List[Dict]) -> float:
        """Calculate rate of completing activities successfully"""
        if not activities:
            return 0.0
        
        # Count successful completions (score >= 60)
        successful_completions = len([a for a in activities if a.get("score", 0) >= 60])
        total_activities = len(activities)
        
        return successful_completions / total_activities
    
    def _calculate_interaction_depth(self, activities: List[Dict], engagements: List[Dict]) -> float:
        """Calculate depth of interaction with content"""
        # Base interaction score from activity types
        interaction_indicators = {
            "quiz": 0.8,
            "assignment": 0.9,
            "project": 1.0,
            "discussion": 0.7,
            "video": 0.4,
            "reading": 0.3,
            "test": 0.9
        }
        
        interaction_scores = []
        for activity in activities:
            activity_type = activity.get("activity_type", "").lower()
            base_score = 0.5  # Default score
            
            for indicator, score in interaction_indicators.items():
                if indicator in activity_type:
                    base_score = max(base_score, score)
                    break
            
            interaction_scores.append(base_score)
        
        # Enhance with engagement metrics
        if engagements:
            completion_rates = [e.get("metrics", {}).get("completion_percentage", 0) for e in engagements]
            if completion_rates:
                avg_completion = np.mean(completion_rates)
                interaction_scores = [score * avg_completion for score in interaction_scores]
        
        return np.mean(interaction_scores) if interaction_scores else 0.5
    
    def _calculate_consistency(self, activities: List[Dict]) -> float:
        """Calculate consistency of engagement over time"""
        if len(activities) < 3:
            return 0.5
        
        # Analyze temporal patterns
        weekly_activity = self._analyze_weekly_patterns(activities)
        daily_variance = self._analyze_daily_variance(activities)
        
        # Combine consistency factors
        consistency_score = (weekly_activity + daily_variance) / 2
        
        return max(0.0, min(1.0, consistency_score))
    
    def _analyze_weekly_patterns(self, activities: List[Dict]) -> float:
        """Analyze consistency across weeks"""
        weekly_counts = defaultdict(int)
        
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                week_key = activity_date.isocalendar()[:2]  # Year and week number
                weekly_counts[week_key] += 1
            except (ValueError, TypeError):
                continue
        
        if len(weekly_counts) < 2:
            return 0.5
        
        # Calculate variance in weekly activity
        activity_counts = list(weekly_counts.values())
        mean_activity = np.mean(activity_counts)
        variance = np.var(activity_counts)
        
        # Lower variance = higher consistency
        if mean_activity == 0:
            return 0.5
        
        consistency = max(0, 1 - (variance / (mean_activity * mean_activity)))
        return consistency
    
    def _analyze_daily_variance(self, activities: List[Dict]) -> float:
        """Analyze variance in daily activity patterns"""
        daily_counts = defaultdict(int)
        
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                daily_counts[activity_date.date()] += 1
            except (ValueError, TypeError):
                continue
        
        if len(daily_counts) < 2:
            return 0.5
        
        # Calculate days with activity vs total days
        total_days_span = (max(daily_counts.keys()) - min(daily_counts.keys())).days + 1
        active_days = len(daily_counts)
        
        daily_consistency = active_days / total_days_span
        
        # Bonus for regular daily patterns
        if daily_consistency >= 0.7:
            consistency_bonus = 1.0
        elif daily_consistency >= 0.5:
            consistency_bonus = 0.8
        else:
            consistency_bonus = 0.6
        
        return consistency_bonus
    
    def _determine_engagement_level(self, score: float) -> Dict[str, str]:
        """Determine engagement level based on score"""
        if score >= 0.8:
            return {"level": "highly_engaged", "description": "Excellent engagement patterns"}
        elif score >= 0.6:
            return {"level": "well_engaged", "description": "Good engagement with room for improvement"}
        elif score >= 0.4:
            return {"level": "moderately_engaged", "description": "Average engagement, could be improved"}
        else:
            return {"level": "low_engagement", "description": "Low engagement, needs attention"}
    
    def _generate_engagement_insights(self, component_scores: Dict[str, float]) -> List[str]:
        """Generate insights about engagement patterns"""
        insights = []
        
        if component_scores["activity_frequency"] < 0.4:
            insights.append("Consider increasing study frequency to improve engagement")
        
        if component_scores["session_quality"] < 0.5:
            insights.append("Focus on deeper understanding during study sessions")
        
        if component_scores["completion_rate"] < 0.6:
            insights.append("Work on completing activities to strengthen knowledge")
        
        if component_scores["interaction_depth"] < 0.5:
            insights.append("Try more interactive content types for deeper learning")
        
        if component_scores["consistency"] < 0.4:
            insights.append("Establish a more consistent study schedule")
        
        # Positive insights
        if component_scores["activity_frequency"] >= 0.7:
            insights.append("Great consistency in your study habits")
        
        if component_scores["session_quality"] >= 0.8:
            insights.append("High-quality learning sessions")
        
        return insights[:3]  # Return top 3 insights
    
    def _generate_engagement_recommendations(self, overall_score: float) -> List[str]:
        """Generate recommendations to improve engagement"""
        recommendations = []
        
        if overall_score < 0.5:
            recommendations.extend([
                "Set small, achievable daily learning goals",
                "Choose content that matches your interests",
                "Track your progress to stay motivated"
            ])
        elif overall_score < 0.7:
            recommendations.extend([
                "Vary your learning activities to maintain interest",
                "Increase session duration for deeper learning",
                "Join study groups or discussion forums"
            ])
        else:
            recommendations.extend([
                "Consider mentoring other learners",
                "Explore advanced topics in your areas of strength",
                "Share your learning experience with others"
            ])
        
        return recommendations[:3]
    
    def _get_initial_engagement_assessment(self, learner_id: str) -> Dict[str, any]:
        """Initial engagement assessment for new learners"""
        return {
            "learner_id": learner_id,
            "overall_engagement_score": 0.0,
            "engagement_level": {
                "level": "new_learner",
                "description": "Just starting the learning journey"
            },
            "component_scores": {
                "activity_frequency": 0.0,
                "session_quality": 0.0,
                "completion_rate": 0.0,
                "interaction_depth": 0.0,
                "consistency": 0.0
            },
            "insights": ["Complete your first activity to start tracking engagement"],
            "recommendations": ["Start with short, focused study sessions", "Choose topics you find interesting"],
            "calculation_timestamp": datetime.now().isoformat()
        }


# Global instances
milestone_tracker = MilestoneTracker()
engagement_calculator = EngagementScoreCalculator()

def track_learner_milestones(learner_id: str) -> Dict[str, any]:
    """Main function to track learner milestones"""
    return milestone_tracker.track_learner_milestones(learner_id)

def calculate_engagement_score(learner_id: str) -> Dict[str, any]:
    """Main function to calculate engagement score"""
    return engagement_calculator.calculate_comprehensive_engagement(learner_id)

if __name__ == "__main__":
    # Test the progress tracking systems
    tracker = MilestoneTracker()
    calculator = EngagementScoreCalculator()
    
    print("Progress Tracking Modules initialized")
    
    # Sample test
    sample_activities = [
        {"activity_type": "python_quiz", "score": 85, "duration": 30, "timestamp": "2024-01-15T10:00:00"},
        {"activity_type": "python_assignment", "score": 78, "duration": 90, "timestamp": "2024-01-16T14:00:00"},
        {"activity_type": "data_science_video", "score": 92, "duration": 45, "timestamp": "2024-01-17T09:00:00"}
    ]
    
    print("Sample Milestone Evaluation:")
    first_activity_status = tracker._evaluate_milestone("test", "first_activity", 
                                                       tracker.milestone_definitions["first_activity"], 
                                                       sample_activities)
    print(f"First Activity: {first_activity_status}")