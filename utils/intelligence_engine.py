"""
Enhanced Intelligence Engine for Learning Agent
Implements advanced backend intelligence features:
- Motivational Messaging System
- Weekly Progress Report Generator
- Strength/Weakness Analysis
- Intervention Trigger Logic
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import statistics
from models.intervention import Intervention
from models.progress import ProgressLog
from utils.crud_operations import read_learner, create_intervention, read_interventions, read_progress_logs
from utils.analytics import calculate_learner_velocity


class MotivationalMessagingSystem:
    """Advanced motivational messaging system based on learner performance and behavior"""
    
    @staticmethod
    def generate_motivational_message(learner_data: Dict, recent_score: Optional[float] = None, 
                                     context: str = "general") -> Dict[str, Any]:
        """Generate personalized motivational messages based on learning context"""
        
        activities = learner_data.get("activities", [])
        learner_name = learner_data.get("name", "Learner")
        
        # Calculate recent performance metrics
        scores = [a.get("score") for a in activities if a.get("score") is not None]
        recent_scores = scores[-5:] if len(scores) >= 5 else scores
        
        avg_recent_score = statistics.mean(recent_scores) if recent_scores else 0
        score_trend = "stable"
        
        if len(recent_scores) >= 3:
            first_half = statistics.mean(recent_scores[:len(recent_scores)//2])
            second_half = statistics.mean(recent_scores[len(recent_scores)//2:])
            if second_half > first_half + 5:
                score_trend = "improving"
            elif second_half < first_half - 5:
                score_trend = "declining"
        
        # Calculate learning velocity
        velocity = calculate_learner_velocity(learner_data)
        
        # Generate contextual messages
        messages = []
        
        # 1. Performance-based messages
        if recent_score is not None:
            if recent_score >= 90:
                messages.append({
                    "type": "achievement",
                    "message": f"🌟 Outstanding performance, {learner_name}! You scored {recent_score} - you're absolutely crushing it!",
                    "priority": "high",
                    "trigger": "high_score"
                })
            elif recent_score >= 80:
                messages.append({
                    "type": "encouragement", 
                    "message": f"💪 Great job, {learner_name}! {recent_score} is a solid performance. Keep pushing forward!",
                    "priority": "medium",
                    "trigger": "good_score"
                })
            elif recent_score >= 60:
                messages.append({
                    "type": "motivation",
                    "message": f"📈 Nice effort, {learner_name}! Every step counts. With {recent_score}, you're making progress!",
                    "priority": "medium", 
                    "trigger": "acceptable_score"
                })
            else:
                messages.append({
                    "type": "support",
                    "message": f"🤝 Don't give up, {learner_name}! {recent_score} is just a starting point. You've got this!",
                    "priority": "high",
                    "trigger": "low_score"
                })
        
        # 2. Trend-based messages
        if score_trend == "improving":
            messages.append({
                "type": "momentum",
                "message": f"🚀 Incredible, {learner_name}! Your scores are trending upward - you're on fire!",
                "priority": "high",
                "trigger": "improving_trend"
            })
        elif score_trend == "declining":
            messages.append({
                "type": "reassurance",
                "message": f"🌱 Everyone has ups and downs, {learner_name}. Remember: great learners bounce back stronger!",
                "priority": "high",
                "trigger": "declining_trend"
            })
        
        # 3. Velocity-based messages
        if velocity >= 2.0:
            messages.append({
                "type": "speed_boost",
                "message": f"⚡ Lightning fast learning, {learner_name}! You're completing modules at an impressive rate!",
                "priority": "medium",
                "trigger": "high_velocity"
            })
        elif velocity < 0.5 and len(activities) > 3:
            messages.append({
                "type": "patience",
                "message": f"🧘 Quality over speed, {learner_name}! Taking your time to understand concepts deeply is valuable.",
                "priority": "medium",
                "trigger": "low_velocity"
            })
        
        # 4. Context-specific messages
        if context == "struggling":
            messages.append({
                "type": "resilience",
                "message": f"💪 Tough times don't last, but tough learners like {learner_name} do!",
                "priority": "high",
                "trigger": "struggling_context"
            })
        elif context == "milestone":
            messages.append({
                "type": "celebration",
                "message": f"🎉 Milestone achieved, {learner_name}! This is what consistent effort looks like!",
                "priority": "high",
                "trigger": "milestone"
            })
        
        # 5. Encouragement for new learners
        if len(activities) <= 2:
            messages.append({
                "type": "welcome",
                "message": f"🌟 Welcome to your learning journey, {learner_name}! Every expert was once a beginner.",
                "priority": "medium",
                "trigger": "new_learner"
            })
        
        # Select the most appropriate message based on priority
        if messages:
            best_message = max(messages, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]])
            return {
                "message": best_message["message"],
                "type": best_message["type"],
                "priority": best_message["priority"],
                "trigger": best_message["trigger"],
                "context": context,
                "available_messages": len(messages)
            }
        
        # Default motivational message
        return {
            "message": f"Keep up the great work, {learner_name}! Your learning journey is unique and valuable.",
            "type": "general",
            "priority": "low",
            "trigger": "default",
            "context": context,
            "available_messages": 0
        }
    
    @staticmethod
    def trigger_motivational_intervention(learner_id: str, context: str = "general", 
                                        recent_score: Optional[float] = None) -> Dict[str, Any]:
        """Trigger and save a motivational intervention"""
        
        learner_data = read_learner(learner_id)
        if not learner_data:
            return {"error": "Learner not found"}
        
        message_data = MotivationalMessagingSystem.generate_motivational_message(
            learner_data, recent_score, context
        )
        
        # Create intervention record
        intervention = Intervention(
            learner_id=learner_id,
            intervention_type="motivational_message",
            message=message_data["message"],
            triggered_by=message_data["trigger"],
            metadata={
                "message_type": message_data["type"],
                "priority": message_data["priority"],
                "context": context,
                "recent_score": recent_score
            }
        )
        
        result = create_intervention(intervention)
        if result:
            return {
                "success": True,
                "intervention_id": intervention.id,
                "message": message_data["message"],
                "type": message_data["type"],
                "priority": message_data["priority"]
            }
        
        return {"error": "Failed to create intervention"}


class WeeklyProgressReportGenerator:
    """Generate comprehensive weekly progress reports for learners"""
    
    @staticmethod
    def generate_weekly_report(learner_id: str, week_start_date: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive weekly progress report"""
        
        learner_data = read_learner(learner_id)
        if not learner_data:
            return {"error": "Learner not found"}
        
        # Calculate week boundaries
        if week_start_date:
            week_start = datetime.fromisoformat(week_start_date.replace('Z', '+00:00'))
        else:
            # Default to current week's Monday
            today = datetime.now(timezone.utc)
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=7)
        
        # Filter activities for the week
        activities = learner_data.get("activities", [])
        weekly_activities = []
        
        for activity in activities:
            try:
                activity_time = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                if week_start <= activity_time < week_end:
                    weekly_activities.append(activity)
            except:
                continue
        
        # Calculate weekly metrics
        weekly_activities.sort(key=lambda x: x.get("timestamp", ""))
        
        # Activity counts
        total_activities = len(weekly_activities)
        module_completions = len([a for a in weekly_activities if a.get("activity_type") == "module_completed"])
        assessments = len([a for a in weekly_activities if "test" in a.get("activity_type", "") or "quiz" in a.get("activity_type", "")])
        
        # Time analysis
        total_time = sum(a.get("duration", 0) for a in weekly_activities)
        avg_session_time = round(total_time / total_activities, 2) if total_activities > 0 else 0
        
        # Score analysis for the week
        weekly_scores = [a.get("score") for a in weekly_activities if a.get("score") is not None]
        if weekly_scores:
            avg_score = round(statistics.mean(weekly_scores), 2)
            score_improvement = weekly_scores[-1] - weekly_scores[0] if len(weekly_scores) > 1 else 0
            best_score = max(weekly_scores)
            worst_score = min(weekly_scores)
        else:
            avg_score = 0
            score_improvement = 0
            best_score = 0
            worst_score = 0
        
        # Learning velocity for the week
        weekly_velocity = round(module_completions / 1.0, 2)  # 1 week
        
        # Activity type distribution
        activity_distribution = {}
        for activity in weekly_activities:
            act_type = activity.get("activity_type", "Unknown")
            activity_distribution[act_type] = activity_distribution.get(act_type, 0) + 1
        
        # Compare with previous week if data exists
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start
        
        prev_weekly_activities = []
        for activity in activities:
            try:
                activity_time = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                if prev_week_start <= activity_time < prev_week_end:
                    prev_weekly_activities.append(activity)
            except:
                continue
        
        # Previous week comparisons
        prev_total_activities = len(prev_weekly_activities)
        prev_total_time = sum(a.get("duration", 0) for a in prev_weekly_activities)
        prev_scores = [a.get("score") for a in prev_weekly_activities if a.get("score") is not None]
        prev_avg_score = round(statistics.mean(prev_scores), 2) if prev_scores else 0
        
        # Calculate trends
        activity_trend = "increased" if total_activities > prev_total_activities else "decreased" if total_activities < prev_total_activities else "stable"
        time_trend = "increased" if total_time > prev_total_time else "decreased" if total_time < prev_total_time else "stable"
        score_trend = "improved" if avg_score > prev_avg_score else "declined" if avg_score < prev_avg_score else "stable"
        
        # Generate insights and recommendations
        insights = []
        recommendations = []
        
        if total_activities == 0:
            insights.append("No activities recorded this week")
            recommendations.append("Consider scheduling regular study sessions")
        else:
            if activity_trend == "increased":
                insights.append("Great job! Your activity level increased this week")
            
            if avg_score >= 85:
                insights.append("Excellent performance this week!")
                recommendations.append("You're ready for more challenging content")
            elif avg_score < 60:
                insights.append("Performance needs attention this week")
                recommendations.append("Focus on reviewing fundamentals")
            
            if module_completions >= 3:
                insights.append("Strong module completion rate")
            elif module_completions == 0:
                recommendations.append("Try to complete at least one module this week")
        
        # Generate motivational message
        motivational_msg = MotivationalMessagingSystem.generate_motivational_message(
            learner_data, None, "weekly_report"
        )
        
        # Construct comprehensive report
        report = {
            "learner_id": learner_id,
            "learner_name": learner_data.get("name"),
            "report_period": {
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "week_number": week_start.isocalendar()[1],
                "year": week_start.year
            },
            "weekly_summary": {
                "total_activities": total_activities,
                "module_completions": module_completions,
                "assessments_taken": assessments,
                "total_study_time": round(total_time, 2),
                "average_session_time": avg_session_time,
                "learning_velocity": weekly_velocity
            },
            "performance_metrics": {
                "average_score": avg_score,
                "best_score": best_score,
                "worst_score": worst_score,
                "score_improvement": score_improvement,
                "total_score_points": sum(weekly_scores) if weekly_scores else 0
            },
            "activity_breakdown": activity_distribution,
            "trends": {
                "activity_trend": activity_trend,
                "time_trend": time_trend,
                "score_trend": score_trend,
                "comparisons": {
                    "previous_week_activities": prev_total_activities,
                    "previous_week_time": round(prev_total_time, 2),
                    "previous_week_avg_score": prev_avg_score
                }
            },
            "insights": insights,
            "recommendations": recommendations,
            "motivational_message": motivational_msg["message"],
            "achievements": WeeklyProgressReportGenerator._generate_achievements(weekly_activities, avg_score),
            "next_week_focus": WeeklyProgressReportGenerator._generate_next_week_focus(
                total_activities, avg_score, module_completions
            )
        }
        
        return report
    
    @staticmethod
    def _generate_achievements(weekly_activities: List[Dict], avg_score: float) -> List[str]:
        """Generate achievements based on weekly performance"""
        achievements = []
        
        module_completions = len([a for a in weekly_activities if a.get("activity_type") == "module_completed"])
        
        if module_completions >= 5:
            achievements.append("🏆 Module Master - Completed 5+ modules this week")
        elif module_completions >= 3:
            achievements.append("📚 Module Champion - Completed 3+ modules this week")
        elif module_completions >= 1:
            achievements.append("📖 Module Starter - Completed your first module this week")
        
        if avg_score >= 95:
            achievements.append("🌟 Perfect Week - Average score above 95%")
        elif avg_score >= 85:
            achievements.append("💪 Strong Performer - Average score above 85%")
        elif avg_score >= 70:
            achievements.append("📈 Consistent Learner - Average score above 70%")
        
        total_time = sum(a.get("duration", 0) for a in weekly_activities)
        if total_time >= 600:  # 10 hours
            achievements.append("⏰ Study Marathon - Studied 10+ hours this week")
        elif total_time >= 300:  # 5 hours
            achievements.append("📚 Dedicated Student - Studied 5+ hours this week")
        
        assessments = len([a for a in weekly_activities if "test" in a.get("activity_type", "") or "quiz" in a.get("activity_type", "")])
        if assessments >= 3:
            achievements.append("🎯 Assessment Ace - Completed 3+ assessments this week")
        
        return achievements
    
    @staticmethod
    def _generate_next_week_focus(total_activities: int, avg_score: float, module_completions: int) -> List[str]:
        """Generate focus areas for next week"""
        focus_areas = []
        
        if total_activities < 3:
            focus_areas.append("Increase study frequency - aim for at least 3 sessions this week")
        
        if avg_score < 70:
            focus_areas.append("Review fundamental concepts to improve scores")
        
        if module_completions < 1:
            focus_areas.append("Set a goal to complete at least one module this week")
        
        if avg_score >= 85:
            focus_areas.append("Challenge yourself with more advanced topics")
        
        if not focus_areas:
            focus_areas.append("Maintain your current excellent learning pace")
            focus_areas.append("Continue exploring new topics that interest you")
        
        return focus_areas[:3]  # Limit to top 3 focus areas


