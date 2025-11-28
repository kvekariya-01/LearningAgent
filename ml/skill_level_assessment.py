"""
Skill Level Assessment System
Evaluates learner proficiency across different subjects and skills
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from utils.crud_operations import read_learner, read_engagements, get_engagement_metrics

class SkillLevelAssessment:
    """Comprehensive skill level assessment for learners"""
    
    def __init__(self):
        self.skill_levels = {
            "beginner": {"min_score": 0, "max_score": 40, "description": "Basic understanding"},
            "novice": {"min_score": 40, "max_score": 60, "description": "Some experience"},
            "intermediate": {"min_score": 60, "max_score": 80, "description": "Good competency"},
            "advanced": {"min_score": 80, "max_score": 90, "description": "Strong proficiency"},
            "expert": {"min_score": 90, "max_score": 100, "description": "Mastery level"}
        }
        
        self.assessment_criteria = {
            "test_performance": 0.4,      # 40% weight
            "assignment_quality": 0.25,   # 25% weight  
            "engagement_quality": 0.2,    # 20% weight
            "consistency": 0.1,           # 10% weight
            "improvement_rate": 0.05      # 5% weight
        }
    
    def assess_skill_levels(self, learner_id: str) -> Dict[str, any]:
        """Assess all skill levels for a learner"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            engagements = get_engagement_metrics(learner_id)
            
            if not activities:
                return self._get_default_assessment(learner_id)
            
            # Extract skill assessments
            skill_assessments = {}
            
            # Group activities by subject/skill area
            subject_performance = self._analyze_subject_performance(activities, engagements)
            
            for subject, performance_data in subject_performance.items():
                level_assessment = self._assess_single_skill(subject, performance_data)
                skill_assessments[subject] = level_assessment
            
            # Overall assessment
            overall_assessment = self._calculate_overall_assessment(skill_assessments)
            
            return {
                "learner_id": learner_id,
                "skill_assessments": skill_assessments,
                "overall_assessment": overall_assessment,
                "assessment_timestamp": datetime.now().isoformat(),
                "confidence_score": self._calculate_assessment_confidence(skill_assessments)
            }
            
        except Exception as e:
            return {"error": f"Assessment failed: {str(e)}"}
    
    def _analyze_subject_performance(self, activities: List[Dict], engagements: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze performance by subject/skill area"""
        subject_performance = defaultdict(list)
        
        # Extract subject from course_id or infer from activity type
        for activity in activities:
            subject = self._extract_subject_from_activity(activity)
            if subject:
                subject_performance[subject].append({
                    "score": activity.get("score"),
                    "duration": activity.get("duration", 0),
                    "type": activity.get("activity_type"),
                    "timestamp": activity.get("timestamp"),
                    "quality_indicator": self._assess_activity_quality(activity)
                })
        
        return dict(subject_performance)
    
    def _extract_subject_from_activity(self, activity: Dict) -> Optional[str]:
        """Extract subject area from activity data"""
        activity_type = activity.get("activity_type", "").lower()
        
        # Map activity types to subjects
        subject_mapping = {
            "python": ["python", "programming", "code"],
            "data_science": ["data", "analytics", "statistics", "machine_learning"],
            "web_development": ["web", "html", "css", "javascript", "frontend"],
            "mathematics": ["math", "algebra", "calculus", "statistics"],
            "language": ["english", "writing", "communication", "language"],
            "design": ["design", "ux", "ui", "graphics", "visual"],
            "business": ["business", "management", "finance", "marketing"],
            "science": ["science", "physics", "chemistry", "biology"]
        }
        
        for subject, keywords in subject_mapping.items():
            if any(keyword in activity_type for keyword in keywords):
                return subject
        
        # Default fallback
        return "general" if activity_type else None
    
    def _assess_activity_quality(self, activity: Dict) -> float:
        """Assess the quality of an activity completion"""
        score = activity.get("score")
        duration = activity.get("duration", 0)
        
        if score is None:
            return 0.5  # Neutral quality for activities without scores
        
        # Normalize score to 0-1
        normalized_score = score / 100.0
        
        # Consider duration efficiency (faster completion with good score = higher quality)
        if duration > 0:
            # Ideal completion time varies by activity type
            ideal_time = self._get_ideal_completion_time(activity.get("activity_type", ""))
            if duration <= ideal_time:
                duration_factor = 1.2  # Bonus for efficient completion
            else:
                duration_factor = max(0.5, ideal_time / duration)  # Penalty for slow completion
        else:
            duration_factor = 1.0
        
        quality = normalized_score * duration_factor
        return min(quality, 1.0)
    
    def _get_ideal_completion_time(self, activity_type: str) -> float:
        """Get ideal completion time for activity type (in minutes)"""
        time_mapping = {
            "quiz": 15,
            "test": 45,
            "assignment": 90,
            "project": 300,  # 5 hours
            "module": 60,
            "video": 30,
            "reading": 20
        }
        
        for activity_key, ideal_time in time_mapping.items():
            if activity_key in activity_type.lower():
                return ideal_time
        
        return 60  # Default 1 hour
    
    def _assess_single_skill(self, subject: str, performance_data: List[Dict]) -> Dict[str, any]:
        """Assess skill level for a single subject"""
        if not performance_data:
            return self._get_default_skill_assessment(subject)
        
        scores = [p["score"] for p in performance_data if p["score"] is not None]
        quality_scores = [p["quality_indicator"] for p in performance_data]
        
        if not scores:
            return self._get_default_skill_assessment(subject)
        
        # Calculate assessment criteria
        test_performance = np.mean(scores) if scores else 0
        assignment_quality = np.mean(quality_scores) * 100 if quality_scores else 0
        
        # Engagement quality from engagement metrics
        engagement_quality = self._assess_engagement_quality(subject, performance_data)
        
        # Consistency (low standard deviation = high consistency)
        consistency = max(0, 100 - np.std(scores)) if len(scores) > 1 else 50
        
        # Improvement rate
        improvement_rate = self._calculate_improvement_rate(performance_data)
        
        # Weighted overall score
        overall_score = (
            test_performance * self.assessment_criteria["test_performance"] +
            assignment_quality * self.assessment_criteria["assignment_quality"] +
            engagement_quality * self.assessment_criteria["engagement_quality"] +
            consistency * self.assessment_criteria["consistency"] +
            improvement_rate * self.assessment_criteria["improvement_rate"]
        )
        
        # Determine level
        level = self._determine_skill_level(overall_score)
        
        return {
            "subject": subject,
            "level": level,
            "score": round(overall_score, 2),
            "criteria_breakdown": {
                "test_performance": round(test_performance, 2),
                "assignment_quality": round(assignment_quality, 2),
                "engagement_quality": round(engagement_quality, 2),
                "consistency": round(consistency, 2),
                "improvement_rate": round(improvement_rate, 2)
            },
            "assessment_details": {
                "total_activities": len(performance_data),
                "score_range": [min(scores), max(scores)] if scores else [0, 0],
                "average_quality": round(np.mean(quality_scores), 3) if quality_scores else 0,
                "recent_performance": self._get_recent_performance(performance_data)
            }
        }
    
    def _assess_engagement_quality(self, subject: str, performance_data: List[Dict]) -> float:
        """Assess engagement quality for a subject"""
        # This would integrate with engagement metrics
        # For now, return a default score based on activity quality
        if not performance_data:
            return 50.0
        
        quality_scores = [p["quality_indicator"] for p in performance_data]
        return np.mean(quality_scores) * 100 if quality_scores else 50.0
    
    def _calculate_improvement_rate(self, performance_data: List[Dict]) -> float:
        """Calculate improvement rate over time"""
        if len(performance_data) < 2:
            return 50.0  # Neutral improvement rate
        
        # Sort by timestamp
        sorted_data = sorted(performance_data, key=lambda x: x.get("timestamp", ""))
        
        # Compare first half vs second half
        mid_point = len(sorted_data) // 2
        first_half = [p["score"] for p in sorted_data[:mid_point] if p["score"] is not None]
        second_half = [p["score"] for p in sorted_data[mid_point:] if p["score"] is not None]
        
        if not first_half or not second_half:
            return 50.0
        
        first_avg = np.mean(first_half)
        second_avg = np.mean(second_half)
        
        if first_avg == 0:
            return 50.0
        
        improvement_rate = ((second_avg - first_avg) / first_avg) * 100
        return max(0, min(100, improvement_rate + 50))  # Normalize to 0-100
    
    def _get_recent_performance(self, performance_data: List[Dict], recent_count: int = 3) -> Dict[str, float]:
        """Get recent performance metrics"""
        if not performance_data:
            return {"recent_avg": 0, "recent_trend": "stable"}
        
        recent_data = sorted(performance_data, key=lambda x: x.get("timestamp", ""))[-recent_count:]
        recent_scores = [p["score"] for p in recent_data if p["score"] is not None]
        
        if not recent_scores:
            return {"recent_avg": 0, "recent_trend": "stable"}
        
        recent_avg = np.mean(recent_scores)
        
        # Determine trend
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0] * 1.1:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0] * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {"recent_avg": round(recent_avg, 2), "recent_trend": trend}
    
    def _determine_skill_level(self, score: float) -> str:
        """Determine skill level based on score"""
        for level, criteria in self.skill_levels.items():
            if criteria["min_score"] <= score <= criteria["max_score"]:
                return level
        return "beginner"  # Default level
    
    def _calculate_overall_assessment(self, skill_assessments: Dict) -> Dict[str, any]:
        """Calculate overall skill assessment"""
        if not skill_assessments:
            return self._get_default_overall_assessment()
        
        # Calculate weighted average across all subjects
        total_score = 0
        total_weight = 0
        
        for subject, assessment in skill_assessments.items():
            # Weight by number of activities in that subject
            activity_count = assessment["assessment_details"]["total_activities"]
            weight = max(1, activity_count)
            
            total_score += assessment["score"] * weight
            total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 0
        overall_level = self._determine_skill_level(overall_score)
        
        # Identify strongest and weakest areas
        if skill_assessments:
            strongest_subject = max(skill_assessments.items(), key=lambda x: x[1]["score"])
            weakest_subject = min(skill_assessments.items(), key=lambda x: x[1]["score"])
        else:
            strongest_subject = ("general", {"score": 0})
            weakest_subject = ("general", {"score": 0})
        
        return {
            "overall_level": overall_level,
            "overall_score": round(overall_score, 2),
            "strongest_subject": {
                "subject": strongest_subject[0],
                "score": strongest_subject[1]["score"]
            },
            "weakest_subject": {
                "subject": weakest_subject[0], 
                "score": weakest_subject[1]["score"]
            },
            "total_subjects_assessed": len(skill_assessments),
            "readiness_for_advancement": self._assess_advancement_readiness(skill_assessments)
        }
    
    def _assess_advancement_readiness(self, skill_assessments: Dict) -> Dict[str, any]:
        """Assess readiness for advancement to next level"""
        if not skill_assessments:
            return {"ready": False, "reason": "No assessment data"}
        
        # Check if most subjects are at intermediate+ level
        intermediate_plus = sum(1 for assessment in skill_assessments.values() 
                              if assessment["level"] in ["intermediate", "advanced", "expert"])
        
        readiness_ratio = intermediate_plus / len(skill_assessments)
        
        if readiness_ratio >= 0.7:
            return {"ready": True, "level": "advanced", "confidence": round(readiness_ratio * 100, 1)}
        elif readiness_ratio >= 0.5:
            return {"ready": True, "level": "intermediate", "confidence": round(readiness_ratio * 100, 1)}
        else:
            return {"ready": False, "level": "beginner", "confidence": round(readiness_ratio * 100, 1)}
    
    def _calculate_assessment_confidence(self, skill_assessments: Dict) -> float:
        """Calculate confidence in the assessment based on data quality"""
        if not skill_assessments:
            return 0.3
        
        total_activities = sum(assessment["assessment_details"]["total_activities"] 
                             for assessment in skill_assessments.values())
        
        # Confidence increases with more data
        if total_activities >= 20:
            confidence = 0.9
        elif total_activities >= 10:
            confidence = 0.7
        elif total_activities >= 5:
            confidence = 0.5
        else:
            confidence = 0.3
        
        return confidence
    
    def _get_default_skill_assessment(self, subject: str) -> Dict[str, any]:
        """Default assessment for new subjects"""
        return {
            "subject": subject,
            "level": "beginner",
            "score": 25.0,
            "criteria_breakdown": {
                "test_performance": 25.0,
                "assignment_quality": 25.0,
                "engagement_quality": 25.0,
                "consistency": 25.0,
                "improvement_rate": 25.0
            },
            "assessment_details": {
                "total_activities": 0,
                "score_range": [0, 0],
                "average_quality": 0.5,
                "recent_performance": {"recent_avg": 0, "recent_trend": "stable"}
            },
            "note": "Insufficient data for assessment"
        }
    
    def _get_default_assessment(self, learner_id: str) -> Dict[str, any]:
        """Default assessment for learners with no data"""
        return {
            "learner_id": learner_id,
            "skill_assessments": {},
            "overall_assessment": self._get_default_overall_assessment(),
            "assessment_timestamp": datetime.now().isoformat(),
            "confidence_score": 0.2,
            "note": "New learner - assessment pending activity completion"
        }
    
    def _get_default_overall_assessment(self) -> Dict[str, any]:
        """Default overall assessment"""
        return {
            "overall_level": "beginner",
            "overall_score": 25.0,
            "strongest_subject": {"subject": "general", "score": 25.0},
            "weakest_subject": {"subject": "general", "score": 25.0},
            "total_subjects_assessed": 0,
            "readiness_for_advancement": {"ready": False, "level": "beginner", "confidence": 0.0}
        }

# Global assessment instance
skill_assessment = SkillLevelAssessment()

def assess_learner_skills(learner_id: str) -> Dict[str, any]:
    """Main function to assess learner skill levels"""
    try:
        return skill_assessment.assess_skill_levels(learner_id)
    except Exception as e:
        return {
            "learner_id": learner_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the assessment system
    assessment = SkillLevelAssessment()
    
    # Sample test data
    sample_activities = [
        {"activity_type": "python_quiz", "score": 85, "duration": 20, "timestamp": "2024-01-15T10:00:00"},
        {"activity_type": "python_assignment", "score": 78, "duration": 90, "timestamp": "2024-01-16T14:00:00"},
        {"activity_type": "data_science_test", "score": 92, "duration": 60, "timestamp": "2024-01-17T09:00:00"},
    ]
    
    result = assessment._analyze_subject_performance(sample_activities, [])
    print(f"Sample Assessment: {result}")