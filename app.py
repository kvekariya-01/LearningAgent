import os
import streamlit as st
import json
import pandas as pd
from datetime import datetime
# Network Blocker - Prevents Minimax API errors
try:
    import network_blocker
    network_blocker.activate_network_blocker()
    print("Network protection active")
except ImportError:
    print("Network blocker not available")

# Load .env only for local development (optional)
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    # For production deployment without .env file

# ---------------------------
#  Database Initialization
# ---------------------------
try:
    from config.db_config import db
    DB_CONNECTED = True
except Exception as e:
    st.warning(f"Database connection failed at startup: {e}")
    db = None
    DB_CONNECTED = False

# ---------------------------
#  Model + CRUD Imports
# ---------------------------
try:
    from models.learner import Learner
    from models.content import Content
    from models.engagement import Engagement
    from models.intervention import Intervention
    from models.progress import ProgressLog
    from utils.crud_operations import (
        create_learner, read_learners, read_learner, update_learner, log_activity,
        create_indexes, create_content, read_contents, read_content, update_content, delete_content,
        create_engagement, read_engagements, read_engagement, update_engagement, delete_engagement,
        create_progress_log, read_progress_logs
    )
    
    # Import read_learner_activities separately to avoid import issues
    try:
        from utils.crud_operations import read_learner_activities
    except ImportError:
        # Fallback implementation if import fails
        def read_learner_activities(learner_id):
            learner_data = read_learner(learner_id)
            if not learner_data:
                return None
            return learner_data.get("activities", [])
    from utils.adaptive_logic import create_intervention, read_interventions
    
    # Import scoring system components
    try:
        from ml.scoring_engine import get_learner_score_summary, ScoringEngine
        from ml.score_based_recommender import ScoreBasedRecommender
        from models.test_result import TestResult
        SCORING_LOADED = True
    except ImportError as e:
        SCORING_LOADED = False
        st.warning(f"Scoring system not available: {e}")
    
    # Import comprehensive scoring system
    try:
        from ml.comprehensive_scoring import comprehensive_scoring_system
        COMPREHENSIVE_SCORING_LOADED = True
    except ImportError:
        COMPREHENSIVE_SCORING_LOADED = False
        comprehensive_scoring_system = None
        
    MODELS_LOADED = True
except Exception as e:
    st.error(f"Failed to import models: {e}")
    MODELS_LOADED = False

# ---------------------------
#  Create Indexes (Safe)
# ---------------------------
if MODELS_LOADED:
    try:
        create_indexes()
        # Check if using MongoDB or in-memory database
        from config.db_config import db
        if db is not None:
            st.success("[OK] Database indexes created")
        else:
            st.info("[OK] Using in-memory database (no indexes needed)")
    except Exception as e:
        st.warning(f"Could not create indexes: {e}")

# ---------------------------
#  Streamlit App Configuration
# ---------------------------
st.set_page_config(
    page_title="Learning Agent",
    page_icon="[EDU]",
    layout="wide"
)

def validate_learner_data(data):
    """Validate learner registration data"""
    errors = []
    
    # Check required fields
    required_fields = ["name", "age", "gender", "learning_style", "preferences"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"'{field}' is required")
    
    # Validate age
    try:
        age = int(data.get("age", 0))
        if not (0 <= age <= 120):
            errors.append("Age must be between 0 and 120")
    except (ValueError, TypeError):
        errors.append("Age must be a valid integer")
    
    return errors

def register_learner_st(name, age, gender, learning_style, preferences):
    """Register a learner using the same business logic as the Flask app"""
    try:
        # Parse preferences from comma-separated string to list
        if isinstance(preferences, str):
            preferences_list = [p.strip() for p in preferences.split(',') if p.strip()]
        else:
            preferences_list = preferences if isinstance(preferences, list) else [str(preferences)]
        
        # Create learner object
        learner = Learner(
            name=name,
            age=int(age),
            gender=gender,
            learning_style=learning_style,
            preferences=preferences_list
        )
        
        # Save to database
        result = create_learner(learner)
        
        if result:
            return True, learner.id, None
        else:
            return False, None, "Database error: Could not save learner"
            
    except Exception as e:
        return False, None, str(e)

def register_content_st(title, description, content_type, course_id, module_id, difficulty_level, tags):
    """Register content using the content model"""
    try:
        # Parse tags from comma-separated string to list
        if isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        else:
            tags_list = tags if isinstance(tags, list) else [str(tags)]
        
        # Create content object
        content = Content(
            title=title,
            description=description,
            content_type=content_type,
            course_id=course_id,
            module_id=module_id if module_id.strip() else None,
            difficulty_level=difficulty_level,
            tags=tags_list
        )
        
        # Save to database
        result = create_content(content)
        
        if result:
            return True, content.id, None
        else:
            return False, None, "Database error: Could not save content"
            
    except Exception as e:
        return False, None, str(e)

def register_engagement_st(learner_id, content_id, course_id, engagement_type, duration, score, feedback):
    """Register engagement using the engagement model"""
    try:
        # Create engagement object
        engagement = Engagement(
            learner_id=learner_id,
            content_id=content_id,
            course_id=course_id,
            engagement_type=engagement_type,
            duration=float(duration) if duration else None,
            score=float(score) if score else None,
            feedback=feedback if feedback.strip() else None
        )
        
        # Save to database
        result = create_engagement(engagement)
        
        if result:
            return True, engagement.id, None
        else:
            return False, None, "Database error: Could not save engagement"
            
    except Exception as e:
        return False, None, str(e)

def register_intervention_st(learner_id, intervention_type, message, triggered_by):
    """Register intervention using the intervention model"""
    try:
        # Create intervention object
        intervention = Intervention(
            learner_id=learner_id,
            intervention_type=intervention_type,
            message=message,
            triggered_by=triggered_by
        )
        
        # Save to database
        result = create_intervention(intervention)
        
        if result:
            return True, intervention.id, None
        else:
            return False, None, "Database error: Could not save intervention"
            
    except Exception as e:
        return False, None, str(e)