class StrengthWeaknessAnalyzer:
    """Advanced strength and weakness analysis for learners"""
    
    @staticmethod
    def analyze_strengths_weaknesses(learner_id: str) -> Dict[str, Any]:
        """Analyze learner strengths and weaknesses based on performance data"""
        
        learner_data = read_learner(learner_id)
        if not learner_data:
            return {"error": "Learner not found"}
        
        activities = learner_data.get("activities", [])
        if not activities:
            return {
                "learner_id": learner_id,
                "strengths": [],
                "weaknesses": [],
                "recommendations": ["Start with basic activities to build your learning profile"],
                "analysis": "insufficient_data"
            }
        
        # Analyze performance by activity type
        activity_scores = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            score = activity.get("score")
            
            if score is not None:
                if activity_type not in activity_scores:
                    activity_scores[activity_type] = []
                activity_scores[activity_type].append(score)
        
        # Calculate averages and identify patterns
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyze by activity type
        for activity_type, scores in activity_scores.items():
            if len(scores) >= 2:  # Need at least 2 scores for meaningful analysis
                avg_score = statistics.mean(scores)
                score_variance = statistics.variance(scores) if len(scores) > 1 else 0
                
                activity_display = activity_type.replace("_", " ").title()
                
                if avg_score >= 80:
                    strengths.append({
                        "area": activity_display,
                        "average_score": round(avg_score, 2),
                        "consistency": "high" if score_variance < 50 else "medium",
                        "evidence": f"Average score of {avg_score:.1f} across {len(scores)} activities"
                    })
                elif avg_score < 60:
                    weaknesses.append({
                        "area": activity_display,
                        "average_score": round(avg_score, 2),
                        "consistency": "high" if score_variance < 50 else "medium",
                        "evidence": f"Average score of {avg_score:.1f} across {len(scores)} activities"
                    })
        
        # Analyze by time patterns
        learning_patterns = StrengthWeaknessAnalyzer._analyze_learning_patterns(activities)
        
        # Generate personalized recommendations
        if strengths:
            recommendations.append(f"Leverage your strengths in {', '.join([s['area'] for s in strengths[:2]])}")
        
        if weaknesses:
            recommendations.append(f"Focus extra practice on {', '.join([w['area'] for w in weaknesses[:2]])}")
        
        # Learning style insights
        learning_style = learner_data.get("learning_style", "Mixed")
        if learning_style != "Mixed":
            recommendations.append(f"Continue using your {learning_style} learning style - it appears to work well for you")
        
        # Velocity-based recommendations
        velocity = calculate_learner_velocity(learner_data)
        if velocity > 2.0:
            recommendations.append("Consider taking on more challenging content to match your fast learning pace")
        elif velocity < 0.5:
            recommendations.append("Focus on understanding concepts deeply before moving forward")
        
        # Additional recommendations based on patterns
        recommendations.extend(learning_patterns.get("recommendations", []))
        
        return {
            "learner_id": learner_id,
            "learner_name": learner_data.get("name"),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "learning_patterns": learning_patterns,
            "recommendations": recommendations[:5],  # Limit to top 5
            "analysis_summary": {
                "total_activity_types": len(activity_scores),
                "strong_areas": len(strengths),
                "weak_areas": len(weaknesses),
                "learning_velocity": velocity,
                "dominant_learning_style": learning_style
            },
            "detailed_metrics": {
                "activity_type_performance": {
                    atype: {
                        "average": round(statistics.mean(scores), 2),
                        "count": len(scores),
                        "min_score": min(scores),
                        "max_score": max(scores)
                    }
                    for atype, scores in activity_scores.items()
                    if len(scores) >= 2
                }
            }
        }
    
    @staticmethod
    def _analyze_learning_patterns(activities: List[Dict]) -> Dict[str, Any]:
        """Analyze learning patterns from activity data"""
        
        if not activities:
            return {"patterns": [], "recommendations": []}
        
        patterns = []
        recommendations = []
        
        # Time of day analysis
        hour_performance = {}
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                hour = timestamp.hour
                score = activity.get("score")
                
                if score is not None:
                    if hour not in hour_performance:
                        hour_performance[hour] = []
                    hour_performance[hour].append(score)
            except:
                continue
        
        if hour_performance:
            best_hour = max(hour_performance.keys(), 
                          key=lambda h: statistics.mean(hour_performance[h]) if hour_performance[h] else 0)
            worst_hour = min(hour_performance.keys(), 
                           key=lambda h: statistics.mean(hour_performance[h]) if hour_performance[h] else 0)
            
            if len(hour_performance) > 1:
                patterns.append(f"Performance varies by time of day - best at {best_hour}:00, worst at {worst_hour}:00")
                recommendations.append(f"Schedule important study sessions around {best_hour}:00 when you perform best")
        
        # Session length analysis
        session_lengths = [a.get("duration", 0) for a in activities if a.get("duration", 0) > 0]
        if session_lengths:
            avg_session = statistics.mean(session_lengths)
            if avg_session > 120:  # 2+ hours
                patterns.append("Prefers longer study sessions")
                recommendations.append("Consider breaking long sessions into shorter, focused periods")
            elif avg_session < 30:  # Less than 30 minutes
                patterns.append("Prefers shorter, frequent study sessions")
                recommendations.append("Continue with frequent short sessions - they're working well for you")
        
        # Activity frequency analysis
        if len(activities) >= 5:
            recent_activities = activities[-5:]
            activity_types = [a.get("activity_type") for a in recent_activities]
            
            if len(set(activity_types)) == 1:
                patterns.append("Tends to focus on one type of activity")
                recommendations.append("Try mixing different activity types for well-rounded learning")
        
        return {
            "patterns": patterns,
            "recommendations": recommendations
        }


