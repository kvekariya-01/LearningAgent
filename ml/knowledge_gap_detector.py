"""
Knowledge Gap Detector
Identifies gaps in learner's knowledge and recommends targeted interventions
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from utils.crud_operations import read_learner, read_content, read_engagements

class KnowledgeGapDetector:
    """Detects knowledge gaps and learning weaknesses"""
    
    def __init__(self):
        self.gap_severity_weights = {
            "critical": 1.0,    # Major gap affecting progression
            "significant": 0.7, # Important gap 
            "minor": 0.3,       # Small gap that may resolve naturally
            "potential": 0.1    # Emerging gap to monitor
        }
        
        self.skill_interdependencies = {
            "python": ["data_structures", "algorithms", "oop"],
            "data_science": ["statistics", "python", "visualization"],
            "web_development": ["html", "css", "javascript"],
            "mathematics": ["algebra", "calculus", "statistics"],
            "machine_learning": ["python", "statistics", "mathematics"]
        }
        
        self.knowledge_areas = {
            "programming": ["syntax", "logic", "debugging", "best_practices"],
            "data_science": ["statistics", "visualization", "modeling", "interpretation"],
            "mathematics": ["algebra", "calculus", "geometry", "statistics"],
            "language": ["vocabulary", "grammar", "composition", "comprehension"],
            "design": ["principles", "tools", "user_experience", "accessibility"]
        }
    
    def detect_knowledge_gaps(self, learner_id: str) -> Dict[str, any]:
        """Detect knowledge gaps for a learner"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            engagements = read_engagements()
            learner_engagements = [e for e in engagements if e.get("learner_id") == learner_id]
            
            if not activities:
                return self._get_initial_gap_assessment(learner_id)
            
            # Analyze performance patterns
            gap_analysis = self._analyze_performance_gaps(activities, learner_engagements)
            
            # Identify knowledge dependencies
            dependency_gaps = self._analyze_dependency_gaps(activities)
            
            # Detect learning progression issues
            progression_gaps = self._analyze_progression_gaps(activities)
            
            # Combine all gap types
            comprehensive_gaps = self._consolidate_gaps(gap_analysis, dependency_gaps, progression_gaps)
            
            # Generate recommendations
            recommendations = self._generate_gap_recommendations(comprehensive_gaps)
            
            return {
                "learner_id": learner_id,
                "gap_analysis": comprehensive_gaps,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_gaps_identified": len(comprehensive_gaps),
                "priority_gaps": [gap for gap in comprehensive_gaps if gap["severity"] in ["critical", "significant"]]
            }
            
        except Exception as e:
            return {"error": f"Gap detection failed: {str(e)}"}
    
    def _analyze_performance_gaps(self, activities: List[Dict], engagements: List[Dict]) -> List[Dict]:
        """Analyze performance-based gaps"""
        gaps = []
        
        # Group activities by subject/knowledge area
        subject_performance = defaultdict(list)
        
        for activity in activities:
            subject = self._extract_knowledge_area(activity)
            if subject:
                subject_performance[subject].append(activity)
        
        # Analyze each subject for performance gaps
        for subject, subject_activities in subject_performance.items():
            scores = [a.get("score", 0) for a in subject_activities if a.get("score") is not None]
            
            if not scores:
                continue
            
            avg_score = np.mean(scores)
            score_variance = np.var(scores) if len(scores) > 1 else 0
            recent_scores = [a.get("score", 0) for a in subject_activities[-3:] if a.get("score") is not None]
            recent_avg = np.mean(recent_scores) if recent_scores else avg_score
            
            # Detect different types of performance gaps
            if avg_score < 60:
                gaps.append({
                    "type": "performance_gap",
                    "subject": subject,
                    "knowledge_area": subject,
                    "severity": "critical" if avg_score < 40 else "significant",
                    "description": f"Low average performance in {subject} ({avg_score:.1f}%)",
                    "evidence": {
                        "average_score": avg_score,
                        "recent_average": recent_avg,
                        "score_variance": score_variance,
                        "activity_count": len(subject_activities)
                    },
                    "learning_objectives": self._get_subject_learning_objectives(subject)
                })
            
            # Detect performance inconsistency (high variance)
            if score_variance > 400 and len(scores) > 3:  # High variance (>20 points)
                gaps.append({
                    "type": "consistency_gap",
                    "subject": subject,
                    "knowledge_area": subject,
                    "severity": "significant",
                    "description": f"Inconsistent performance in {subject}",
                    "evidence": {
                        "score_variance": score_variance,
                        "min_score": min(scores),
                        "max_score": max(scores),
                        "coefficient_of_variation": np.sqrt(score_variance) / avg_score if avg_score > 0 else 0
                    },
                    "learning_objectives": ["consistency", "practice", "foundational_review"]
                })
            
            # Detect declining performance
            if len(recent_scores) >= 3:
                if recent_avg < avg_score * 0.8:  # 20% decline
                    gaps.append({
                        "type": "performance_decline",
                        "subject": subject,
                        "knowledge_area": subject,
                        "severity": "significant",
                        "description": f"Declining performance trend in {subject}",
                        "evidence": {
                            "overall_average": avg_score,
                            "recent_average": recent_avg,
                            "decline_percentage": ((avg_score - recent_avg) / avg_score * 100) if avg_score > 0 else 0
                        },
                        "learning_objectives": ["reinforcement", "review", "additional_practice"]
                    })
        
        return gaps
    
    def _analyze_dependency_gaps(self, activities: List[Dict]) -> List[Dict]:
        """Analyze gaps due to missing prerequisite knowledge"""
        gaps = []
        
        # Identify subjects being studied
        subjects_studied = set()
        for activity in activities:
            subject = self._extract_knowledge_area(activity)
            if subject:
                subjects_studied.add(subject)
        
        # Check for missing dependencies
        for subject in subjects_studied:
            if subject in self.skill_interdependencies:
                required_skills = self.skill_interdependencies[subject]
                
                # Check which required skills are weak or missing
                for required_skill in required_skills:
                    if required_skill not in subjects_studied:
                        gaps.append({
                            "type": "prerequisite_gap",
                            "subject": subject,
                            "knowledge_area": required_skill,
                            "severity": "critical",
                            "description": f"Missing prerequisite knowledge: {required_skill} for {subject}",
                            "evidence": {
                                "required_for": subject,
                                "missing_skill": required_skill,
                                "impact": f"May limit progress in {subject}"
                            },
                            "learning_objectives": [f"{required_skill}_fundamentals", "prerequisite_knowledge"]
                        })
        
        return gaps
    
    def _analyze_progression_gaps(self, activities: List[Dict]) -> List[Dict]:
        """Analyze gaps in learning progression"""
        gaps = []
        
        # Sort activities by timestamp
        sorted_activities = sorted(activities, key=lambda x: x.get("timestamp", ""))
        
        # Analyze activity type diversity
        activity_types = [a.get("activity_type", "") for a in sorted_activities]
        activity_type_counts = Counter(activity_types)
        
        # Detect over-reliance on certain activity types
        total_activities = len(activities)
        for activity_type, count in activity_type_counts.items():
            if count / total_activities > 0.7 and total_activities > 5:  # Over 70% one type
                gaps.append({
                    "type": "activity_diversity_gap",
                    "subject": "general",
                    "knowledge_area": "learning_methods",
                    "severity": "minor",
                    "description": f"Over-reliance on {activity_type} activities",
                    "evidence": {
                        "dominant_activity": activity_type,
                        "percentage": (count / total_activities) * 100,
                        "total_activities": total_activities
                    },
                    "learning_objectives": ["varied_practice", "different_learning_methods", "skill_diversification"]
                })
        
        # Detect lack of assessment activities
        assessment_activities = [a for a in activities if any(keyword in a.get("activity_type", "").lower() 
                               for keyword in ["quiz", "test", "exam", "assessment"])]
        
        if len(assessment_activities) / total_activities < 0.2 and total_activities > 10:
            gaps.append({
                "type": "assessment_gap",
                "subject": "general",
                "knowledge_area": "knowledge_verification",
                "severity": "significant",
                "description": "Insufficient assessment activities to measure learning",
                "evidence": {
                    "assessment_count": len(assessment_activities),
                    "total_activities": total_activities,
                    "assessment_percentage": (len(assessment_activities) / total_activities) * 100
                },
                "learning_objectives": ["knowledge_assessment", "progress_monitoring", "skill_validation"]
            })
        
        return gaps
    
    def _consolidate_gaps(self, performance_gaps: List[Dict], dependency_gaps: List[Dict], progression_gaps: List[Dict]) -> List[Dict]:
        """Consolidate all gap types into a comprehensive list"""
        all_gaps = performance_gaps + dependency_gaps + progression_gaps
        
        # Remove duplicate gaps of the same type for the same subject
        consolidated_gaps = []
        seen_gaps = set()
        
        for gap in all_gaps:
            gap_key = (gap["type"], gap["subject"], gap["knowledge_area"])
            if gap_key not in seen_gaps:
                seen_gaps.add(gap_key)
                consolidated_gaps.append(gap)
        
        # Sort by severity
        severity_order = {"critical": 4, "significant": 3, "minor": 2, "potential": 1}
        consolidated_gaps.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        return consolidated_gaps
    
    def _generate_gap_recommendations(self, gaps: List[Dict]) -> List[Dict]:
        """Generate specific recommendations for each gap"""
        recommendations = []
        
        for gap in gaps:
            recommendation = {
                "gap_type": gap["type"],
                "subject": gap["subject"],
                "priority": gap["severity"],
                "recommendations": [],
                "estimated_effort": self._estimate_remediation_effort(gap),
                "success_metrics": self._define_success_metrics(gap)
            }
            
            # Generate specific recommendations based on gap type
            if gap["type"] == "performance_gap":
                recommendation["recommendations"] = [
                    f"Review fundamental concepts in {gap['subject']}",
                    "Complete additional practice exercises",
                    "Seek additional support or tutoring",
                    "Break down complex topics into smaller chunks"
                ]
            
            elif gap["type"] == "prerequisite_gap":
                recommendation["recommendations"] = [
                    f"Complete prerequisite course in {gap['knowledge_area']}",
                    "Start with beginner-level materials",
                    "Use foundational learning resources",
                    "Practice basic concepts before advanced topics"
                ]
            
            elif gap["type"] == "consistency_gap":
                recommendation["recommendations"] = [
                    "Establish regular study schedule",
                    "Practice consistent daily review",
                    "Use spaced repetition techniques",
                    "Monitor progress more frequently"
                ]
            
            elif gap["type"] == "activity_diversity_gap":
                recommendation["recommendations"] = [
                    "Incorporate different types of learning activities",
                    "Balance theoretical and practical exercises",
                    "Include both individual and collaborative work",
                    "Try various learning modalities"
                ]
            
            elif gap["type"] == "assessment_gap":
                recommendation["recommendations"] = [
                    "Schedule regular quizzes and assessments",
                    "Use self-assessment tools",
                    "Track progress with milestone tests",
                    "Implement knowledge verification checkpoints"
                ]
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _estimate_remediation_effort(self, gap: Dict) -> Dict[str, any]:
        """Estimate effort required to address the gap"""
        base_effort = {
            "critical": {"hours": 20, "days": 10},
            "significant": {"hours": 12, "days": 6},
            "minor": {"hours": 6, "days": 3},
            "potential": {"hours": 3, "days": 2}
        }
        
        severity = gap["severity"]
        effort = base_effort.get(severity, base_effort["minor"])
        
        # Adjust based on gap type
        if gap["type"] == "prerequisite_gap":
            effort["hours"] *= 1.5  # Prerequisite gaps require more effort
        elif gap["type"] == "performance_decline":
            effort["hours"] *= 1.2
        
        return {
            "estimated_hours": effort["hours"],
            "estimated_days": effort["days"],
            "difficulty": "High" if severity == "critical" else "Medium" if severity == "significant" else "Low",
            "urgency": "Immediate" if severity == "critical" else "High" if severity == "significant" else "Normal"
        }
    
    def _define_success_metrics(self, gap: Dict) -> List[str]:
        """Define metrics to measure success in addressing the gap"""
        if gap["type"] == "performance_gap":
            return [
                "Achieve 70%+ average score in subject assessments",
                "Complete 3 practice exercises with 80%+ accuracy",
                "Demonstrate understanding in practical application"
            ]
        elif gap["type"] == "prerequisite_gap":
            return [
                "Complete prerequisite course with passing grade",
                "Pass foundational knowledge assessment",
                "Demonstrate basic competency in prerequisite skills"
            ]
        elif gap["type"] == "consistency_gap":
            return [
                "Maintain consistent study schedule for 2 weeks",
                "Reduce score variance by 50%",
                "Complete daily review exercises"
            ]
        else:
            return [
                "Demonstrate improvement in targeted areas",
                "Complete prescribed remediation activities",
                "Achieve competency benchmarks"
            ]
    
    def _extract_knowledge_area(self, activity: Dict) -> Optional[str]:
        """Extract knowledge area from activity"""
        activity_type = activity.get("activity_type", "").lower()
        
        # Map activity types to knowledge areas
        area_mapping = {
            "programming": ["python", "code", "programming", "algorithm"],
            "data_science": ["data", "analytics", "statistics", "machine_learning"],
            "web_development": ["web", "html", "css", "javascript", "frontend"],
            "mathematics": ["math", "algebra", "calculus", "statistics"],
            "language": ["english", "writing", "communication"],
            "design": ["design", "ux", "ui", "graphics"],
            "science": ["science", "physics", "chemistry", "biology"]
        }
        
        for area, keywords in area_mapping.items():
            if any(keyword in activity_type for keyword in keywords):
                return area
        
        return "general"
    
    def _get_subject_learning_objectives(self, subject: str) -> List[str]:
        """Get learning objectives for a subject"""
        objectives = {
            "programming": ["syntax_mastery", "problem_solving", "debugging", "best_practices"],
            "data_science": ["statistical_analysis", "data_visualization", "modeling", "interpretation"],
            "mathematics": ["conceptual_understanding", "problem_solving", "application", "proof_techniques"],
            "language": ["vocabulary", "grammar", "composition", "comprehension"],
            "design": ["principles", "tools", "user_experience", "accessibility"]
        }
        
        return objectives.get(subject, ["fundamental_concepts", "practical_application"])
    
    def _get_initial_gap_assessment(self, learner_id: str) -> Dict[str, any]:
        """Initial gap assessment for new learners"""
        return {
            "learner_id": learner_id,
            "gap_analysis": [],
            "recommendations": [
                {
                    "gap_type": "initial_assessment",
                    "subject": "general",
                    "priority": "potential",
                    "recommendations": [
                        "Complete initial skill assessment",
                        "Establish baseline performance metrics",
                        "Identify learning preferences and style"
                    ],
                    "estimated_effort": {"estimated_hours": 2, "estimated_days": 1, "difficulty": "Low", "urgency": "Normal"},
                    "success_metrics": ["Complete initial assessment", "Establish baseline", "Set learning goals"]
                }
            ],
            "analysis_timestamp": datetime.now().isoformat(),
            "total_gaps_identified": 0,
            "priority_gaps": [],
            "note": "New learner - comprehensive gap analysis pending activity completion"
        }

# Global detector instance
knowledge_gap_detector = KnowledgeGapDetector()

def detect_learning_gaps(learner_id: str) -> Dict[str, any]:
    """Main function to detect knowledge gaps"""
    try:
        return knowledge_gap_detector.detect_knowledge_gaps(learner_id)
    except Exception as e:
        return {
            "learner_id": learner_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the gap detector
    detector = KnowledgeGapDetector()
    
    # Sample activities showing knowledge gaps
    sample_activities = [
        {"activity_type": "python_quiz", "score": 45, "timestamp": "2024-01-15T10:00:00"},  # Low performance
        {"activity_type": "machine_learning_test", "score": 85, "timestamp": "2024-01-16T14:00:00"},  # Advanced without prerequisites
        {"activity_type": "python_video", "score": None, "timestamp": "2024-01-17T09:00:00"},  # Passive consumption only
    ]
    
    gaps = detector._analyze_performance_gaps(sample_activities, [])
    print(f"Detected Gaps: {gaps}")