def display_course_recommendations(course_recs):
    """Display course recommendations with enhanced formatting"""
    for i, rec in enumerate(course_recs, 1):
        with st.container():
            # Course card styling
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                <h4 style="margin: 0; color: #1f77b4;">[BOOK] {rec.get('title', 'Course Title')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Course details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Subject:** {rec.get('subject', 'General')}")
                st.write(f"**Description:** {rec.get('description', 'No description available')}")
                st.write(f"**Why recommended:** {rec.get('reason', 'Matches your preferences')}")
                
                # Show tags if available
                tags = rec.get('tags', [])
                if tags:
                    st.write(f"**Topics:** {', '.join(tags[:5])}")  # Show first 5 tags
            
            with col2:
                st.write(f"**Difficulty:** {rec.get('difficulty', 'Beginner').title()}")
                st.write(f"**Content Type:** {rec.get('content_type', 'Video').title()}")
                st.write(f"**Duration:** {rec.get('duration', 0)} minutes")
                
                # Confidence indicator
                confidence = rec.get('confidence', 0.5)
                confidence_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                st.write(f"**Match Confidence:** {confidence_color} {confidence:.0%}")
                
                # Learning style match
                if rec.get('learning_style_match'):
                    st.write(f"**Learning Style:** [OK] {rec.get('learning_style_match')}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📖 Start Course", key=f"start_{rec.get('course_id', i)}"):
                    st.success(f"Ready to start: {rec.get('title', 'Course')}!")
                    st.info("[TIP] Use the 'Log Activity' page to track your progress.")
            
            with col2:
                if st.button(f"[LIST] Add to Wishlist", key=f"wishlist_{rec.get('course_id', i)}"):
                    st.info(f"Added '{rec.get('title', 'Course')}' to your wishlist!")
            
            with col3:
                if st.button(f"[STATS] View Details", key=f"details_{rec.get('course_id', i)}"):
                    with st.expander("Course Details", expanded=False):
                        st.write(f"**Course ID:** `{rec.get('course_id', 'N/A')}`")
                        st.write(f"**Tags:** {rec.get('tags', [])}")
                        st.write(f"**Preference Match:** {'[OK] Yes' if rec.get('preference_match') else '[FAIL] No'}")
            
            st.markdown("---")

def display_performance_recommendations(perf_recs):
    """Display performance-based recommendations"""
    for i, rec in enumerate(perf_recs, 1):
        with st.container():
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #ffc107;">
                <h4 style="margin: 0; color: #856404;">[GROWTH] {rec.get('title', 'Performance Recommendation')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Insight:** {rec.get('description', 'Performance-based recommendation')}")
            st.write(f"**Reason:** {rec.get('reason', 'Based on your learning performance')}")
            
            if st.button(f"[POWER] Take Action", key=f"action_{i}"):
                st.info("[TIP] **Next Steps:**")
                st.write("1. Review the recommended areas")
                st.write("2. Practice with targeted exercises")
                st.write("3. Track your improvement")
            
            st.markdown("---")

def display_general_recommendations(recs):
    """Display general recommendations"""
    for i, rec in enumerate(recs, 1):
        with st.container():
            st.markdown(f"### {i}. {rec.get('title', 'Recommendation')}")
            st.write(f"**Description:** {rec.get('description', 'No description')}")
            st.write(f"**Reason:** {rec.get('reason', 'No reason provided')}")
            
            if rec.get('content_id'):
                st.write(f"**Content ID:** `{rec.get('content_id')}`")
            
            if rec.get('difficulty'):
                st.write(f"**Difficulty:** {rec.get('difficulty')}")
            
            st.markdown("---")

def get_recommendations(learner_id, api_base_url="http://localhost:5000"):
    """Get recommendations for a learner - ALWAYS uses local recommendations to prevent Minimax API errors"""
    try:
        # ALWAYS use local enhanced recommendations - NO external API calls allowed
        return get_enhanced_recommendations_safe(learner_id)
    except Exception as e:
        # Fallback to basic local recommendations if enhanced engine fails
        return generate_local_recommendations(learner_id)

def get_enhanced_recommendations_safe(learner_id):
    """Safe wrapper for enhanced recommendations with comprehensive error handling"""
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
        # Get learner data
        learner_data = read_learner(learner_id)
        if not learner_data:
            return {"error": "Learner not found"}
        
        # Use enhanced recommendation engine (which now only uses local recommendations)
        return get_enhanced_recommendations(learner_id, learner_data)
        
    except Exception as e:
        # Ultimate fallback to basic local recommendations
        return generate_local_recommendations(learner_id)

def display_enhanced_recommendations(recommendations_data):
    """Display enhanced recommendations including PDFs, assessments, and projects"""
    
    # Extract enhanced recommendations if available
    enhanced_recs = recommendations_data.get("enhanced_recommendations", {})
    
    if not enhanced_recs:
        # Fallback to regular recommendations display
        recs = recommendations_data.get("recommendations", [])
        display_course_recommendations(recs)
        return
    
    # Display learning score and performance analysis
    performance_analysis = enhanced_recs.get("performance_analysis", {})
    if performance_analysis:
        st.subheader("[STATS] Your Learning Performance Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            learning_score = performance_analysis.get("learning_score", 0)
            st.metric("Learning Score", f"{learning_score}/100", delta=None)
        
        with col2:
            avg_score = performance_analysis.get("avg_score", 0)
            st.metric("Average Score", f"{avg_score:.1f}%", delta=None)
        
        with col3:
            learning_velocity = performance_analysis.get("learning_velocity", 0)
            st.metric("Learning Velocity", f"{learning_velocity:.2f}/week", delta=None)
        
        with col4:
            total_activities = performance_analysis.get("total_activities", 0)
            st.metric("Total Activities", f"{total_activities}", delta=None)
        
        # Performance level and insights
        performance_level = performance_analysis.get("performance_level", "Unknown").title()
        st.info(f"**Performance Level:** {performance_level}")
        
        strengths = performance_analysis.get("strengths", [])
        improvement_areas = performance_analysis.get("improvement_areas", [])
        
        if strengths or improvement_areas:
            col1, col2 = st.columns(2)
            
            with col1:
                if strengths:
                    st.write("**[OK] Your Strengths:**")
                    for strength in strengths:
                        st.write(f"• {strength}")
            
            with col2:
                if improvement_areas:
                    st.write("**[TARGET] Areas for Improvement:**")
                    for area in improvement_areas:
                        st.write(f"• {area}")
    
    # Display course recommendations
    courses = enhanced_recs.get("courses", [])
    if courses:
        st.subheader("[BOOK] Recommended Courses")
        display_enhanced_courses(courses)
    
    # Display PDF resources
    pdf_resources = enhanced_recs.get("pdf_resources", [])
    if pdf_resources:
        st.subheader("[DOC] Recommended Reading Materials")
        display_pdf_resources(pdf_resources)
    
    # Display assessments
    assessments = enhanced_recs.get("assessments", [])
    if assessments:
        st.subheader("[NOTE] Recommended Assessments")
        display_assessments(assessments)
    
    # Display projects
    projects = enhanced_recs.get("projects", [])
    if projects:
        st.subheader("[WORK] Recommended Hands-on Projects")
        display_projects(projects)

def display_enhanced_courses(courses):
    """Display enhanced course recommendations with detailed information"""
    for i, course in enumerate(courses, 1):
        with st.container():
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                <h4 style="margin: 0; color: #1f77b4;">[BOOK] {course.get('title', 'Course Title')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Subject:** {course.get('subject', 'General')}")
                st.write(f"**Description:** {course.get('description', 'No description available')}")
                st.write(f"**Why recommended:** {course.get('reason', 'Matches your preferences')}")
                
                # Show tags
                tags = course.get('tags', [])
                if tags:
                    st.write(f"**Topics:** {', '.join(tags[:5])}")
                
                # Show estimated completion time
                duration = course.get('duration', 0)
                estimated_completion = course.get('estimated_completion', f"{duration} minutes")
                st.write(f"**Estimated Time:** {estimated_completion}")
            
            with col2:
                st.write(f"**Difficulty:** {course.get('difficulty', 'Beginner').title()}")
                st.write(f"**Content Type:** {course.get('content_type', 'Video').title()}")
                
                # Confidence indicator
                confidence = course.get('confidence', 0.5)
                confidence_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                st.write(f"**Match Confidence:** {confidence_color} {confidence:.0%}")
                
                # Learning style match
                if course.get('learning_style_match'):
                    st.write(f"**Learning Style:** [OK] {course.get('learning_style_match')}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"[TARGET] Start Course", key=f"start_course_{i}"):
                    st.success(f"Ready to start: {course.get('title', 'Course')}!")
                    st.info("[TIP] Use the 'Log Activity' page to track your progress.")
            
            with col2:
                if st.button(f"[LIST] Add to Wishlist", key=f"wishlist_course_{i}"):
                    st.info(f"Added '{course.get('title', 'Course')}' to your wishlist!")
            
            with col3:
                if st.button(f"[STATS] View Details", key=f"details_course_{i}"):
                    with st.expander("Course Details", expanded=False):
                        st.write(f"**Course ID:** `{course.get('course_id', 'N/A')}`")
                        st.write(f"**Tags:** {course.get('tags', [])}")
                        st.write(f"**Duration:** {course.get('duration', 0)} minutes")
            
            st.markdown("---")

def display_pdf_resources(pdf_resources):
    """Display PDF resource recommendations"""
    for i, pdf in enumerate(pdf_resources, 1):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**[DOC] {pdf.get('title', 'PDF Resource')}**")
                st.write(f"Subject: {pdf.get('subject', 'General')} | Reason: {pdf.get('reason', 'Recommended resource')}")
            
            with col2:
                if st.button("📖 View PDF", key=f"view_pdf_{i}"):
                    st.info(f"Opening PDF: {pdf.get('title', 'Resource')}")
            
            with col3:
                if st.button("⬇️ Download", key=f"download_pdf_{i}"):
                    st.info(f"Downloading: {pdf.get('title', 'Resource')}")
            
            st.markdown("---")

def display_assessments(assessments):
    """Display assessment recommendations"""
    for i, assessment in enumerate(assessments, 1):
        with st.container():
            assessment_type = assessment.get('type', 'quiz').replace('_', ' ').title()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**[NOTE] {assessment.get('title', 'Assessment')}** ({assessment_type})")
                st.write(f"Subject: {assessment.get('subject', 'General')} | Difficulty: {assessment.get('difficulty', 'Mixed').title()}")
                st.write(f"Questions: {assessment.get('questions', 'N/A')} | Duration: {assessment.get('estimated_time', 'N/A')}")
                
                # Show sections for comprehensive tests
                sections = assessment.get('sections', [])
                if sections:
                    st.write(f"**Sections:** {', '.join(sections)}")
                
                st.write(f"**Why recommended:** {assessment.get('reason', 'Skill assessment')}")
            
            with col2:
                if assessment.get('type') == 'comprehensive_test':
                    icon = "[LIST]"
                else:
                    icon = "❓"
                
                if st.button(f"{icon} Take Assessment", key=f"take_assessment_{i}"):
                    st.success(f"Starting: {assessment.get('title', 'Assessment')}")
            
            st.markdown("---")

def display_projects(projects):
    """Display project recommendations"""
    for i, project in enumerate(projects, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**[WORK] {project.get('title', 'Project')}**")
                st.write(f"Subject: {project.get('subject', 'General')} | Difficulty: {project.get('difficulty', 'Mixed').title()}")
                st.write(f"Estimated Time: {project.get('estimated_completion', 'N/A')}")
                
                # Show skills
                skills = project.get('skills', [])
                if skills:
                    st.write(f"**Skills Required:** {', '.join(skills)}")
                
                # Show tags
                tags = project.get('tags', [])
                if tags:
                    st.write(f"**Tags:** {', '.join(tags)}")
                
                st.write(f"**Why recommended:** {project.get('reason', 'Hands-on learning experience')}")
            
            with col2:
                if st.button("[START] Start Project", key=f"start_project_{i}"):
                    st.success(f"Starting project: {project.get('title', 'Project')}")
                    st.info("[TIP] Track your progress using the 'Log Activity' feature!")
            
            st.markdown("---")

def get_available_courses():
    """Get available courses from data files"""
    try:
        import json
        import os
        
        courses = []
        
        # Try to load from courses.json
        courses_file = "data/courses.json"
        if os.path.exists(courses_file):
            with open(courses_file, 'r', encoding='utf-8') as f:
                courses_data = json.load(f)
                if isinstance(courses_data, list):
                    courses = courses_data
                elif isinstance(courses_data, dict) and 'courses' in courses_data:
                    courses = courses_data['courses']
                elif isinstance(courses_data, dict):
                    # If it's a dict, convert to list
                    courses = list(courses_data.values())
        
        # If no courses found, create sample course catalog
        if not courses:
            courses = create_sample_course_catalog()
        
        return courses
        
    except Exception as e:
        print(f"Warning: Could not load courses data: {e}")
        return create_sample_course_catalog()

def create_sample_course_catalog():
    """Create a comprehensive sample course catalog when data files are not available"""
    return [
        {
            "id": "python-101",
            "title": "Introduction to Python Programming",
            "description": "Learn the basics of Python programming including variables, loops, and functions.",
            "subject": "Programming",
            "difficulty": "beginner",
            "content_type": "video",
            "duration": 120,
            "tags": ["python", "programming", "basics"]
        },
        {
            "id": "data-science-intro",
            "title": "Data Science Fundamentals",
            "description": "Introduction to data science concepts, tools, and techniques.",
            "subject": "Data Science",
            "difficulty": "beginner", 
            "content_type": "article",
            "duration": 90,
            "tags": ["data", "science", "statistics", "analysis"]
        },
        {
            "id": "web-dev-101",
            "title": "Web Development Basics",
            "description": "Learn HTML, CSS, and JavaScript fundamentals for web development.",
            "subject": "Web Development",
            "difficulty": "beginner",
            "content_type": "interactive",
            "duration": 180,
            "tags": ["html", "css", "javascript", "web"]
        },
        {
            "id": "machine-learning-101",
            "title": "Machine Learning Introduction",
            "description": "Basic concepts of machine learning and AI algorithms.",
            "subject": "Machine Learning",
            "difficulty": "intermediate",
            "content_type": "video",
            "duration": 150,
            "tags": ["machine-learning", "ai", "algorithms", "python"]
        },
        {
            "id": "math-101",
            "title": "Basic Mathematics",
            "description": "Essential mathematical concepts for technical fields.",
            "subject": "Mathematics",
            "difficulty": "beginner",
            "content_type": "quiz",
            "duration": 60,
            "tags": ["math", "algebra", "calculus", "statistics"]
        },
        {
            "id": "english-101",
            "title": "English Communication Skills",
            "description": "Improve your English writing and communication abilities.",
            "subject": "Language",
            "difficulty": "beginner",
            "content_type": "assignment",
            "duration": 100,
            "tags": ["english", "communication", "writing", "language"]
        },
        {
            "id": "business-101",
            "title": "Business Fundamentals",
            "description": "Introduction to business principles and practices.",
            "subject": "Business",
            "difficulty": "beginner",
            "content_type": "article",
            "duration": 80,
            "tags": ["business", "management", "finance", "marketing"]
        },
        {
            "id": "design-101",
            "title": "Graphic Design Basics",
            "description": "Learn fundamental design principles and tools.",
            "subject": "Design",
            "difficulty": "beginner",
            "content_type": "interactive",
            "duration": 140,
            "tags": ["design", "graphics", "creativity", "visual"]
        }
    ]

def match_courses_to_preferences(learner_preferences, learning_style, available_courses):
    """Match available courses to learner preferences and learning style"""
    recommendations = []
    
    # Convert preferences to lowercase for matching
    if isinstance(learner_preferences, str):
        preference_keywords = [p.strip().lower() for p in learner_preferences.split(',')]
    elif isinstance(learner_preferences, list):
        preference_keywords = [str(p).lower() for p in learner_preferences]
    else:
        preference_keywords = []
    
    # Learning style preferences mapping
    style_content_mapping = {
        "Visual": ["video", "interactive", "infographic"],
        "Auditory": ["video", "podcast", "discussion"],
        "Kinesthetic": ["interactive", "assignment", "project"],
        "Reading/Writing": ["article", "assignment", "quiz"],
        "Mixed": ["video", "article", "interactive"]
    }
    
    preferred_content_types = style_content_mapping.get(learning_style, ["video", "article"])
    
    # Score each course based on relevance
    scored_courses = []
    
    for course in available_courses:
        score = 0
        reasons = []
        
        # Subject matching (highest priority)
        course_subject = course.get("subject", "").lower()
        for pref in preference_keywords:
            if pref in course_subject or course_subject in pref:
                score += 10
                reasons.append(f"matches your interest in {pref}")
        
        # Tag matching
        course_tags = [tag.lower() for tag in course.get("tags", [])]
        for pref in preference_keywords:
            if any(pref in tag for tag in course_tags):
                score += 8
                reasons.append(f"related to {pref}")
        
        # Learning style matching
        course_content_type = course.get("content_type", "").lower()
        if course_content_type in preferred_content_types:
            score += 5
            reasons.append(f"suitable for {learning_style} learners")
        
        # Bonus for beginner-friendly content
        if course.get("difficulty", "").lower() == "beginner":
            score += 3
            reasons.append("beginner-friendly content")
        
        if score > 0:
            scored_courses.append({
                "course": course,
                "score": score,
                "reasons": reasons
            })
    
    # Sort by score and return top recommendations
    scored_courses.sort(key=lambda x: x["score"], reverse=True)
    
    for item in scored_courses[:6]:  # Top 6 recommendations
        course = item["course"]
        reasons = item["reasons"]
        
        recommendations.append({
            "course_id": course.get("id", ""),
            "title": course.get("title", ""),
            "description": course.get("description", ""),
            "subject": course.get("subject", ""),
            "difficulty": course.get("difficulty", ""),
            "content_type": course.get("content_type", ""),
            "duration": course.get("duration", 0),
            "tags": course.get("tags", []),
            "reason": f"Matches your preferences for {', '.join(reasons[:2])}",
            "confidence": min(item["score"] / 10.0, 1.0),  # Normalize to 0-1
            "learning_style_match": learning_style,
            "preference_match": len([r for r in reasons if "matches your interest" in r]) > 0
        })
    
    return recommendations

def generate_course_recommendations(learner_data):
    """Generate personalized course recommendations based on learner profile"""
    try:
        learner_preferences = learner_data.get("preferences", [])
        learning_style = learner_data.get("learning_style", "Mixed")
        age = learner_data.get("age", 25)
        
        # Get available courses
        available_courses = get_available_courses()
        
        # Match courses to learner preferences
        matched_courses = match_courses_to_preferences(learner_preferences, learning_style, available_courses)
        
        # If no matches, provide general recommendations
        if not matched_courses:
            # Fallback: recommend popular beginner courses
            general_courses = [c for c in available_courses if c.get("difficulty", "").lower() == "beginner"]
            matched_courses = [
                {
                    "course_id": c.get("id", ""),
                    "title": c.get("title", ""),
                    "description": c.get("description", ""),
                    "subject": c.get("subject", ""),
                    "difficulty": c.get("difficulty", ""),
                    "content_type": c.get("content_type", ""),
                    "duration": c.get("duration", 0),
                    "tags": c.get("tags", []),
                    "reason": f"Good starter course in {c.get('subject', 'general studies')}",
                    "confidence": 0.7,
                    "learning_style_match": learning_style,
                    "preference_match": False
                }
                for c in general_courses[:3]
            ]
        
        return matched_courses
        
    except Exception as e:
        print(f"Error generating course recommendations: {e}")
        return []

def generate_local_recommendations(learner_id):
    """Generate comprehensive course recommendations based on learning preferences"""
    try:
        learner_data = read_learner(learner_id)
        if not learner_data:
            return {"error": "Learner not found"}
        
        activities = learner_data.get("activities", [])
        learner_preferences = learner_data.get("preferences", [])
        learning_style = learner_data.get("learning_style", "Mixed")
        
        # Generate course recommendations based on preferences
        course_recommendations = generate_course_recommendations(learner_data)
        
        if not activities:
            # New learner - emphasize course recommendations
            return {
                "learner_id": learner_id,
                "is_new_learner": True,
                "recommendations": course_recommendations[:4],
                "recommendation_type": "course_focused",
                "learning_profile": {
                    "preferences": learner_preferences,
                    "learning_style": learning_style,
                    "recommended_subjects": list(set([r.get("subject", "") for r in course_recommendations]))
                },
                "next_steps": [
                    "Start with recommended courses matching your interests",
                    "Complete the learning style assessment",
                    "Set up your study schedule",
                    "Track your progress with activities"
                ]
            }
        
        # Existing learner - combine course recommendations with performance insights
        total_duration = sum([a.get("duration", 0) for a in activities if isinstance(a.get("duration"), (int, float))])
        scores = [a.get("score", 0) for a in activities if a.get("score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Performance-based suggestions
        performance_suggestions = []
        
        if avg_score < 70:
            performance_suggestions.append({
                "course_id": "skill-review",
                "title": f"Review & Practice in {', '.join(learner_preferences[:2]) if learner_preferences else 'Your Areas'}",
                "description": f"Focus on strengthening fundamentals based on your average score of {avg_score:.1f}",
                "reason": f"Your performance suggests more practice in core concepts",
                "type": "performance"
            })
        
        # Combine course recommendations with performance suggestions
        all_recommendations = course_recommendations[:3] + performance_suggestions
        
        return {
            "learner_id": learner_id,
            "is_new_learner": False,
            "recommendations": all_recommendations,
            "recommendation_type": "hybrid",
            "learning_profile": {
                "preferences": learner_preferences,
                "learning_style": learning_style,
                "avg_score": avg_score,
                "total_study_time": total_duration,
                "total_activities": len(activities),
                "recommended_subjects": list(set([r.get("subject", "") for r in course_recommendations]))
            },
            "insights": [
                f"Your learning style: {learning_style}",
                f"Preferred content types: {', '.join([r.get('content_type', '') for r in course_recommendations[:2]])}",
                f"Performance level: {'Excellent' if avg_score > 85 else 'Good' if avg_score > 70 else 'Needs Improvement'}",
                f"Study consistency: {'Regular' if len(activities) > 5 else 'Getting Started'}"
            ]
        }
        
    except Exception as e:
        return {"error": f"Failed to generate course recommendations: {str(e)}"}

def register_progress_st(learner_id, milestone, engagement_score, learning_velocity):
    """Register progress log using the progress model"""
    try:
        # Import LearningVelocity model
        from models.progress import LearningVelocity
        
        # Create LearningVelocity object
        velocity_obj = LearningVelocity(
            current_velocity=float(learning_velocity),
            velocity_trend="stable" if learning_velocity >= 1.0 else "decelerating"
        )
        
        # Create progress log object
        progress_log = ProgressLog(
            learner_id=learner_id,
            milestone=milestone,
            engagement_score=float(engagement_score),
            learning_velocity=velocity_obj
        )
        
        # Save to database
        result = create_progress_log(progress_log)
        
        if result:
            return True, progress_log.id, None
        else:
            return False, None, "Database error: Could not save progress log"
            
    except Exception as e:
        return False, None, str(e)

# ---------------------------
#  Main Streamlit App
# ---------------------------

# Header
st.title("🎓 Learning Agent")
st.markdown("### 📚 Welcome to the Learning Management System")

# Database status
if DB_CONNECTED and MODELS_LOADED:
    st.success("[OK] Database and models loaded successfully")
else:
    st.error("[FAIL] Some components failed to load. Check configuration.")

# Sidebar for navigation
st.sidebar.title("🧭 Navigation Menu")
page = st.sidebar.radio("📋 Select a page", [
    "👤 Register Learner", "👥 View Learners", "✏️ Update Learner",
    "📚 Register Content", "📖 View Content",
    "📊 Register Engagement", "📈 View Engagements", 
    "🎯 Register Intervention", "🎪 View Interventions",
    "📝 Register Progress", "📋 View Progress",
    "🕒 Log Activity", "📱 View Activities", 
    "📊 Score Analytics", "🎯 Score-Based Recommendations", "💡 Personalized Recommendations",
    "🛤️ Learning Paths", "📝 Submit Test Results"
])

if page == "👤 Register Learner":
    st.header("👤 Register New Learner")
    st.markdown("📝 Fill in the learner's information below:")
    
    # Registration form
    with st.form("learner_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter learner's full name")
            age = st.number_input("Age *", min_value=0, max_value=120, value=25, step=1)
            gender = st.selectbox("Gender *", ["", "Male", "Female", "Other", "Prefer not to say"])
        
        with col2:
            learning_style = st.selectbox("Learning Style *", [
                "", "Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"
            ])
            preferences = st.text_area(
                "Learning Preferences *", 
                placeholder="e.g., Mathematics, Programming, Science (comma-separated)",
                help="Enter preferences separated by commas"
            )
        
        submitted = st.form_submit_button("👤 Register Learner", type="primary")
    
    # Form submission handling
    if submitted:
        if not all([name.strip(), age, gender, learning_style, preferences.strip()]):
            st.error("[FAIL] Please fill in all required fields")
        else:
            with st.spinner("Registering learner..."):
                success, learner_id, error = register_learner_st(
                    name.strip(), age, gender, learning_style, preferences
                )
                
                if success:
                    st.success(f"[OK] Learner registered successfully!")
                    st.info(f"**Learner ID:** {learner_id}")
                    
                    # Display learner summary
                    with st.expander("View Registered Learner Details"):
                        st.json({
                            "name": name.strip(),
                            "age": int(age),
                            "gender": gender,
                            "learning_style": learning_style,
                            "preferences": [p.strip() for p in preferences.split(',') if p.strip()],
                            "id": learner_id
                        })
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "👥 View Learners":
    st.header("👥 Registered Learners")
    st.markdown("🔍 View and manage all registered learners in the system")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display learners.")
    else:
        try:
            # Debug information
            st.write(f"**Database Status**: {'Connected' if DB_CONNECTED else 'Connection Failed'}")
            st.write(f"**Models Status**: {'Loaded' if MODELS_LOADED else 'Failed to load'}")
            
            learners = read_learners()
            st.write(f"**Database returned**: {len(learners) if learners else 0} learners")
            if learners:
                st.write(f"**Sample learner**: {learners[0] if learners else 'None'}")
            
            # Add sample data if no learners exist
            if not learners:
                st.warning("[WARNING] No learners found in database. Loading sample data for demonstration...")
                
                # Create sample learners
                sample_learners = [
                    {
                        "id": "demo-alice-123",
                        "name": "Alice Johnson",
                        "age": 28,
                        "gender": "Female",
                        "learning_style": "Visual",
                        "preferences": ["Data Science", "Machine Learning", "Python"],
                        "activity_count": 3,
                        "activities": [
                            {"activity_type": "module_completed", "timestamp": "2024-01-15T10:00:00", "score": 95},
                            {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 88},
                            {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 92}
                        ]
                    },
                    {
                        "id": "demo-bob-456", 
                        "name": "Bob Smith",
                        "age": 35,
                        "gender": "Male",
                        "learning_style": "Kinesthetic",
                        "preferences": ["Web Development", "JavaScript", "React"],
                        "activity_count": 2,
                        "activities": [
                            {"activity_type": "project_completed", "timestamp": "2024-01-14T16:45:00", "score": 85},
                            {"activity_type": "code_review", "timestamp": "2024-01-18T11:20:00", "score": 90}
                        ]
                    },
                    {
                        "id": "demo-carol-789",
                        "name": "Carol Davis",
                        "age": 22,
                        "gender": "Female", 
                        "learning_style": "Auditory",
                        "preferences": ["Design", "UX/UI", "Figma"],
                        "activity_count": 1,
                        "activities": [
                            {"activity_type": "portfolio_submitted", "timestamp": "2024-01-19T13:30:00", "score": 96}
                        ]
                    }
                ]
                
                learners = sample_learners
                st.success("[OK] Sample data loaded successfully! Showing 3 demo learners.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real learners.")
            
            if learners:
                st.success(f"Found {len(learners)} learners")
                
                # Search functionality
                search_name = st.text_input("🔍 Search by name:", placeholder="Enter learner name to filter...")
                if search_name:
                    learners = [l for l in learners if search_name.lower() in l.get('name', '').lower()]
                    st.write(f"📊 **Filtered results**: {len(learners)} learners found")
                
                # Display learners
                for i, learner in enumerate(learners):
                    # Handle MongoDB _id field conversion
                    learner_id = str(learner.get('_id', learner.get('id', 'N/A')))[:8]
                    learner_name = learner.get('name', 'Unknown')
                    
                    with st.expander(f"👤 {learner_name} (ID: {learner_id}...)", expanded=(i == 0)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Personal Information:**")
                            st.write(f"• **Name**: {learner_name}")
                            st.write(f"• **Age**: {learner.get('age', 'N/A')}")
                            st.write(f"• **Gender**: {learner.get('gender', 'N/A')}")
                            st.write(f"• **Database ID**: {learner_id}")
                        
                        with col2:
                            st.write("**Learning Profile:**")
                            st.write(f"• **Learning Style**: {learner.get('learning_style', 'N/A')}")
                            preferences = learner.get('preferences', [])
                            if isinstance(preferences, str):
                                preferences = [preferences]
                            st.write(f"• **Preferences**: {', '.join(preferences)}")
                            st.write(f"• **Activities**: {learner.get('activity_count', 0)}")
                        
                        # Display recent activities
                        activities = learner.get('activities', [])
                        if activities:
                            st.write("**Recent Activities:**")
                            # Show only the 5 most recent activities
                            recent_activities = sorted(activities, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
                            for activity in recent_activities:
                                score_text = f" (Score: {activity.get('score', 'N/A')})" if activity.get('score') else ""
                                duration_text = f" [{activity.get('duration', 'N/A')}min]" if activity.get('duration') else ""
                                st.write(f"• {activity.get('activity_type', 'Unknown').replace('_', ' ').title()}{score_text}{duration_text}")
                                st.write(f"  *{activity.get('timestamp', 'Unknown')}*")
                            
                            if len(activities) > 5:
                                st.info(f"... and {len(activities) - 5} more activities. Use 'View Activities' page to see all.")
                        else:
                            st.write("**Recent Activities:** No activities recorded yet")
                            st.info("[TIP] Use the 'Log Activity' page to track learner activities!")
            else:
                st.info("No learners found in the database. Go to the 'Register Learner' page to add your first learner!")
                
        except Exception as e:
            st.error(f"Error fetching learners: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "✏️ Update Learner":
    st.header("✏️ Update Learner Information")
    st.markdown("🔧 Update learner details and preferences:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot update learners.")
    else:
        try:
            # Get all learners for selection
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found in database. Please register learners first.")
            else:
                # Learner selection for updating
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("Select Learner to Update:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Selected Learner:** {selected_learner_name}")
                    
                    # Display current learner information
                    with st.expander("Current Learner Information", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Personal Information:**")
                            st.write(f"• **Name**: {selected_learner.get('name', 'N/A')}")
                            st.write(f"• **Age**: {selected_learner.get('age', 'N/A')}")
                            st.write(f"• **Gender**: {selected_learner.get('gender', 'N/A')}")
                            st.write(f"• **Database ID**: {learner_id}")
                        
                        with col2:
                            st.write("**Learning Profile:**")
                            st.write(f"• **Learning Style**: {selected_learner.get('learning_style', 'N/A')}")
                            preferences = selected_learner.get('preferences', [])
                            if isinstance(preferences, str):
                                preferences = [preferences]
                            st.write(f"• **Preferences**: {', '.join(preferences)}")
                            st.write(f"• **Activities**: {selected_learner.get('activity_count', 0)}")
                    
                    # Update form
                    st.markdown("### Update Learner Information")
                    
                    with st.form("learner_update_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pre-fill with current values
                            new_name = st.text_input("Full Name", value=selected_learner.get('name', ''))
                            new_age = st.number_input("Age", min_value=0, max_value=120, value=int(selected_learner.get('age', 25)), step=1)
                            new_gender = st.selectbox("Gender", 
                                ["Male", "Female", "Other", "Prefer not to say"], 
                                index=["Male", "Female", "Other", "Prefer not to say"].index(selected_learner.get('gender', 'Other')) 
                                if selected_learner.get('gender', 'Other') in ["Male", "Female", "Other", "Prefer not to say"] else 2
                            )
                        
                        with col2:
                            new_learning_style = st.selectbox("Learning Style", 
                                ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"],
                                index=["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"].index(selected_learner.get('learning_style', 'Visual'))
                                if selected_learner.get('learning_style', 'Visual') in ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"] else 0
                            )
                            current_preferences = selected_learner.get('preferences', [])
                            if isinstance(current_preferences, list):
                                current_preferences_str = ', '.join(current_preferences)
                            else:
                                current_preferences_str = str(current_preferences)
                            
                            new_preferences = st.text_area(
                                "Learning Preferences", 
                                value=current_preferences_str,
                                help="Enter preferences separated by commas"
                            )
                        
                        # Field selection for update
                        st.markdown("### Select Fields to Update")
                        update_name = st.checkbox("Update Name", value=True)
                        update_age = st.checkbox("Update Age", value=False)
                        update_gender = st.checkbox("Update Gender", value=False)
                        update_learning_style = st.checkbox("Update Learning Style", value=False)
                        update_preferences = st.checkbox("Update Learning Preferences", value=False)
                        
                        submitted = st.form_submit_button("✏️ Update Learner", type="primary")
                    
                    # Form submission handling
                    if submitted:
                        # Build update fields dictionary
                        update_fields = {}
                        
                        if update_name and new_name.strip():
                            update_fields['name'] = new_name.strip()
                        
                        if update_age:
                            update_fields['age'] = int(new_age)
                        
                        if update_gender:
                            update_fields['gender'] = new_gender
                        
                        if update_learning_style:
                            update_fields['learning_style'] = new_learning_style
                        
                        if update_preferences and new_preferences.strip():
                            # Parse preferences from comma-separated string to list
                            preferences_list = [p.strip() for p in new_preferences.split(',') if p.strip()]
                            update_fields['preferences'] = preferences_list
                        
                        if not update_fields:
                            st.error("[FAIL] Please select at least one field to update and ensure it's not empty.")
                        else:
                            with st.spinner("Updating learner information..."):
                                try:
                                    # Update learner using the database function
                                    updated_learner = update_learner(learner_id, update_fields)
                                    
                                    if updated_learner:
                                        st.success(f"[OK] Learner information updated successfully!")
                                        
                                        # Display update summary
                                        with st.expander("View Updated Learner Details"):
                                            st.json({
                                                "learner_id": learner_id,
                                                "updated_fields": update_fields,
                                                "full_record": updated_learner
                                            })
                                        
                                        st.info("[TIP] **Tip**: Changes are immediately reflected in the 'View Learners' page.")
                                    else:
                                        st.error(f"[FAIL] Failed to update learner. Learner {learner_id} not found.")
                                        
                                except Exception as e:
                                    st.error(f"[FAIL] Error updating learner: {str(e)}")
                else:
                    st.info("Select a learner to update their information.")
                    
        except Exception as e:
            st.error(f"Error fetching learners for update: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "📚 Register Content":
    st.header("📚 Register New Content")
    st.markdown("📝 Add learning content to the system:")
    
    # Content registration form
    with st.form("content_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title *", placeholder="Enter content title")
            description = st.text_area("Description *", placeholder="Enter content description")
            content_type = st.selectbox("Content Type *", ["", "video", "quiz", "article", "assignment", "project"])
            course_id = st.text_input("Course ID *", placeholder="Enter course identifier")
        
        with col2:
            module_id = st.text_input("Module ID", placeholder="Enter module identifier (optional)")
            difficulty_level = st.selectbox("Difficulty Level *", ["", "beginner", "intermediate", "advanced"])
            tags = st.text_area(
                "Tags *", 
                placeholder="e.g., mathematics, programming, python (comma-separated)",
                help="Enter tags separated by commas"
            )
        
        submitted = st.form_submit_button("📚 Register Content", type="primary")
    
    # Form submission handling
    if submitted:
        if not all([title.strip(), description.strip(), content_type, course_id, difficulty_level, tags.strip()]):
            st.error("[FAIL] Please fill in all required fields")
        else:
            with st.spinner("Registering content..."):
                success, content_id, error = register_content_st(
                    title.strip(), description.strip(), content_type, course_id.strip(), 
                    module_id.strip(), difficulty_level, tags
                )
                
                if success:
                    st.success(f"[OK] Content registered successfully!")
                    st.info(f"**Content ID:** {content_id}")
                    
                    # Display content summary
                    with st.expander("View Registered Content Details"):
                        st.json({
                            "title": title.strip(),
                            "description": description.strip(),
                            "content_type": content_type,
                            "course_id": course_id.strip(),
                            "module_id": module_id.strip() if module_id.strip() else None,
                            "difficulty_level": difficulty_level,
                            "tags": [t.strip() for t in tags.split(',') if t.strip()],
                            "id": content_id
                        })
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "📖 View Content":
    st.header("📖 Content Library")
    st.markdown("📚 Browse and manage all learning content in the system")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display content.")
    else:
        try:
            contents = read_contents()
            st.write(f"**Database returned**: {len(contents) if contents else 0} content items")
            
            # Add sample data if no content exists
            if not contents:
                st.warning("[WARNING] No content found in database. Loading sample data for demonstration...")
                
                # Create sample content
                sample_contents = [
                    {
                        "id": "demo-content-1",
                        "title": "Introduction to Python Programming",
                        "description": "Learn the basics of Python programming language including variables, loops, and functions.",
                        "content_type": "video",
                        "course_id": "PYTHON-101",
                        "module_id": "module-1",
                        "difficulty_level": "beginner",
                        "tags": ["python", "programming", "basics"],
                        "created_at": "2024-01-15T10:00:00"
                    },
                    {
                        "id": "demo-content-2",
                        "title": "Data Structures Quiz",
                        "description": "Test your knowledge of arrays, lists, stacks, and queues.",
                        "content_type": "quiz",
                        "course_id": "DSA-201",
                        "module_id": "module-3",
                        "difficulty_level": "intermediate",
                        "tags": ["data-structures", "quiz", "algorithms"],
                        "created_at": "2024-01-16T14:30:00"
                    },
                    {
                        "id": "demo-content-3",
                        "title": "Advanced Machine Learning Concepts",
                        "description": "Deep dive into neural networks, deep learning, and advanced ML algorithms.",
                        "content_type": "article",
                        "course_id": "ML-301",
                        "module_id": "module-5",
                        "difficulty_level": "advanced",
                        "tags": ["machine-learning", "neural-networks", "deep-learning"],
                        "created_at": "2024-01-17T09:15:00"
                    }
                ]
                
                contents = sample_contents
                st.success("[OK] Sample data loaded successfully! Showing 3 demo content items.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real content.")
            
            if contents:
                st.success(f"Found {len(contents)} content items")
                
                # Search functionality
                search_title = st.text_input("🔍 Search by title:", placeholder="Enter content title to filter...")
                if search_title:
                    contents = [c for c in contents if search_title.lower() in c.get('title', '').lower()]
                    st.write(f"📊 **Filtered results**: {len(contents)} content items found")
                
                # Filter by content type
                content_types = [""] + list(set([c.get('content_type', '') for c in contents if c.get('content_type')]))
                selected_type = st.selectbox("📋 Filter by content type:", content_types)
                if selected_type:
                    contents = [c for c in contents if c.get('content_type') == selected_type]
                    st.write(f"🎯 **Filtered by type**: {len(contents)} content items found")
                
                # Display content
                for i, content in enumerate(contents):
                    content_id = str(content.get('_id', content.get('id', 'N/A')))[:8]
                    content_title = content.get('title', 'Unknown')
                    
                    with st.expander(f"📚 {content_title} (ID: {content_id}...)", expanded=(i == 0)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Content Information:**")
                            st.write(f"• **Title**: {content_title}")
                            st.write(f"• **Type**: {content.get('content_type', 'N/A').title()}")
                            st.write(f"• **Difficulty**: {content.get('difficulty_level', 'N/A').title()}")
                            st.write(f"• **Database ID**: {content_id}")
                        
                        with col2:
                            st.write("**Course Details:**")
                            st.write(f"• **Course ID**: {content.get('course_id', 'N/A')}")
                            st.write(f"• **Module ID**: {content.get('module_id', 'N/A')}")
                            tags = content.get('tags', [])
                            if isinstance(tags, str):
                                tags = [tags]
                            st.write(f"• **Tags**: {', '.join(tags)}")
                        
                        # Display description
                        st.write("**Description:**")
                        st.write(content.get('description', 'No description available'))
            else:
                st.info("No content found in the database. Go to the 'Register Content' page to add your first content!")
                
        except Exception as e:
            st.error(f"Error fetching content: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "📊 Register Engagement":
    st.header("📊 Register New Engagement")
    st.markdown("📈 Track learner engagement with content:")
    
    # Engagement registration form
    with st.form("engagement_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            learner_id = st.text_input("Learner ID *", placeholder="Enter learner identifier")
            content_id = st.text_input("Content ID *", placeholder="Enter content identifier")
            course_id = st.text_input("Course ID *", placeholder="Enter course identifier")
            engagement_type = st.selectbox("Engagement Type *", ["", "view", "complete", "quiz_attempt", "feedback", "interaction"])
        
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=0.0, value=0.0, step=0.5)
            score = st.number_input("Score", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            feedback = st.text_area("Feedback", placeholder="Enter feedback (optional)")
        
        submitted = st.form_submit_button("📊 Register Engagement", type="primary")
    
    # Form submission handling
    if submitted:
        if not all([learner_id.strip(), content_id.strip(), course_id, engagement_type]):
            st.error("[FAIL] Please fill in all required fields")
        else:
            with st.spinner("Registering engagement..."):
                success, engagement_id, error = register_engagement_st(
                    learner_id.strip(), content_id.strip(), course_id, engagement_type, 
                    duration, score, feedback
                )
                
                if success:
                    st.success(f"[OK] Engagement registered successfully!")
                    st.info(f"**Engagement ID:** {engagement_id}")
                    
                    # Display engagement summary
                    with st.expander("View Registered Engagement Details"):
                        st.json({
                            "learner_id": learner_id.strip(),
                            "content_id": content_id.strip(),
                            "course_id": course_id,
                            "engagement_type": engagement_type,
                            "duration": duration,
                            "score": score,
                            "feedback": feedback if feedback.strip() else None,
                            "id": engagement_id
                        })
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "📈 View Engagements":
    st.header("📈 Engagement Tracking")
    st.markdown("📊 Monitor and analyze learner engagement with content")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display engagements.")
    else:
        try:
            engagements = read_engagements()
            st.write(f"**Database returned**: {len(engagements) if engagements else 0} engagement records")
            
            # Add sample data if no engagements exist
            if not engagements:
                st.warning("[WARNING] No engagements found in database. Loading sample data for demonstration...")
                
                # Create sample engagements
                sample_engagements = [
                    {
                        "id": "demo-engagement-1",
                        "learner_id": "demo-alice-123",
                        "content_id": "demo-content-1",
                        "course_id": "PYTHON-101",
                        "engagement_type": "complete",
                        "duration": 45.5,
                        "score": 92.0,
                        "feedback": "Great explanation, very helpful!",
                        "timestamp": "2024-01-15T10:30:00"
                    },
                    {
                        "id": "demo-engagement-2",
                        "learner_id": "demo-bob-456",
                        "content_id": "demo-content-2",
                        "course_id": "DSA-201",
                        "engagement_type": "quiz_attempt",
                        "duration": 30.0,
                        "score": 78.0,
                        "feedback": "Challenging but fair questions",
                        "timestamp": "2024-01-16T14:45:00"
                    },
                    {
                        "id": "demo-engagement-3",
                        "learner_id": "demo-carol-789",
                        "content_id": "demo-content-3",
                        "course_id": "ML-301",
                        "engagement_type": "view",
                        "duration": 60.0,
                        "score": None,
                        "feedback": "Need to read this multiple times to understand",
                        "timestamp": "2024-01-17T09:30:00"
                    }
                ]
                
                engagements = sample_engagements
                st.success("[OK] Sample data loaded successfully! Showing 3 demo engagement records.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real engagements.")
            
            if engagements:
                st.success(f"Found {len(engagements)} engagement records")
                
                # Search functionality
                search_learner = st.text_input("🔍 Search by learner ID:", placeholder="Enter learner ID to filter...")
                if search_learner:
                    engagements = [e for e in engagements if search_learner.lower() in e.get('learner_id', '').lower()]
                    st.write(f"📊 **Filtered results**: {len(engagements)} engagement records found")
                
                # Filter by engagement type
                engagement_types = [""] + list(set([e.get('engagement_type', '') for e in engagements if e.get('engagement_type')]))
                selected_type = st.selectbox("📋 Filter by engagement type:", engagement_types)
                if selected_type:
                    engagements = [e for e in engagements if e.get('engagement_type') == selected_type]
                    st.write(f"🎯 **Filtered by type**: {len(engagements)} engagement records found")
                
                # Display engagements
                for i, engagement in enumerate(engagements):
                    engagement_id = str(engagement.get('_id', engagement.get('id', 'N/A')))[:8]
                    
                    with st.expander(f"📊 Engagement Record (ID: {engagement_id}...)", expanded=(i == 0)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Engagement Details:**")
                            st.write(f"• **Learner ID**: {engagement.get('learner_id', 'N/A')}")
                            st.write(f"• **Content ID**: {engagement.get('content_id', 'N/A')}")
                            st.write(f"• **Type**: {engagement.get('engagement_type', 'N/A').replace('_', ' ').title()}")
                            st.write(f"• **Database ID**: {engagement_id}")
                        
                        with col2:
                            st.write("**Performance Metrics:**")
                            st.write(f"• **Duration**: {engagement.get('duration', 'N/A')} minutes")
                            st.write(f"• **Score**: {engagement.get('score', 'N/A')}")
                            st.write(f"• **Timestamp**: {engagement.get('timestamp', 'N/A')}")
                        
                        # Display feedback
                        if engagement.get('feedback'):
                            st.write("**Feedback:**")
                            st.write(f'"{engagement.get("feedback")}"')
            else:
                st.info("No engagements found in the database. Go to the 'Register Engagement' page to add your first engagement record!")
                
        except Exception as e:
            st.error(f"Error fetching engagements: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "🎯 Register Intervention":
    st.header("🎯 Register New Intervention")
    st.markdown("🎪 Create automated interventions for learners:")
    
    # Intervention registration form
    with st.form("intervention_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            learner_id = st.text_input("Learner ID *", placeholder="Enter learner identifier")
            intervention_type = st.selectbox("Intervention Type *", ["", "motivational_message", "difficulty_adjustment", "content_                        ", "study_reminder", "achievement_notification"])
            message = st.text_area("Message *", placeholder="Enter intervention message", height=100)
        
        with col2:
            triggered_by = st.text_input("Triggered By *", placeholder="e.g., low_score, high_improvement, milestone")
        
        submitted = st.form_submit_button("🎯 Register Intervention", type="primary")
    
    # Form submission handling
    if submitted:
        if not all([learner_id.strip(), intervention_type, message.strip(), triggered_by.strip()]):
            st.error("[FAIL] Please fill in all required fields")
        else:
            with st.spinner("Registering intervention..."):
                success, intervention_id, error = register_intervention_st(
                    learner_id.strip(), intervention_type, message.strip(), triggered_by.strip()
                )
                
                if success:
                    st.success(f"[OK] Intervention registered successfully!")
                    st.info(f"**Intervention ID:** {intervention_id}")
                    
                    # Display intervention summary
                    with st.expander("View Registered Intervention Details"):
                        st.json({
                            "learner_id": learner_id.strip(),
                            "intervention_type": intervention_type,
                            "message": message.strip(),
                            "triggered_by": triggered_by.strip(),
                            "id": intervention_id
                        })
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "🎪 View Interventions":
    st.header("🎪 Intervention Management")
    st.markdown("🎯 Monitor and manage automated learner interventions")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display interventions.")
    else:
        try:
            interventions = read_interventions()
            st.write(f"**Database returned**: {len(interventions) if interventions else 0} intervention records")
            
            # Add sample data if no interventions exist
            if not interventions:
                st.warning("[WARNING] No interventions found in database. Loading sample data for demonstration...")
                
                # Create sample interventions
                sample_interventions = [
                    {
                        "id": "demo-intervention-1",
                        "learner_id": "demo-alice-123",
                        "intervention_type": "motivational_message",
                        "message": "You're improving fast! Keep up the great work!",
                        "triggered_by": "high_improvement",
                        "timestamp": "2024-01-15T11:00:00"
                    },
                    {
                        "id": "demo-intervention-2",
                        "learner_id": "demo-bob-456",
                        "intervention_type": "difficulty_adjustment",
                        "message": "We've adjusted the difficulty level based on your recent performance.",
                        "triggered_by": "low_score",
                        "timestamp": "2024-01-16T15:00:00"
                    },
                    {
                        "id": "demo-intervention-3",
                        "learner_id": "demo-carol-789",
                        "intervention_type": "content_recommendation",
                        "message": "Based on your interests, we recommend checking out our UX Design course!",
                        "triggered_by": "preference_match",
                        "timestamp": "2024-01-17T10:00:00"
                    }
                ]
                
                interventions = sample_interventions
                st.success("[OK] Sample data loaded successfully! Showing 3 demo intervention records.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real interventions.")
            
            if interventions:
                st.success(f"Found {len(interventions)} intervention records")
                
                # Search functionality
                search_learner = st.text_input("🔍 Search by learner ID:", placeholder="Enter learner ID to filter...")
                if search_learner:
                    interventions = [i for i in interventions if search_learner.lower() in i.get('learner_id', '').lower()]
                    st.write(f"📊 **Filtered results**: {len(interventions)} intervention records found")
                
                # Filter by intervention type
                intervention_types = [""] + list(set([i.get('intervention_type', '') for i in interventions if i.get('intervention_type')]))
                selected_type = st.selectbox("📋 Filter by intervention type:", intervention_types)
                if selected_type:
                    interventions = [i for i in interventions if i.get('intervention_type') == selected_type]
                    st.write(f"🎯 **Filtered by type**: {len(interventions)} intervention records found")
                
                # Display interventions
                for i, intervention in enumerate(interventions):
                    intervention_id = str(intervention.get('_id', intervention.get('id', 'N/A')))[:8]
                    
                    with st.expander(f"🎯 Intervention (ID: {intervention_id}...)", expanded=(i == 0)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Intervention Details:**")
                            st.write(f"• **Learner ID**: {intervention.get('learner_id', 'N/A')}")
                            st.write(f"• **Type**: {intervention.get('intervention_type', 'N/A').replace('_', ' ').title()}")
                            st.write(f"• **Trigger**: {intervention.get('triggered_by', 'N/A').replace('_', ' ').title()}")
                            st.write(f"• **Database ID**: {intervention_id}")
                        
                        with col2:
                            st.write("**Timing:**")
                            st.write(f"• **Timestamp**: {intervention.get('timestamp', 'N/A')}")
                        
                        # Display message
                        st.write("**Message:**")
                        st.info(f'"{intervention.get("message", "No message available")}"')
            else:
                st.info("No interventions found in the database. Go to the 'Register Intervention' page to add your first intervention record!")
                
        except Exception as e:
            st.error(f"Error fetching interventions: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "📝 Register Progress":
    st.header("📝 Register Progress Log")
    st.markdown("📊 Track learner learning progress and milestones:")
    
    # Progress registration form
    with st.form("progress_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            learner_id = st.text_input("Learner ID *", placeholder="Enter learner identifier")
            milestone = st.selectbox("Milestone *", ["", "module_completed", "quiz_passed", "course_finished", "difficulty_adjusted", "streak_achieved"])
            engagement_score = st.number_input("Engagement Score *", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        
        with col2:
            learning_velocity = st.number_input("Learning Velocity *", min_value=0.0, value=0.0, step=0.1, help="Modules per week")
        
        submitted = st.form_submit_button("📝 Register Progress", type="primary")
    
    # Form submission handling
    if submitted:
        if not all([learner_id.strip(), milestone, engagement_score, learning_velocity]):
            st.error("[FAIL] Please fill in all required fields")
        else:
            with st.spinner("Registering progress..."):
                success, progress_id, error = register_progress_st(
                    learner_id.strip(), milestone, engagement_score, learning_velocity
                )
                
                if success:
                    st.success(f"[OK] Progress registered successfully!")
                    st.info(f"**Progress Log ID:** {progress_id}")
                    
                    # Display progress summary
                    with st.expander("View Registered Progress Details"):
                        st.json({
                            "learner_id": learner_id.strip(),
                            "milestone": milestone,
                            "engagement_score": engagement_score,
                            "learning_velocity": learning_velocity,
                            "id": progress_id
                        })
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "📋 View Progress":
    st.header("📋 Progress Tracking")
    st.markdown("📊 Monitor learner progress and learning milestones")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display progress.")
    else:
        try:
            # Get progress logs with optional learner filter
            learner_filter = st.text_input("🔍 Filter by learner ID:", placeholder="Enter learner ID (leave empty to see all)")
            
            if learner_filter.strip():
                progress_logs = read_progress_logs(learner_filter.strip())
                st.write(f"👤 **Filtered by learner**: {len(progress_logs) if progress_logs else 0} progress records")
            else:
                progress_logs = read_progress_logs()
                st.write(f"📊 **Database returned**: {len(progress_logs) if progress_logs else 0} progress records")
            
            # Add sample data if no progress exists
            if not progress_logs:
                st.warning("[WARNING] No progress found in database. Loading sample data for demonstration...")
                
                # Create sample progress logs
                sample_progress = [
                    {
                        "id": "demo-progress-1",
                        "learner_id": "demo-alice-123",
                        "milestone": "module_completed",
                        "engagement_score": 92.0,
                        "learning_velocity": 2.1,
                        "timestamp": "2024-01-15T10:30:00"
                    },
                    {
                        "id": "demo-progress-2",
                        "learner_id": "demo-alice-123",
                        "milestone": "quiz_passed",
                        "engagement_score": 88.0,
                        "learning_velocity": 2.3,
                        "timestamp": "2024-01-16T14:45:00"
                    },
                    {
                        "id": "demo-progress-3",
                        "learner_id": "demo-bob-456",
                        "milestone": "difficulty_adjusted",
                        "engagement_score": 78.0,
                        "learning_velocity": 1.8,
                        "timestamp": "2024-01-16T15:00:00"
                    }
                ]
                
                progress_logs = sample_progress
                st.success("[OK] Sample data loaded successfully! Showing 3 demo progress records.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real progress logs.")
            
            if progress_logs:
                st.success(f"Found {len(progress_logs)} progress records")
                
                # Filter by milestone type
                milestones = [""] + list(set([p.get('milestone', '') for p in progress_logs if p.get('milestone')]))
                selected_milestone = st.selectbox("🎯 Filter by milestone:", milestones)
                if selected_milestone:
                    progress_logs = [p for p in progress_logs if p.get('milestone') == selected_milestone]
                    st.write(f"📋 **Filtered by milestone**: {len(progress_logs)} progress records found")
                
                # Display progress
                for i, progress in enumerate(progress_logs):
                    progress_id = str(progress.get('_id', progress.get('id', 'N/A')))[:8]
                    
                    with st.expander(f"📊 Progress Log (ID: {progress_id}...)", expanded=(i == 0)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Progress Details:**")
                            st.write(f"• **Learner ID**: {progress.get('learner_id', 'N/A')}")
                            st.write(f"• **Milestone**: {progress.get('milestone', 'N/A').replace('_', ' ').title()}")
                            st.write(f"• **Database ID**: {progress_id}")
                        
                        with col2:
                            st.write("**Performance Metrics:**")
                            st.write(f"• **Engagement Score**: {progress.get('engagement_score', 'N/A')}")
                            st.write(f"• **Learning Velocity**: {progress.get('learning_velocity', 'N/A')} modules/week")
                            st.write(f"• **Timestamp**: {progress.get('timestamp', 'N/A')}")
            else:
                st.info("No progress found in the database. Go to the 'Register Progress' page to add your first progress record!")
                
        except Exception as e:
            st.error(f"Error fetching progress: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "🕒 Log Activity":
    st.header("🕒 Log Learner Activity")
    st.markdown("📝 Track learner test and quiz completion with performance scores:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot log activities.")
    else:
        # Activity logging form
        with st.form("activity_logging_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                learner_id = st.text_input("Learner ID *", placeholder="Enter learner identifier")
                activity_type = st.selectbox("Activity Type *", [
                    "", "module_completed", "quiz_completed", "test_completed", "assignment_submitted", 
                    "project_completed", "video_watched", "reading_completed", 
                    "discussion_participated", "assessment_taken", "skill_practiced"
                ], help="🎯 Choose between test_completed or quiz_completed for assessment tracking")
                duration = st.number_input("Duration (minutes) *", min_value=0.0, value=0.0, step=0.5)
            
            with col2:
                score = st.number_input("Score (0-100)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                completion_status = st.selectbox("Completion Status *", ["", "completed", "in_progress", "not_started"])
            
            submitted = st.form_submit_button("🕒 Log Activity", type="primary")
        
        # Form submission handling
        if submitted:
            if not all([learner_id.strip(), activity_type, duration is not None, completion_status]):
                st.error("[FAIL] Please fill in all required fields")
            else:
                with st.spinner("Logging activity..."):
                    try:
                        # Log the activity using the database function
                        logged_learner = log_activity(
                            learner_id.strip(), 
                            activity_type, 
                            float(duration), 
                            float(score) if score > 0 else None
                        )
                        
                        if logged_learner:
                            st.success(f"[OK] Activity logged successfully for learner {learner_id}!")
                            
                            # Display activity summary
                            with st.expander("View Logged Activity Details"):
                                st.json({
                                    "learner_id": learner_id.strip(),
                                    "activity_type": activity_type,
                                    "duration": float(duration),
                                    "score": float(score) if score > 0 else None,
                                    "completion_status": completion_status,
                                    "timestamp": datetime.now().isoformat(),
                                    "activity_count": logged_learner.get("activity_count", 0)
                                })
                        else:
                            st.error(f"[FAIL] Failed to log activity. Learner {learner_id} not found.")
                            
                    except Exception as e:
                        st.error(f"[FAIL] Error logging activity: {str(e)}")

elif page == "📱 View Activities":
    st.header("📱 Activity Log Viewer")
    st.markdown("📊 View and analyze logged learner activities:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display activities.")
    else:
        try:
            # Get all learners to populate the filter
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found in database. Please register learners first.")
            else:
                # Learner selection for activity viewing
                learner_options = {f"{l.get('name', 'Unknown')} ({l.get('_id', l.get('id', 'N/A'))})": l.get('_id', l.get('id')) for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner_id = learner_options[selected_learner_name]
                    st.info(f"**Viewing activities for learner:** {selected_learner_name}")
                    
                    # Get learner activities using the dedicated function
                    activities = read_learner_activities(selected_learner_id)
                    learner_data = read_learner(selected_learner_id)
                    
                    if activities is not None:  # Check if learner exists (even if no activities)
                        
                        if activities:
                            st.success(f"Found {len(activities)} activities")
                            
                            # Activity type filter
                            activity_types = [""] + list(set([a.get('activity_type', '') for a in activities if a.get('activity_type')]))
                            selected_type = st.selectbox("📋 Filter by activity type:", activity_types)
                            
                            if selected_type:
                                activities = [a for a in activities if a.get('activity_type') == selected_type]
                                st.write(f"🎯 **Filtered by type**: {len(activities)} activities found")
                            
                            # Display activities with emojis and visual indicators
                            for i, activity in enumerate(reversed(activities)):  # Show newest first
                                activity_type = activity.get('activity_type', 'Unknown').replace('_', ' ').title()
                                timestamp = activity.get('timestamp', 'Unknown')
                                duration = activity.get('duration', 'N/A')
                                score = activity.get('score', 'N/A')
                                
                                # Add emojis based on activity type
                                emoji_map = {
                                    'test_completed': '📝',
                                    'quiz_completed': '❓', 
                                    'module_completed': '📚',
                                    'assignment_submitted': '📋',
                                    'project_completed': '🛠️',
                                    'video_watched': '🎥',
                                    'reading_completed': '📖',
                                    'discussion_participated': '💬',
                                    'assessment_taken': '📊',
                                    'skill_practiced': '💪'
                                }
                                
                                activity_emoji = emoji_map.get(activity.get('activity_type'), '📊')
                                
                                with st.expander(f"{activity_emoji} {activity_type} - {timestamp[:19]}", expanded=(i < 3)):  # Show first 3 expanded
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write("**Activity Details:**")
                                        st.write(f"• **Type**: {activity_type}")
                                        st.write(f"• **Duration**: {duration} minutes")
                                        st.write(f"• **Score**: {score}")
                                    
                                    with col2:
                                        st.write("**Timing:**")
                                        st.write(f"• **Timestamp**: {timestamp}")
                                    
                                    # Calculate engagement metrics with visual indicators
                                    if score != 'N/A' and duration != 'N/A':
                                        st.write("**Performance Metrics:**")
                                        efficiency = float(score) / float(duration) * 60 if float(duration) > 0 else 0  # Score per hour
                                        
                                        # Color coding for scores
                                        score_val = float(score)
                                        if score_val >= 80:
                                            score_indicator = "🟢 Excellent"
                                        elif score_val >= 60:
                                            score_indicator = "🟡 Good"
                                        else:
                                            score_indicator = "🔴 Needs Improvement"
                                        
                                        st.write(f"• **Score**: {score} ({score_indicator})")
                                        st.write(f"• **Efficiency**: {efficiency:.2f} points/hour")
                                        
                                        # Progress bar for score
                                        st.progress(score_val / 100)
                            
                            # Activity summary with emojis and visual elements
                            st.markdown("---")
                            st.subheader("🌟 Activity Summary")
                            
                            total_duration = sum([a.get('duration', 0) for a in activities if isinstance(a.get('duration'), (int, float))])
                            avg_score = sum([a.get('score', 0) for a in activities if isinstance(a.get('score'), (int, float)) and a.get('score') is not None])
                            score_count = len([a for a in activities if isinstance(a.get('score'), (int, float)) and a.get('score') is not None])
                            
                            # Count test vs quiz activities
                            test_count = len([a for a in activities if a.get('activity_type') == 'test_completed'])
                            quiz_count = len([a for a in activities if a.get('activity_type') == 'quiz_completed'])
                            
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric("📊 Total Activities", len(activities))
                            with col2:
                                st.metric("⏱️ Total Duration", f"{total_duration:.1f} min")
                            with col3:
                                st.metric("🎯 Average Score", f"{avg_score/score_count:.1f}" if score_count > 0 else "N/A")
                            with col4:
                                st.metric("📝 Tests Completed", test_count)
                            with col5:
                                st.metric("❓ Quizzes Completed", quiz_count)
                            
                            # Assessment breakdown
                            if test_count > 0 or quiz_count > 0:
                                st.markdown("📊 **Assessment Breakdown:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if test_count > 0:
                                        st.info(f"📝 **Tests:** {test_count} completed")
                                with col2:
                                    if quiz_count > 0:
                                        st.info(f"❓ **Quizzes:** {quiz_count} completed")
                        else:
                            st.info(f"No activities found for learner {selected_learner_name}. Use the 'Log Activity' page to add activities.")
                    else:
                        st.error(f"Failed to retrieve data for learner {selected_learner_name}")
                else:
                    st.info("Select a learner to view their activities.")
                    
        except Exception as e:
            st.error(f"Error fetching activities: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "📊 Score Analytics":
    st.header("📊 View Learner Scores")
    st.markdown("🎯 View comprehensive test and quiz performance metrics with personalized recommendations")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display scores.")
    elif not SCORING_LOADED:
        st.error("Scoring system not loaded. Please check configuration.")
    else:
        try:
            # Get all learners for score analysis
            learners = read_learners()
            
            if not learners:
                st.warning("⚠️ No learners found in database. Please register learners first.")
            else:
                # Learner selection for score viewing
                learner_options = {f"{l.get('name', 'Unknown')} ({l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner for Score Analysis:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"📊 Analyzing scores for: {selected_learner_name}")
                    
                    # Calculate comprehensive scores
                    score_data = comprehensive_scoring_system.calculate_learner_score(selected_learner)
                    
                    if 'error' in score_data:
                        st.error(f"❌ Error calculating scores: {score_data['error']}")
                    else:
                        # 🎨 Display Overall Performance
                        st.markdown("---")
                        st.subheader("🌟 Overall Performance")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            overall_score = score_data.get('overall_score', 0)
                            performance_level = score_data.get('performance_level', 'unknown').title()
                            performance_emoji = score_data.get('performance_emoji', '📊')
                            
                            st.metric(
                                "🎯 Overall Score", 
                                f"{overall_score}/100", 
                                delta=f"{score_data.get('performance_emoji', '📊')} {performance_level}"
                            )
                            
                            # Progress bar for overall score
                            st.progress(overall_score / 100)
                            
                        with col2:
                            test_avg = score_data.get('component_scores', {}).get('test_average', 0)
                            st.metric("📝 Test Average", f"{test_avg:.1f}%")
                            st.progress(test_avg / 100)
                            
                        with col3:
                            quiz_avg = score_data.get('component_scores', {}).get('quiz_average', 0)
                            st.metric("❓ Quiz Average", f"{quiz_avg:.1f}%")
                            st.progress(quiz_avg / 100)
                        
                        # 📊 Component Scores Breakdown
                        st.markdown("---")
                        st.subheader("📈 Detailed Score Breakdown")
                        
                        component_scores = score_data.get('component_scores', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📝 Test Score", f"{component_scores.get('test_average', 0):.1f}%")
                        with col2:
                            st.metric("❓ Quiz Score", f"{component_scores.get('quiz_average', 0):.1f}%")
                        with col3:
                            st.metric("🔥 Engagement", f"{component_scores.get('engagement_score', 0):.1f}%")
                        with col4:
                            st.metric("🎁 Bonus", f"+{component_scores.get('engagement_bonus', 0):.1f}")
                        
                        # 💡 Insights and Recommendations
                        st.markdown("---")
                        st.subheader("💡 Personalized Insights")
                        
                        insights = score_data.get('insights', [])
                        if insights:
                            for insight in insights:
                                st.info(f"💡 {insight}")
                        
                        # 🎯 Performance-Based Recommendations
                        st.markdown("---")
                        st.subheader("🎯 Personalized Recommendations")
                        
                        recommendations = score_data.get('recommendations', [])
                        if recommendations:
                            for i, rec in enumerate(recommendations, 1):
                                with st.container():
                                    st.markdown(f"""
                                    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                                        <h4 style="margin: 0; color: #1f77b4;">{rec.get('emoji', '🎯')} {rec.get('title', 'Recommendation')}</h4>
                                        <p style="margin: 0.5rem 0; color: #333;">{rec.get('description', 'No description available')}</p>
                                        <p style="margin: 0; font-size: 0.9em; color: #666;"><strong>Priority:</strong> {rec.get('priority', 'medium').title()}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # 📚 Course Recommendations
                        st.markdown("---")
                        st.subheader("📚 Recommended Courses")
                        
                        course_recs = score_data.get('course_recommendations', [])
                        if course_recs:
                            for course in course_recs:
                                with st.container():
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(f"**{course.get('emoji', '📚')} {course.get('title', 'Course Title')}**")
                                        st.write(f"Difficulty: {course.get('difficulty', 'beginner').title()}")
                                    
                                    with col2:
                                        if st.button(f"🚀 Start Course", key=f"start_course_{course.get('id', '')}"):
                                            st.success(f"Ready to start: {course.get('title', 'Course')}!")
                                    
                                    st.markdown("---")
                        
                        # 🛤️ Learning Path
                        st.markdown("---")
                        st.subheader("🛤️ Your Learning Path")
                        
                        learning_path = score_data.get('learning_path', [])
                        if learning_path:
                            for i, step in enumerate(learning_path, 1):
                                st.write(f"{i}. {step}")
                        
                        # 📅 Recent Assessment History
                        st.markdown("---")
                        st.subheader("📅 Recent Assessment History")
                        
                        activities = selected_learner.get('activities', [])
                        test_activities = [a for a in activities if a.get('activity_type') in ['test_completed', 'quiz_completed']]
                        
                        if test_activities:
                            # Show recent 5 assessments
                            recent_assessments = sorted(test_activities, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
                            
                            for activity in recent_assessments:
                                activity_type = activity.get('activity_type', 'Unknown').replace('_', ' ').title()
                                score = activity.get('score', 'N/A')
                                timestamp = activity.get('timestamp', 'Unknown')[:19]  # Remove microseconds
                                
                                # Color coding based on score
                                if score != 'N/A':
                                    score_val = float(score)
                                    if score_val >= 80:
                                        score_color = "🟢"
                                    elif score_val >= 60:
                                        score_color = "🟡"
                                    else:
                                        score_color = "🔴"
                                else:
                                    score_color = "⚪"
                                
                                with st.expander(f"{score_color} {activity_type} - {timestamp}"):
                                    st.write(f"**Score:** {score}")
                                    st.write(f"**Duration:** {activity.get('duration', 'N/A')} minutes")
                                    st.write(f"**Type:** {activity_type}")
                        
                        else:
                            st.info("📝 No test or quiz activities found. Start logging assessments to see your progress!")
                        
                        # 📊 Export Score Report
                        st.markdown("---")
                        st.subheader("📥 Export Score Report")
                        
                        if st.button("📊 Generate Score Report"):
                            # Create a comprehensive report
                            report_data = {
                                "learner_name": selected_learner.get('name', 'Unknown'),
                                "analysis_date": datetime.now().isoformat(),
                                "overall_score": score_data.get('overall_score', 0),
                                "performance_level": score_data.get('performance_level', 'unknown'),
                                "component_scores": score_data.get('component_scores', {}),
                                "insights": score_data.get('insights', []),
                                "recommendations": score_data.get('recommendations', []),
                                "learning_path": score_data.get('learning_path', [])
                            }
                            
                            st.success("📊 Score report generated successfully!")
                            st.json(report_data)
                            
                            # Offer download
                            report_json = json.dumps(report_data, indent=2)
                            st.download_button(
                                label="📥 Download Report (JSON)",
                                data=report_json,
                                file_name=f"score_report_{selected_learner.get('name', 'learner').replace(' ', '_')}.json",
                                mime="application/json"
                            )
                else:
                    st.info("🎯 Select a learner to view their comprehensive score analysis.")
                    
        except Exception as e:
            st.error(f"❌ Error fetching score data: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "💡 Personalized Recommendations":
    st.header("💡 Personalized Learning Recommendations")
    st.markdown("🤖 AI-powered recommendations to enhance your learning journey:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot generate recommendations.")
    else:
        try:
            # Get all learners for recommendation generation
            learners = read_learners()
            
            # Add sample data if no learners exist (same logic as View Learners)
            if not learners:
                st.warning("[WARNING] No learners found in database. Loading sample data for demonstration...")
                
                # Create sample learners (same as View Learners page)
                sample_learners = [
                    {
                        "id": "demo-alice-123",
                        "name": "Alice Johnson",
                        "age": 28,
                        "gender": "Female",
                        "learning_style": "Visual",
                        "preferences": ["Data Science", "Machine Learning", "Python"],
                        "activity_count": 3,
                        "activities": [
                            {"activity_type": "module_completed", "timestamp": "2024-01-15T10:00:00", "score": 95},
                            {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "score": 88},
                            {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "score": 92}
                        ]
                    },
                    {
                        "id": "demo-bob-456", 
                        "name": "Bob Smith",
                        "age": 35,
                        "gender": "Male",
                        "learning_style": "Kinesthetic",
                        "preferences": ["Web Development", "JavaScript", "React"],
                        "activity_count": 2,
                        "activities": [
                            {"activity_type": "project_completed", "timestamp": "2024-01-14T16:45:00", "score": 85},
                            {"activity_type": "code_review", "timestamp": "2024-01-18T11:20:00", "score": 90}
                        ]
                    },
                    {
                        "id": "demo-carol-789",
                        "name": "Carol Davis",
                        "age": 22,
                        "gender": "Female", 
                        "learning_style": "Auditory",
                        "preferences": ["Design", "UX/UI", "Figma"],
                        "activity_count": 1,
                        "activities": [
                            {"activity_type": "portfolio_submitted", "timestamp": "2024-01-19T13:30:00", "score": 96}
                        ]
                    }
                ]
                
                learners = sample_learners
                st.success("[OK] Sample data loaded successfully! Showing 3 demo learners.")
                st.info("[TIP] **Note**: This is demo data. Use the registration form to add real learners.")
            
            if learners:
                # API configuration
                api_base_url = st.text_input(
                    "API Base URL", 
                    value="http://localhost:5000",
                    help="URL of your Flask API server"
                )
                
                # Learner selection for recommendations
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner for Recommendations:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Generating recommendations for:** {selected_learner_name}")
                    
                    # Show learner context
                    with st.expander("Learner Profile", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Personal Information:**")
                            st.write(f"• **Name**: {selected_learner.get('name', 'N/A')}")
                            st.write(f"• **Age**: {selected_learner.get('age', 'N/A')}")
                            st.write(f"• **Learning Style**: {selected_learner.get('learning_style', 'N/A')}")
                        
                        with col2:
                            st.write("**Learning Progress:**")
                            st.write(f"• **Total Activities**: {selected_learner.get('activity_count', 0)}")
                            activities = selected_learner.get('activities', [])
                            if activities:
                                scores = [a.get('score', 0) for a in activities if a.get('score') is not None]
                                avg_score = sum(scores) / len(scores) if scores else 0
                                st.write(f"• **Average Score**: {avg_score:.1f}")
                                st.write(f"• **Study Time**: {sum([a.get('duration', 0) for a in activities]):.1f} minutes")
                            else:
                                st.write("• **Average Score**: N/A (No activities yet)")
                                st.write("• **Study Time**: N/A (No activities yet)")
                    
                    # Generate recommendations button
                    if st.button("🎯 Generate Recommendations", type="primary"):
                        with st.spinner("Analyzing learner data and generating personalized recommendations..."):
                            try:
                                # Get recommendations from API
                                recommendations = get_recommendations(learner_id, api_base_url)
                                
                                if "error" in recommendations:
                                    st.error(f"[FAIL] Error generating recommendations: {recommendations['error']}")
                                    st.info("[TIP] **Tip**: Make sure your Flask API server is running on the specified URL.")
                                else:
                                    st.success("[OK] Recommendations generated successfully!")
                                    
                                    # Display recommendations
                                    st.markdown("---")
                                    
                                    # Display enhanced recommendations
                                    display_enhanced_recommendations(recommendations)
                                    
                                    # Display learning profile and insights
                                    learning_profile = recommendations.get("learning_profile", {})
                                    
                                    if learning_profile:
                                        st.subheader("[STATS] Your Learning Profile")
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.write("**Personal Preferences:**")
                                            preferences = learning_profile.get("preferences", [])
                                            if preferences:
                                                for pref in preferences:
                                                    st.write(f"• {pref}")
                                            else:
                                                st.write("• No preferences set")
                                            
                                            st.write(f"**Learning Style:** {learning_profile.get('learning_style', 'Mixed')}")
                                        
                                        with col2:
                                            st.write("**Recommended Subjects:**")
                                            subjects = learning_profile.get("recommended_subjects", [])
                                            if subjects:
                                                for subject in subjects:
                                                    st.write(f"• {subject}")
                                            else:
                                                st.write("• General studies")
                                            
                                            # Performance metrics for existing learners
                                            if not recommendations.get("is_new_learner", False):
                                                avg_score = learning_profile.get("avg_score", 0)
                                                total_time = learning_profile.get("total_study_time", 0)
                                                st.write(f"**Average Score:** {avg_score:.1f}")
                                                st.write(f"**Study Time:** {total_time:.0f} minutes")
                                    
                                    # Display insights
                                    insights = recommendations.get("insights", [])
                                    if insights:
                                        st.subheader("[TIP] Learning Insights")
                                        for insight in insights:
                                            st.write(f"• {insight}")
                                    
                                    # Display next steps for new learners
                                    if recommendations.get("is_new_learner", False):
                                        next_steps = recommendations.get("next_steps", [])
                                        if next_steps:
                                            st.subheader("[START] Getting Started")
                                            for i, step in enumerate(next_steps, 1):
                                                st.write(f"{i}. {step}")
                                    
                                    # Enhanced action buttons with course focus
                                    st.markdown("---")
                                    st.subheader("[TARGET] Quick Actions")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        if st.button("[NOTE] Log Activity", use_container_width=True):
                                            st.info("Track your learning progress and activities!")
                                    
                                    with col2:
                                        if st.button("[STATS] View Progress", use_container_width=True):
                                            st.info("See detailed analytics and performance metrics!")
                                    
                                    with col3:
                                        if st.button("[EDU] Browse Courses", use_container_width=True):
                                            st.info("Explore all available courses in our catalog!")
                                    
                                    with col4:
                                        if st.button("[SETTINGS] Update Profile", use_container_width=True):
                                            st.info("Update your learning preferences and style!")
                                    
                                    # Success message
                                    st.success("[SUCCESS] **Recommendations Generated Successfully!**")
                                    st.info("[TIP] **Pro Tip:** Click on course titles to get started, and use the 'Log Activity' page to track your learning journey!")
                            
                            except Exception as e:
                                st.error(f"[FAIL] Failed to generate recommendations: {str(e)}")
                                st.info("[TIP] **Troubleshooting Tips:**")
                                st.write("1. Check if the Flask API server is running")
                                st.write("2. Verify the API Base URL is correct")
                                st.write("3. Ensure the learner ID exists in the database")
                else:
                    st.info("Select a learner to generate personalized recommendations.")
                    
        except Exception as e:
            st.error(f"Error fetching recommendations: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "📊 Score Analytics":
    st.header("📊 Comprehensive Score Analytics")
    st.markdown("📈 Analyze learner performance with advanced scoring metrics based on test and quiz marks:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot access scoring analytics.")
    else:
        try:
            # Import the scoring components
            from ml.scoring_engine import get_learner_score_summary, ScoringEngine
            from models.test_result import TestResult
            from utils.crud_operations import read_engagements
            
            # Get all learners
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                # Learner selection
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                
                selected_learner_name = st.selectbox("👤 Select Learner for Score Analysis:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Analyzing score for:** {selected_learner_name}")
                    
                    # Get test results from engagements
                    engagements = read_engagements()
                    test_engagements = [
                        e for e in engagements 
                        if e.get('learner_id') == str(learner_id) 
                        and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
                    ]
                    
                    # Convert engagements to TestResult objects
                    test_results = []
                    for engagement in test_engagements:
                        try:
                            test_result = TestResult(
                                learner_id=str(learner_id),
                                test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                                test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                                course_id=engagement['course_id'],
                                content_id=engagement['content_id'],
                                score=engagement.get('score', 0),
                                max_score=engagement.get('metadata', {}).get('max_score', 100),
                                time_taken=engagement.get('duration'),
                                attempts=engagement.get('metadata', {}).get('attempts', 1),
                                completed_at=engagement['timestamp']
                            )
                            test_results.append(test_result)
                        except Exception:
                            continue
                    
                    if st.button("🔍 Calculate Comprehensive Score", type="primary"):
                        with st.spinner("Calculating comprehensive score analysis..."):
                            # Generate score summary
                            score_summary = get_learner_score_summary(str(learner_id), test_results)
                            
                            # Display score summary
                            st.subheader("[TARGET] Score Summary")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Average Score", f"{score_summary.average_score:.1f}%")
                            with col2:
                                trend_emoji = "📈" if score_summary.score_trend == "improving" else "📉" if score_summary.score_trend == "declining" else "➡️"
                                st.metric("Score Trend", f"{trend_emoji} {score_summary.score_trend.title()}")
                            with col3:
                                st.metric("Confidence Level", f"{score_summary.confidence_score:.1f}/100")
                            with col4:
                                level_emoji = "🏆" if score_summary.recommendation_level == "advanced" else "🎯" if score_summary.recommendation_level == "intermediate" else "🌱"
                                st.metric("Level", f"{level_emoji} {score_summary.recommendation_level.title()}")
                            
                            # Performance analysis
                            st.subheader("[GROWTH] Performance Analysis")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Strengths & Weaknesses:**")
                                st.write(f"• **Strongest Subject:** {score_summary.strongest_subject}")
                                st.write(f"• **Weakest Subject:** {score_summary.weakest_subject}")
                                st.write(f"• **Total Tests:** {score_summary.total_tests}")
                                st.write(f"• **Latest Score:** {score_summary.latest_score:.1f}%")
                            
                            with col2:
                                st.write("**Performance Insights:**")
                                if score_summary.confidence_score >= 80:
                                    st.write("• Very consistent performance")
                                elif score_summary.confidence_score >= 60:
                                    st.write("• Moderately consistent performance")
                                else:
                                    st.write("• Performance shows high variability")
                                
                                if score_summary.score_trend == "improving":
                                    st.write("• Strong upward learning trajectory")
                                elif score_summary.score_trend == "declining":
                                    st.write("• Performance needs attention")
                                else:
                                    st.write("• Stable learning pattern")
                            
                            # Display test results table
                            if test_results:
                                st.subheader("[NOTE] Test Results History")
                                test_data = []
                                for test in test_results:
                                    test_data.append({
                                        'Test ID': test.test_id,
                                        'Type': test.test_type.title(),
                                        'Course': test.course_id,
                                        'Score': f"{test.percentage:.1f}%",
                                        'Date': test.completed_at.strftime('%Y-%m-%d') if hasattr(test.completed_at, 'strftime') else str(test.completed_at)[:10]
                                    })
                                
                                if test_data:
                                    import pandas as pd
                                    df = pd.DataFrame(test_data)
                                    st.dataframe(df, use_container_width=True)
                            
                            st.success("[SUCCESS] Score analysis completed successfully!")
                            st.info("[TIP] Use this analysis to identify areas for improvement and track learning progress.")
                
                else:
                    st.info("Select a learner to analyze their scoring profile.")
                    
        except Exception as e:
            st.error(f"Error in score analytics: {str(e)}")

elif page == "🎯 Score-Based Recommendations":
    st.header("🎯 Score-Based Course Recommendations")
    st.markdown("📚 Get personalized course recommendations based on your test and quiz performance:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot generate score-based recommendations.")
    else:
        try:
            from ml.scoring_engine import get_learner_score_summary
            from ml.score_based_recommender import ScoreBasedRecommender
            from utils.crud_operations import read_engagements
            
            # Get all learners
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                # Learner selection
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner for Score-Based Recommendations:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Generating recommendations for:** {selected_learner_name}")
                    
                    # Get test results
                    engagements = read_engagements()
                    test_engagements = [
                        e for e in engagements 
                        if e.get('learner_id') == str(learner_id) 
                        and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
                    ]
                    
                    # Convert to TestResult objects
                    test_results = []
                    for engagement in test_engagements:
                        try:
                            from models.test_result import TestResult
                            test_result = TestResult(
                                learner_id=str(learner_id),
                                test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                                test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                                course_id=engagement['course_id'],
                                content_id=engagement['content_id'],
                                score=engagement.get('score', 0),
                                max_score=engagement.get('metadata', {}).get('max_score', 100),
                                time_taken=engagement.get('duration'),
                                attempts=engagement.get('metadata', {}).get('attempts', 1),
                                completed_at=engagement['timestamp']
                            )
                            test_results.append(test_result)
                        except Exception:
                            continue
                    
                    # Configuration
                    col1, col2 = st.columns(2)
                    with col1:
                        recommendation_count = st.slider("Number of recommendations", 3, 10, 5)
                    with col2:
                        include_learning_path = st.checkbox("Include learning path", value=True)
                    
                    if st.button("🎯 Generate Score-Based Recommendations", type="primary"):
                        with st.spinner("Analyzing performance and generating recommendations..."):
                            # Generate score summary
                            score_summary = get_learner_score_summary(str(learner_id), test_results)
                            
                            # Get recommendations
                            recommender = ScoreBasedRecommender()
                            recommendations = recommender.get_personalized_recommendations(str(learner_id), score_summary, top_n=recommendation_count)
                            
                            if not recommendations:
                                st.warning("No suitable recommendations found. Make sure the learner has test results.")
                            else:
                                # Display current performance
                                st.subheader("[STATS] Current Performance Summary")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Average Score", f"{score_summary.average_score:.1f}%")
                                with col2:
                                    st.metric("Performance Level", score_summary.recommendation_level.title())
                                with col3:
                                    st.metric("Confidence", f"{score_summary.confidence_score:.1f}/100")
                                
                                # Display recommendations
                                st.subheader("[BOOK] Personalized Course Recommendations")
                                
                                for i, rec in enumerate(recommendations, 1):
                                    course = rec['course']
                                    with st.container():
                                        st.markdown(f"""
                                        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                                            <h4 style="margin: 0; color: #1f77b4;">[BOOK] {course.get('title', 'Course Title')} (#{i})</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        col1, col2 = st.columns([2, 1])
                                        
                                        with col1:
                                            st.write(f"**Description:** {course.get('description', 'No description available')}")
                                            st.write(f"**Difficulty:** {course.get('difficulty_level', 'intermediate').title()}")
                                            st.write(f"**Estimated Time:** {rec.get('estimated_completion_time', 'N/A')}")
                                            st.write(f"**Why Recommended:** {rec.get('recommendation_reason', 'Based on your performance')}")
                                        
                                        with col2:
                                            st.write(f"**Match Score:** {rec.get('match_score', 0):.1f}/100")
                                            st.write(f"**Confidence:** {rec.get('confidence', 0):.1f}%")
                                            st.write(f"**Content Type:** {course.get('content_type', 'video').title()}")
                                        
                                        # Action buttons
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            if st.button(f"[TARGET] Start Course", key=f"start_score_rec_{i}"):
                                                st.success(f"Ready to start: {course.get('title', 'Course')}!")
                                        
                                        with col2:
                                            if st.button(f"[LIST] Add to Wishlist", key=f"wishlist_score_rec_{i}"):
                                                st.info(f"Added '{course.get('title', 'Course')}' to your wishlist!")
                                        
                                        with col3:
                                            if st.button(f"[STATS] View Details", key=f"details_score_rec_{i}"):
                                                with st.expander("Course Details", expanded=False):
                                                    st.write(f"**Course ID:** `{course.get('id', 'N/A')}`")
                                                    st.write(f"**Tags:** {course.get('tags', [])}")
                                                    if rec.get('next_steps'):
                                                        st.write(f"**Next Steps:** {rec['next_steps']}")
                                        
                                        st.markdown("---")
                                
                                # Learning path if requested
                                if include_learning_path:
                                    st.subheader("🛤️ Recommended Learning Path")
                                    learning_path = recommender.generate_learning_path(str(learner_id), score_summary)
                                    
                                    if learning_path and learning_path.get('learning_path'):
                                        path_items = learning_path['learning_path']
                                        st.write(f"**Path contains {len(path_items)} courses**")
                                        st.write(f"**Estimated duration:** {learning_path.get('estimated_duration', 'N/A')}")
                                        st.write(f"**Expected outcome:** {learning_path.get('expected_outcome', 'N/A')}")
                                        
                                        for item in path_items:
                                            st.write(f"**{item.get('sequence', '')}.** {item.get('title', 'Course')}")
                                            st.write(f"   - Difficulty: {item.get('difficulty', 'N/A').title()}")
                                            st.write(f"   - Duration: {item.get('estimated_time', 'N/A')}")
                                            st.write(f"   - Match Confidence: {item.get('match_confidence', 0):.1f}%")
                                            st.write("")
                                
                                st.success("[SUCCESS] Score-based recommendations generated successfully!")
                                st.info("[TIP] These recommendations are specifically tailored to your test and quiz performance!")
                
                else:
                    st.info("Select a learner to generate score-based recommendations.")
                    
        except Exception as e:
            st.error(f"Error generating score-based recommendations: {str(e)}")

elif page == "🛤️ Learning Paths":
    st.header("🛤️ Personalized Learning Paths")
    st.markdown("🗺️ Get structured learning journeys based on your performance analysis:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot generate learning paths.")
    else:
        try:
            from ml.scoring_engine import get_learner_score_summary
            from ml.score_based_recommender import ScoreBasedRecommender
            from utils.crud_operations import read_engagements
            
            # Get all learners
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner for Learning Path:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Generating learning path for:** {selected_learner_name}")
                    
                    # Get test results
                    engagements = read_engagements()
                    test_engagements = [
                        e for e in engagements 
                        if e.get('learner_id') == str(learner_id) 
                        and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
                    ]
                    
                    # Convert to TestResult objects
                    test_results = []
                    for engagement in test_engagements:
                        try:
                            from models.test_result import TestResult
                            test_result = TestResult(
                                learner_id=str(learner_id),
                                test_id=engagement.get('metadata', {}).get('test_id', engagement['content_id']),
                                test_type=engagement.get('engagement_type', 'test').replace('_attempt', ''),
                                course_id=engagement['course_id'],
                                content_id=engagement['content_id'],
                                score=engagement.get('score', 0),
                                max_score=engagement.get('metadata', {}).get('max_score', 100),
                                time_taken=engagement.get('duration'),
                                attempts=engagement.get('metadata', {}).get('attempts', 1),
                                completed_at=engagement['timestamp']
                            )
                            test_results.append(test_result)
                        except Exception:
                            continue
                    
                    if st.button("🗺️ Generate Personalized Learning Path", type="primary"):
                        with st.spinner("Creating your personalized learning path..."):
                            # Generate score summary
                            score_summary = get_learner_score_summary(str(learner_id), test_results)
                            
                            # Generate learning path
                            recommender = ScoreBasedRecommender()
                            learning_path = recommender.generate_learning_path(str(learner_id), score_summary)
                            
                            if not learning_path or not learning_path.get('learning_path'):
                                st.warning("No suitable learning path found. Make sure the learner has test results and preferences.")
                            else:
                                # Display learning path
                                st.subheader("[TARGET] Your Personalized Learning Path")
                                
                                path_items = learning_path['learning_path']
                                
                                # Path overview
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Courses", len(path_items))
                                with col2:
                                    total_hours = learning_path.get('estimated_duration', '0 hours')
                                    st.metric("Duration", total_hours)
                                with col3:
                                    level = learning_path.get('starting_level', 'beginner').title()
                                    st.metric("Starting Level", level)
                                
                                # Display learning sequence
                                st.subheader("[BOOK] Learning Sequence")
                                
                                for i, item in enumerate(path_items, 1):
                                    with st.container():
                                        st.markdown(f"""
                                        <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #28a745;">
                                            <h4 style="margin: 0; color: #28a745;">{i}. {item.get('title', 'Course')}</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**Difficulty:** {item.get('difficulty', 'N/A').title()}")
                                            st.write(f"**Estimated Time:** {item.get('estimated_time', 'N/A')}")
                                            st.write(f"**Skills Covered:** {', '.join(item.get('focus_skills', [])[:3])}")
                                        
                                        with col2:
                                            st.write(f"**Match Confidence:** {item.get('match_confidence', 0):.1f}%")
                                            st.write(f"**Prerequisites:** {'Met' if item.get('prerequisites_met', True) else 'Not Met'}")
                                        
                                        # Progress indicator
                                        if i == 1:
                                            st.success("[START] Recommended starting point")
                                        elif i <= len(path_items) // 2:
                                            st.info("[PROGRESS] Next in sequence")
                                        else:
                                            st.warning("[ADVANCED] Advanced topics")
                                        
                                        st.markdown("---")
                                
                                # Learning outcomes
                                st.subheader("[TARGET] Expected Learning Outcomes")
                                expected_outcome = learning_path.get('expected_outcome', 'Enhanced knowledge and skills')
                                st.write(f"**By completing this path, you will achieve:** {expected_outcome}")
                                
                                st.success("[SUCCESS] Learning path generated successfully!")
                                st.info("[TIP] Follow this structured path for optimal learning outcomes based on your current performance!")
                
                else:
                    st.info("Select a learner to generate a learning path.")
                    
        except Exception as e:
            st.error(f"Error generating learning path: {str(e)}")

elif page == "📝 Submit Test Results":
    st.header("📝 Submit Test and Quiz Results")
    st.markdown("📊 Record test and quiz results for scoring analysis:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot submit test results.")
    else:
        try:
            from models.test_result import TestResult
            from utils.crud_operations import read_learners, create_engagement
            
            # Get all learners for selection
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                # Learner selection
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                selected_learner_name = st.selectbox("👤 Select Learner:", [""] + list(learner_options.keys()))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Submitting test result for:** {selected_learner_name}")
                    
                    # Test result submission form
                    with st.form("test_result_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            test_id = st.text_input("Test ID *", placeholder="e.g., quiz_001, test_midterm")
                            test_type = st.selectbox("Test Type *", ["", "quiz", "test", "assignment", "exam"])
                            course_id = st.text_input("Course ID *", placeholder="e.g., python-101, math-201")
                        
                        with col2:
                            score = st.number_input("Score Achieved *", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                            max_score = st.number_input("Maximum Possible Score", min_value=1.0, max_value=1000.0, value=100.0, step=1.0)
                            time_taken = st.number_input("Time Taken (minutes)", min_value=0.0, value=0.0, step=0.5)
                        
                        content_id = st.text_input("Content ID (optional)", placeholder="Specific content identifier")
                        attempts = st.number_input("Number of Attempts", min_value=1, value=1, step=1)
                        
                        submitted = st.form_submit_button("📝 Submit Test Result", type="primary")
                    
                    # Form submission handling
                    if submitted:
                        if not all([test_id.strip(), test_type, course_id.strip()]):
                            st.error("[FAIL] Please fill in all required fields")
                        else:
                            with st.spinner("Submitting test result..."):
                                try:
                                    # Create TestResult object
                                    test_result = TestResult(
                                        learner_id=str(learner_id),
                                        test_id=test_id.strip(),
                                        test_type=test_type,
                                        course_id=course_id.strip(),
                                        content_id=content_id.strip() if content_id.strip() else None,
                                        score=float(score),
                                        max_score=float(max_score),
                                        time_taken=float(time_taken) if time_taken > 0 else None,
                                        attempts=int(attempts)
                                    )
                                    
                                    # Create engagement record
                                    engagement_data = {
                                        'learner_id': str(learner_id),
                                        'content_id': content_id.strip() if content_id.strip() else test_id.strip(),
                                        'course_id': course_id.strip(),
                                        'engagement_type': f"{test_type}_attempt",
                                        'duration': float(time_taken) if time_taken > 0 else 0,
                                        'score': test_result.percentage,
                                        'feedback': f"Test result: {score}/{max_score}",
                                        'metadata': {
                                            'test_id': test_id.strip(),
                                            'test_type': test_type,
                                            'max_score': float(max_score),
                                            'attempts': int(attempts)
                                        }
                                    }
                                    
                                    # Create engagement
                                    engagement = Engagement(**engagement_data)
                                    result = create_engagement(engagement)
                                    
                                    if result:
                                        st.success(f"[OK] Test result submitted successfully!")
                                        st.info(f"**Test ID:** {test_id.strip()}")
                                        st.info(f"**Score:** {test_result.percentage:.1f}% ({score}/{max_score})")
                                        st.info(f"**Test Type:** {test_type.title()}")
                                        
                                        # Show next steps
                                        st.info("[TIP] **Next Steps:**")
                                        st.write("1. View 'Score Analytics' to see the updated scoring analysis")
                                        st.write("2. Get 'Score-Based Recommendations' for personalized course suggestions")
                                        st.write("3. Generate a 'Learning Path' based on your performance")
                                        
                                        # Display result summary
                                        with st.expander("View Submitted Test Result"):
                                            st.json({
                                                "learner_id": str(learner_id),
                                                "test_id": test_id.strip(),
                                                "test_type": test_type,
                                                "course_id": course_id.strip(),
                                                "score": float(score),
                                                "max_score": float(max_score),
                                                "percentage": test_result.percentage,
                                                "time_taken": float(time_taken) if time_taken > 0 else None,
                                                "attempts": int(attempts),
                                                "passed": test_result.passed
                                            })
                                    else:
                                        st.error("[FAIL] Failed to submit test result")
                                        
                                except Exception as e:
                                    st.error(f"[FAIL] Error submitting test result: {str(e)}")
                    
                    # Display recent test results for this learner
                    st.subheader("[NOTE] Recent Test Results")
                    try:
                        from utils.crud_operations import read_engagements
                        engagements = read_engagements()
                        learner_engagements = [
                            e for e in engagements 
                            if e.get('learner_id') == str(learner_id) 
                            and any(test_type in e.get('engagement_type', '') for test_type in ['quiz', 'test', 'assignment', 'exam'])
                        ]
                        
                        if learner_engagements:
                            # Show recent 5 test results
                            recent_tests = sorted(learner_engagements, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
                            
                            for engagement in recent_tests:
                                test_type_display = engagement.get('engagement_type', 'unknown').replace('_attempt', '').title()
                                score = engagement.get('score', 0)
                                st.write(f"• **{test_type_display}** in {engagement.get('course_id', 'Unknown Course')}: {score:.1f}%")
                        else:
                            st.info("No test results found for this learner yet.")
                    except Exception as e:
                        st.warning(f"Could not load recent test results: {str(e)}")
                
                else:
                    st.info("Select a learner to submit test results.")
                    
        except Exception as e:
            st.error(f"Error in test result submission: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🎓 Learning Agent - Enhanced Scoring & Recommendations | Powered by Advanced Analytics 🤖"
    "</div>", 
    unsafe_allow_html=True
)