# Integration functions for Flask routes
def get_enhanced_intelligence_features():
    """Get all enhanced intelligence features for integration with Flask routes"""
    return {
        "motivational_messaging": MotivationalMessagingSystem,
        "weekly_reports": WeeklyProgressReportGenerator,
        "strength_weakness_analysis": StrengthWeaknessAnalyzer
    }


if __name__ == "__main__":
    # Test the intelligence engine
    print("Enhanced Intelligence Engine - Test Suite")
    print("=" * 50)
    
    # Test with sample data
    sample_learner = {
        "id": "test-learner",
        "name": "Test Learner",
        "age": 25,
        "gender": "Other",
        "learning_style": "Visual",
        "preferences": ["Python", "Data Science"],
        "activities": [
            {"activity_type": "module_completed", "timestamp": "2024-01-15T10:00:00", "score": 85, "duration": 60},
            {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 92, "duration": 30},
            {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 78, "duration": 45}
        ]
    }
    
    # Test motivational messaging
    print("Testing Motivational Messaging System...")
    msg = MotivationalMessagingSystem.generate_motivational_message(sample_learner, 88, "general")
    print(f"Generated message: {msg['message']}")
    print(f"Message type: {msg['type']}")
    print()
    
    # Test weekly report generation
    print("Testing Weekly Progress Report Generator...")
    # This would require a real database call, so we'll just show the structure
    print("Weekly report structure:")
    print("- Learner summary metrics")
    print("- Performance analysis")
    print("- Activity breakdown")
    print("- Trends and insights")
    print("- Motivational messages")
    print("- Achievements and next week focus")
    print()
    
    # Test strength/weakness analysis
    print("Testing Strength/Weakness Analyzer...")
    print("Analysis includes:")
    print("- Performance by activity type")
    print("- Learning pattern identification")
    print("- Personalized recommendations")
    print("- Detailed metrics")
    print()
    
    print("Enhanced Intelligence Engine test completed!")