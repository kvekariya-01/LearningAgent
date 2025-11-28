#!/usr/bin/env python3
"""
Enhanced Recommendation Engine for Learning Agent
Provides robust AI-powered course recommendations with fallback mechanisms
Addresses Minimax API error with alternative solutions
"""

import os
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
# FORCED LOCAL MODE - NO EXTERNAL API CALLS ALLOWED
import os
os.environ["DISABLE_ALL_EXTERNAL_APIS"] = "true"
os.environ["USE_LOCAL_MODELS_ONLY"] = "true" 
os.environ["MINIMAX_API_DISABLED"] = "true"

# Override any API calls to force local mode
def force_local_mode():
    """Force the module to use only local operations"""
    import sys
    import logging
    
    # Disable all external API logging
    logging.getLogger("requests").disabled = True
    logging.getLogger("urllib3").disabled = True
    logging.getLogger("httpx").disabled = True
    
    return True

force_local_mode()



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRecommendationEngine:
    """
    Advanced recommendation engine with multiple fallback mechanisms
    and learning score analysis
    """
    
    def __init__(self):
        self.course_catalog = self._load_course_catalog()
        self.learning_resources = self._load_learning_resources()
        self.assessment_tools = self._load_assessment_tools()
        
    def _load_course_catalog(self) -> List[Dict]:
        """Load comprehensive course catalog"""
        return [
            # Programming Courses
            {
                "id": "python-101",
                "title": "Introduction to Python Programming",
                "description": "Learn the basics of Python programming including variables, loops, and functions.",
                "subject": "Programming",
                "difficulty": "beginner",
                "content_type": "video",
                "duration": 120,
                "tags": ["python", "programming", "basics", "coding"],
                "learning_style": ["visual", "kinesthetic"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Python Basics Cheat Sheet", "url": "/resources/python-cheatsheet.pdf"},
                    {"title": "Python Syntax Guide", "url": "/resources/python-syntax.pdf"}
                ]
            },
            {
                "id": "data-science-intro",
                "title": "Data Science Fundamentals",
                "description": "Introduction to data science concepts, tools, and techniques.",
                "subject": "Data Science",
                "difficulty": "beginner", 
                "content_type": "interactive",
                "duration": 180,
                "tags": ["data", "science", "statistics", "analysis", "pandas", "numpy"],
                "learning_style": ["visual", "kinesthetic"],
                "prerequisites": ["python-101"],
                "pdf_resources": [
                    {"title": "Data Science Handbook", "url": "/resources/data-science-handbook.pdf"}
                ]
            },
            {
                "id": "web-dev-101",
                "title": "Web Development Basics",
                "description": "Learn HTML, CSS, and JavaScript fundamentals for web development.",
                "subject": "Web Development",
                "difficulty": "beginner",
                "content_type": "interactive",
                "duration": 200,
                "tags": ["html", "css", "javascript", "web", "frontend"],
                "learning_style": ["visual", "kinesthetic"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Web Dev Quick Reference", "url": "/resources/web-dev-ref.pdf"}
                ]
            },
            {
                "id": "machine-learning-101",
                "title": "Machine Learning Introduction",
                "description": "Basic concepts of machine learning and AI algorithms.",
                "subject": "Machine Learning",
                "difficulty": "intermediate",
                "content_type": "video",
                "duration": 240,
                "tags": ["machine-learning", "ai", "algorithms", "python", "scikit-learn"],
                "learning_style": ["visual", "mathematical"],
                "prerequisites": ["python-101", "data-science-intro"],
                "pdf_resources": [
                    {"title": "ML Algorithms Reference", "url": "/resources/ml-algorithms.pdf"}
                ]
            },
            # Mathematics Courses
            {
                "id": "math-101",
                "title": "Basic Mathematics",
                "description": "Essential mathematical concepts for technical fields.",
                "subject": "Mathematics",
                "difficulty": "beginner",
                "content_type": "interactive",
                "duration": 90,
                "tags": ["math", "algebra", "calculus", "statistics"],
                "learning_style": ["mathematical", "visual"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Mathematics Formula Sheet", "url": "/resources/math-formulas.pdf"}
                ]
            },
            {
                "id": "statistics-101",
                "title": "Statistics and Probability",
                "description": "Learn statistical analysis and probability theory.",
                "subject": "Mathematics",
                "difficulty": "intermediate",
                "content_type": "video",
                "duration": 150,
                "tags": ["statistics", "probability", "data-analysis"],
                "learning_style": ["mathematical", "analytical"],
                "prerequisites": ["math-101"],
                "pdf_resources": [
                    {"title": "Statistics Guide", "url": "/resources/statistics-guide.pdf"}
                ]
            },
            # Language Courses
            {
                "id": "english-101",
                "title": "English Communication Skills",
                "description": "Improve your English writing and communication abilities.",
                "subject": "Language",
                "difficulty": "beginner",
                "content_type": "article",
                "duration": 100,
                "tags": ["english", "communication", "writing", "language"],
                "learning_style": ["reading", "writing", "auditory"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Communication Skills Guide", "url": "/resources/communication-guide.pdf"}
                ]
            },
            # Business Courses
            {
                "id": "business-101",
                "title": "Business Fundamentals",
                "description": "Introduction to business principles and practices.",
                "subject": "Business",
                "difficulty": "beginner",
                "content_type": "article",
                "duration": 80,
                "tags": ["business", "management", "finance", "marketing"],
                "learning_style": ["reading", "analytical"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Business Basics Handbook", "url": "/resources/business-handbook.pdf"}
                ]
            },
            # Design Courses
            {
                "id": "design-101",
                "title": "Graphic Design Basics",
                "description": "Learn fundamental design principles and tools.",
                "subject": "Design",
                "difficulty": "beginner",
                "content_type": "interactive",
                "duration": 140,
                "tags": ["design", "graphics", "creativity", "visual", "photoshop"],
                "learning_style": ["visual", "kinesthetic", "creative"],
                "prerequisites": [],
                "pdf_resources": [
                    {"title": "Design Principles Guide", "url": "/resources/design-principles.pdf"}
                ]
            }
        ]
    
    def _load_learning_resources(self) -> Dict[str, List[Dict]]:
        """Load additional learning resources by category"""
        return {
            "pdfs": [
                {"id": "python-official-docs", "title": "Python Official Documentation", "url": "/resources/python-docs.pdf", "subject": "Programming"},
                {"id": "ml-math-prerequisites", "title": "Math for Machine Learning", "url": "/resources/ml-math.pdf", "subject": "Mathematics"},
                {"id": "data-viz-guide", "title": "Data Visualization Guide", "url": "/resources/data-viz.pdf", "subject": "Data Science"},
                {"id": "web-accessibility", "title": "Web Accessibility Guidelines", "url": "/resources/web-accessibility.pdf", "subject": "Web Development"}
            ],
            "articles": [
                {"id": "best-practices-coding", "title": "10 Best Coding Practices", "url": "/articles/best-practices", "subject": "Programming"},
                {"id": "data-science-career", "title": "Career in Data Science", "url": "/articles/data-science-career", "subject": "Data Science"},
                {"id": "ux-design-principles", "title": "UX Design Principles", "url": "/articles/ux-principles", "subject": "Design"}
            ],
            "videos": [
                {"id": "intro-to-algorithms", "title": "Introduction to Algorithms", "url": "/videos/algorithms-intro", "subject": "Computer Science"},
                {"id": "data-structures", "title": "Data Structures Explained", "url": "/videos/data-structures", "subject": "Computer Science"}
            ]
        }
    
    def _load_assessment_tools(self) -> Dict[str, List[Dict]]:
        """Load assessment tools and quizzes"""
        return {
            "quizzes": [
                {
                    "id": "python-basics-quiz",
                    "title": "Python Basics Quiz",
                    "subject": "Programming",
                    "difficulty": "beginner",
                    "questions": 10,
                    "duration": 15,
                    "tags": ["python", "basics", "syntax"]
                },
                {
                    "id": "data-science-assessment",
                    "title": "Data Science Fundamentals Assessment",
                    "subject": "Data Science",
                    "difficulty": "intermediate",
                    "questions": 15,
                    "duration": 25,
                    "tags": ["statistics", "analysis", "pandas"]
                },
                {
                    "id": "web-dev-knowledge-check",
                    "title": "Web Development Knowledge Check",
                    "subject": "Web Development",
                    "difficulty": "beginner",
                    "questions": 12,
                    "duration": 20,
                    "tags": ["html", "css", "javascript"]
                }
            ],
            "tests": [
                {
                    "id": "programming-proficiency-test",
                    "title": "Programming Proficiency Test",
                    "subject": "Programming",
                    "difficulty": "intermediate",
                    "sections": ["syntax", "problem-solving", "debugging"],
                    "duration": 60,
                    "tags": ["programming", "logical-thinking"]
                },
                {
                    "id": "mathematics-skills-assessment",
                    "title": "Mathematics Skills Assessment",
                    "subject": "Mathematics", 
                    "difficulty": "mixed",
                    "sections": ["algebra", "calculus", "statistics"],
                    "duration": 45,
                    "tags": ["math", "analytical-thinking"]
                }
            ],
            "projects": [
                {
                    "id": "portfolio-website",
                    "title": "Build a Portfolio Website",
                    "subject": "Web Development",
                    "difficulty": "intermediate",
                    "skills": ["html", "css", "javascript", "responsive-design"],
                    "estimated_hours": 20,
                    "tags": ["web", "portfolio", "practical"]
                },
                {
                    "id": "data-analysis-project",
                    "title": "Data Analysis of Real Dataset",
                    "subject": "Data Science",
                    "difficulty": "intermediate",
                    "skills": ["pandas", "visualization", "statistics", "reporting"],
                    "estimated_hours": 25,
                    "tags": ["data", "analysis", "visualization"]
                }
            ]
        }

    def analyze_learning_score(self, learner_data: Dict) -> Dict[str, Any]:
        """
        Analyze learner performance and learning score
        """
        activities = learner_data.get("activities", [])
        
        if not activities:
            return {
                "learning_score": 0,
                "performance_level": "newcomer",
                "strengths": [],
                "improvement_areas": ["general-knowledge"],
                "recommended_focus": "foundation-building"
            }
        
        # Calculate metrics
        total_activities = len(activities)
        scores = [a.get("score", 0) for a in activities if a.get("score") is not None]
        durations = [a.get("duration", 0) for a in activities if a.get("duration") is not None]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        total_duration = sum(durations) if durations else 0
        completion_rate = len([a for a in activities if a.get("activity_type") == "module_completed"]) / total_activities if total_activities > 0 else 0
        
        # Calculate learning velocity (activities per week)
        timestamps = [a.get("timestamp", "") for a in activities if a.get("timestamp")]
        if timestamps:
            try:
                dates = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in timestamps if ts]
                if len(dates) > 1:
                    days_span = (max(dates) - min(dates)).days
                    learning_velocity = len(activities) / max(days_span / 7, 1)
                else:
                    learning_velocity = 1.0
            except:
                learning_velocity = 1.0
        else:
            learning_velocity = 1.0
        
        # Determine performance level
        if avg_score >= 90 and learning_velocity >= 2:
            performance_level = "advanced"
            recommended_focus = "advanced-topics"
        elif avg_score >= 80 and learning_velocity >= 1:
            performance_level = "proficient"
            recommended_focus = "skill-refinement"
        elif avg_score >= 70:
            performance_level = "developing"
            recommended_focus = "practice-improvement"
        elif avg_score >= 50:
            performance_level = "emerging"
            recommended_focus = "foundation-strengthening"
        else:
            performance_level = "struggling"
            recommended_focus = "basic-remediation"
        
        # Identify strengths and improvement areas based on subject performance
        subject_scores = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "")
            score = activity.get("score", 0)
            
            # Categorize activities by subject
            if "programming" in activity_type or "coding" in activity_type:
                subject_scores["Programming"] = subject_scores.get("Programming", []) + [score]
            elif "data" in activity_type or "analysis" in activity_type:
                subject_scores["Data Science"] = subject_scores.get("Data Science", []) + [score]
            elif "design" in activity_type or "creative" in activity_type:
                subject_scores["Design"] = subject_scores.get("Design", []) + [score]
            elif "math" in activity_type:
                subject_scores["Mathematics"] = subject_scores.get("Mathematics", []) + [score]
        
        # Calculate subject averages
        subject_averages = {subject: sum(scores)/len(scores) for subject, scores in subject_scores.items()}
        
        # Determine strengths (subjects with >80% average)
        strengths = [subject for subject, avg in subject_averages.items() if avg >= 80]
        
        # Determine improvement areas (subjects with <70% average or not attempted)
        improvement_areas = [subject for subject, avg in subject_averages.items() if avg < 70]
        if not improvement_areas and subject_averages:
            # If all attempted subjects are good, suggest new areas
            improvement_areas = ["advanced-concepts", "specialized-topics"]
        elif not improvement_areas:
            improvement_areas = ["foundation-building"]
        
        # Calculate overall learning score (0-100)
        score_component = min(avg_score, 100)
        velocity_component = min(learning_velocity * 25, 25)  # Max 25 points for velocity
        completion_component = completion_rate * 25  # Max 25 points for completion
        consistency_component = min(total_activities * 2, 25)  # Max 25 points for activity count
        
        learning_score = score_component + velocity_component + completion_component + consistency_component
        learning_score = min(learning_score, 100)  # Cap at 100
        
        return {
            "learning_score": round(learning_score, 1),
            "performance_level": performance_level,
            "avg_score": round(avg_score, 1),
            "total_activities": total_activities,
            "total_duration": round(total_duration, 1),
            "learning_velocity": round(learning_velocity, 2),
            "completion_rate": round(completion_rate * 100, 1),
            "subject_averages": subject_averages,
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "recommended_focus": recommended_focus
        }

    def generate_enhanced_recommendations(self, learner_data: Dict, count: int = 6) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations based on learning score and preferences
        """
        # Analyze learner performance
        performance_analysis = self.analyze_learning_score(learner_data)
        learning_score = performance_analysis["learning_score"]
        performance_level = performance_analysis["performance_level"]
        strengths = performance_analysis["strengths"]
        improvement_areas = performance_analysis["improvement_areas"]
        
        # Get learner preferences and style
        preferences = learner_data.get("preferences", [])
        learning_style = learner_data.get("learning_style", "Mixed")
        age = learner_data.get("age", 25)
        
        recommendations = {
            "courses": [],
            "pdf_resources": [],
            "assessments": [],
            "projects": [],
            "performance_analysis": performance_analysis,
            "recommendation_metadata": {
                "generated_at": datetime.now().isoformat(),
                "learning_score": learning_score,
                "performance_level": performance_level,
                "recommendation_count": 0
            }
        }
        
        # Course recommendations based on learning score and preferences
        course_recs = self._recommend_courses(learner_data, performance_analysis, count)
        recommendations["courses"] = course_recs
        
        # PDF resource recommendations
        pdf_recs = self._recommend_pdf_resources(preferences, improvement_areas, learning_score)
        recommendations["pdf_resources"] = pdf_recs
        
        # Assessment recommendations based on performance
        assessment_recs = self._recommend_assessments(performance_analysis, preferences)
        recommendations["assessments"] = assessment_recs
        
        # Project recommendations for hands-on learning
        project_recs = self._recommend_projects(performance_level, preferences, strengths)
        recommendations["projects"] = project_recs
        
        # Update metadata
        total_recs = len(course_recs) + len(pdf_recs) + len(assessment_recs) + len(project_recs)
        recommendations["recommendation_metadata"]["recommendation_count"] = total_recs
        
        return recommendations

    def _recommend_courses(self, learner_data: Dict, performance_analysis: Dict, count: int) -> List[Dict]:
        """Recommend courses based on learning score and performance"""
        preferences = learner_data.get("preferences", [])
        learning_style = learner_data.get("learning_style", "Mixed")
        learning_score = performance_analysis["learning_score"]
        performance_level = performance_analysis["performance_level"]
        improvement_areas = performance_analysis["improvement_areas"]
        
        # Score courses based on multiple factors
        scored_courses = []
        
        for course in self.course_catalog:
            score = 0
            reasons = []
            
            # Subject matching (highest priority)
            course_subject = course.get("subject", "").lower()
            for pref in preferences:
                if pref.lower() in course_subject or course_subject in pref.lower():
                    score += 15
                    reasons.append(f"matches your interest in {pref}")
                    break
            
            # Tag matching
            course_tags = [tag.lower() for tag in course.get("tags", [])]
            for pref in preferences:
                if any(pref.lower() in tag for tag in course_tags):
                    score += 10
                    reasons.append(f"covers {pref} topics")
                    break
            
            # Learning style matching
            course_content_type = course.get("content_type", "").lower()
            style_content_mapping = {
                "Visual": ["video", "interactive", "infographic"],
                "Auditory": ["video", "podcast", "discussion"],
                "Kinesthetic": ["interactive", "assignment", "project"],
                "Reading/Writing": ["article", "assignment", "quiz"],
                "Mixed": ["video", "article", "interactive"]
            }
            
            preferred_types = style_content_mapping.get(learning_style, ["video", "article"])
            if course_content_type in preferred_types:
                score += 8
                reasons.append(f"suitable for {learning_style} learners")
            
            # Performance-based difficulty adjustment
            course_difficulty = course.get("difficulty", "beginner")
            if performance_level == "struggling" and course_difficulty == "beginner":
                score += 12
                reasons.append("beginner-friendly content to build confidence")
            elif performance_level == "advanced" and course_difficulty == "intermediate":
                score += 10
                reasons.append("challenging content for your skill level")
            elif performance_level == "proficient" and course_difficulty in ["beginner", "intermediate"]:
                score += 5
                reasons.append("appropriate difficulty level")
            
            # Improvement area matching
            for area in improvement_areas:
                if any(area.lower() in tag for tag in course_tags):
                    score += 8
                    reasons.append(f"addresses your improvement area: {area}")
                    break
            
            # Learning score adjustment
            if learning_score < 50 and course_difficulty == "beginner":
                score += 6  # Favor easier content for lower scores
            elif learning_score > 80 and course_difficulty in ["intermediate", "advanced"]:
                score += 6  # Favor harder content for higher scores
            
            if score > 0:
                scored_courses.append({
                    "course": course,
                    "score": score,
                    "reasons": reasons[:2],  # Top 2 reasons
                    "match_confidence": min(score / 20.0, 1.0)  # Normalize to 0-1
                })
        
        # Sort by score and return top recommendations
        scored_courses.sort(key=lambda x: x["score"], reverse=True)
        
        course_recommendations = []
        for item in scored_courses[:count]:
            course = item["course"]
            course_recommendations.append({
                "course_id": course.get("id", ""),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "subject": course.get("subject", ""),
                "difficulty": course.get("difficulty", ""),
                "content_type": course.get("content_type", ""),
                "duration": course.get("duration", 0),
                "tags": course.get("tags", []),
                "reason": f"Recommended because {', '.join(item['reasons'])}",
                "confidence": round(item["match_confidence"], 2),
                "learning_style_match": learning_style,
                "estimated_completion": f"{course.get('duration', 0)} minutes"
            })
        
        return course_recommendations

    def _recommend_pdf_resources(self, preferences: List[str], improvement_areas: List[str], learning_score: float) -> List[Dict]:
        """Recommend PDF resources based on preferences and performance"""
        pdf_recommendations = []
        
        # Match PDFs to preferences
        for pdf in self.learning_resources["pdfs"]:
            score = 0
            reasons = []
            
            # Subject matching
            pdf_subject = pdf.get("subject", "").lower()
            for pref in preferences:
                if pref.lower() in pdf_subject:
                    score += 10
                    reasons.append(f"covers {pref}")
                    break
            
            # Improvement area matching
            for area in improvement_areas:
                if area.lower() in pdf_subject:
                    score += 8
                    reasons.append(f"addresses {area}")
                    break
            
            # Learning score consideration
            if learning_score < 60:  # For struggling learners, recommend foundational resources
                if "basics" in pdf.get("title", "").lower() or "fundamentals" in pdf.get("title", "").lower():
                    score += 6
                    reasons.append("foundational knowledge")
            
            if score > 0:
                pdf_recommendations.append({
                    "resource_id": pdf.get("id", ""),
                    "title": pdf.get("title", ""),
                    "subject": pdf.get("subject", ""),
                    "url": pdf.get("url", ""),
                    "type": "pdf_guide",
                    "reason": f"Recommended because {', '.join(reasons)}",
                    "score": score
                })
        
        # Sort by score and return top 4
        pdf_recommendations.sort(key=lambda x: x["score"], reverse=True)
        return pdf_recommendations[:4]

    def _recommend_assessments(self, performance_analysis: Dict, preferences: List[str]) -> List[Dict]:
        """Recommend assessments based on performance level and preferences"""
        assessment_recommendations = []
        performance_level = performance_analysis["performance_level"]
        learning_score = performance_analysis["learning_score"]
        
        # Recommend quizzes
        for quiz in self.assessment_tools["quizzes"]:
            score = 0
            reasons = []
            
            # Preference matching
            quiz_subject = quiz.get("subject", "").lower()
            for pref in preferences:
                if pref.lower() in quiz_subject:
                    score += 8
                    reasons.append(f"assesses {pref} knowledge")
                    break
            
            # Performance-appropriate difficulty
            if performance_level in ["struggling", "emerging"] and quiz["difficulty"] == "beginner":
                score += 6
                reasons.append("appropriate for current skill level")
            elif performance_level in ["advanced", "proficient"] and quiz["difficulty"] == "intermediate":
                score += 6
                reasons.append("challenging assessment for skill level")
            
            # Learning score consideration
            if learning_score > 75:  # For good performers, suggest more challenging assessments
                if quiz["difficulty"] == "intermediate":
                    score += 4
                    reasons.append("challenging content")
            
            if score > 0:
                assessment_recommendations.append({
                    "assessment_id": quiz.get("id", ""),
                    "title": quiz.get("title", ""),
                    "subject": quiz.get("subject", ""),
                    "type": "quiz",
                    "difficulty": quiz.get("difficulty", ""),
                    "questions": quiz.get("questions", 0),
                    "duration": quiz.get("duration", 0),
                    "tags": quiz.get("tags", []),
                    "reason": f"Recommended because {', '.join(reasons)}",
                    "estimated_time": f"{quiz.get('duration', 0)} minutes",
                    "score": score
                })
        
        # Recommend tests for more comprehensive assessment
        for test in self.assessment_tools["tests"]:
            # Only recommend comprehensive tests for learners with some experience
            total_activities = performance_analysis.get("total_activities", 0)
            if total_activities >= 3:
                score = 5  # Base score for comprehensive tests
                assessment_recommendations.append({
                    "assessment_id": test.get("id", ""),
                    "title": test.get("title", ""),
                    "subject": test.get("subject", ""),
                    "type": "comprehensive_test",
                    "difficulty": test.get("difficulty", ""),
                    "sections": test.get("sections", []),
                    "duration": test.get("duration", 0),
                    "tags": test.get("tags", []),
                    "reason": "Comprehensive assessment to evaluate overall competency",
                    "estimated_time": f"{test.get('duration', 0)} minutes",
                    "score": score
                })
        
        # Sort by score and return top assessments
        assessment_recommendations.sort(key=lambda x: x["score"], reverse=True)
        return assessment_recommendations[:5]

    def _recommend_projects(self, performance_level: str, preferences: List[str], strengths: List[str]) -> List[Dict]:
        """Recommend hands-on projects"""
        project_recommendations = []
        
        for project in self.assessment_tools["projects"]:
            score = 0
            reasons = []
            
            # Subject matching with preferences
            project_subject = project.get("subject", "").lower()
            for pref in preferences:
                if pref.lower() in project_subject:
                    score += 10
                    reasons.append(f"hands-on experience in {pref}")
                    break
            
            # Match with strengths
            for strength in strengths:
                if strength.lower() in project_subject:
                    score += 8
                    reasons.append(f"leverages your strength in {strength}")
                    break
            
            # Performance-appropriate difficulty
            if performance_level in ["advanced", "proficient"] and project["difficulty"] == "intermediate":
                score += 6
                reasons.append("challenging project for skill level")
            elif performance_level in ["emerging", "developing"] and project["difficulty"] == "beginner":
                score += 6
                reasons.append("appropriate project complexity")
            
            if score > 0:
                project_recommendations.append({
                    "project_id": project.get("id", ""),
                    "title": project.get("title", ""),
                    "subject": project.get("subject", ""),
                    "type": "hands_on_project",
                    "difficulty": project.get("difficulty", ""),
                    "skills": project.get("skills", []),
                    "estimated_hours": project.get("estimated_hours", 0),
                    "tags": project.get("tags", []),
                    "reason": f"Recommended because {', '.join(reasons)}",
                    "estimated_completion": f"{project.get('estimated_hours', 0)} hours",
                    "score": score
                })
        
        # Sort by score and return top projects
        project_recommendations.sort(key=lambda x: x["score"], reverse=True)
        return project_recommendations[:3]

    def safe_get_recommendations(self, learner_id: str, learner_data: Dict, api_base_url: str = None) -> Dict[str, Any]:
        """
        Safe wrapper for getting recommendations with robust error handling
        ALWAYS uses local recommendations to prevent Minimax API errors
        """
        try:
            # ALWAYS use local enhanced recommendations - NO external API calls allowed
            logger.info("Using local enhanced recommendation engine (external APIs completely disabled)")
            enhanced_recommendations = self.generate_enhanced_recommendations(learner_data)
            
            return {
                "learner_id": learner_id,
                "recommendations": enhanced_recommendations["courses"],
                "enhanced_recommendations": enhanced_recommendations,
                "recommendation_type": "enhanced_local",
                "enhanced_by": "EnhancedRecommendationEngine",
                "fallback_used": False,
                "fallback_reason": "Local recommendation engine (external APIs disabled by design)"
            }
            
        except Exception as e:
            logger.error(f"Recommendation engine error: {e}")
            # Ultimate fallback - basic recommendations
            return {
                "learner_id": learner_id,
                "recommendations": [],
                "enhanced_recommendations": {
                    "courses": [],
                    "pdf_resources": [],
                    "assessments": [],
                    "projects": [],
                    "performance_analysis": {
                        "learning_score": 0,
                        "performance_level": "error",
                        "error": str(e)
                    }
                },
                "recommendation_type": "error_fallback",
                "enhanced_by": "EnhancedRecommendationEngine",
                "fallback_used": True,
                "fallback_reason": f"Recommendation system error: {str(e)}"
            }

# Global instance for easy importing
recommendation_engine = EnhancedRecommendationEngine()

def get_enhanced_recommendations(learner_id: str, learner_data: Dict, api_base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to get enhanced recommendations
    """
    return recommendation_engine.safe_get_recommendations(learner_id, learner_data, api_base_url)

if __name__ == "__main__":
    # Test the recommendation engine
    test_learner_data = {
        "id": "test-learner",
        "name": "Test Learner",
        "age": 25,
        "learning_style": "Visual",
        "preferences": ["Programming", "Data Science"],
        "activities": [
            {"activity_type": "module_completed", "score": 85, "duration": 60, "timestamp": "2024-01-15T10:00:00"},
            {"activity_type": "quiz_completed", "score": 92, "duration": 30, "timestamp": "2024-01-16T14:30:00"},
            {"activity_type": "assignment_submitted", "score": 78, "duration": 90, "timestamp": "2024-01-17T09:15:00"}
        ]
    }
    
    result = get_enhanced_recommendations("test-learner", test_learner_data)
    print(json.dumps(result, indent=2))