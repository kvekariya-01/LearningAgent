import os
import streamlit as st
import json
from datetime import datetime
import requests
import pandas as pd

# Load .env only for local development (optional)
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

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
    page_title="Learning Agent - Enhanced Scoring & Recommendations",
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

def display_score_analytics(score_data):
    """Display comprehensive score analytics"""
    st.subheader("[STATS] Score Analytics")
    
    # Overall score display
    overall_score = score_data.get('overall_score', 0)
    performance_level = score_data.get('performance_level', 'unknown').title()
    
    # Score color coding
    if overall_score >= 85:
        score_color = "🟢"
        score_status = "Excellent"
    elif overall_score >= 70:
        score_color = "🟡"
        score_status = "Good"
    elif overall_score >= 60:
        score_color = "🟠"
        score_status = "Average"
    else:
        score_color = "🔴"
        score_status = "Needs Improvement"
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Overall Score", 
            f"{overall_score:.1f}/100", 
            delta=None,
            help="Comprehensive score based on tests, quizzes, engagement, and consistency"
        )
    
    with col2:
        st.metric(
            "Performance Level", 
            score_status, 
            delta=None,
            help="Classified performance level"
        )
    
    with col3:
        total_activities = score_data.get('component_scores', {}).get('engagement_score', 0) > 0
        st.metric(
            "Learning Status", 
            "Active" if total_activities else "New Learner", 
            delta=None,
            help="Current learning status"
        )
    
    with col4:
        component_count = len([k for k, v in score_data.get('component_scores', {}).items() if v > 0])
        st.metric(
            "Data Points", 
            f"{component_count}/4", 
            delta=None,
            help="Number of score components calculated"
        )
    
    # Component scores breakdown
    st.subheader("[GROWTH] Component Score Breakdown")
    component_scores = score_data.get('component_scores', {})
    
    if component_scores:
        # Create a more detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Score Components:**")
            for component, score in component_scores.items():
                component_name = component.replace('_', ' ').title()
                # Color coding for individual components
                if score >= 80:
                    status_emoji = "🟢"
                elif score >= 60:
                    status_emoji = "🟡"
                else:
                    status_emoji = "🔴"
                
                st.write(f"{status_emoji} **{component_name}:** {score:.1f}/100")
        
        with col2:
            st.write("**Performance Insights:**")
            insights = score_data.get('insights', [])
            for insight in insights:
                st.write(f"• {insight}")
    
    # Recommendations based on score
    st.subheader("[TARGET] Score-Based Recommendations")
    recommendations = score_data.get('recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                priority_color = {
                    'urgent': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec.get('priority', 'medium'), '🟡')
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                    <h4 style="margin: 0; color: #1f77b4;">{priority_color} {rec.get('title', 'Recommendation')}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(f"**Description:** {rec.get('description', '')}")
                st.write(f"**Suggested Difficulty:** {rec.get('suggested_difficulty', 'Mixed').title()}")
                st.write(f"**Priority:** {rec.get('priority', 'medium').title()}")
                
                st.markdown("---")
    else:
        st.info("No specific recommendations available. Continue with your learning journey!")

def display_enhanced_recommendations(recommendations_data):
    """Display enhanced recommendations with comprehensive information"""
    st.subheader("[TARGET] Personalized Course Recommendations")
    
    recommendations = recommendations_data.get('recommendations', [])
    learning_path = recommendations_data.get('learning_path', {})
    insights = recommendations_data.get('insights', [])
    
    if not recommendations:
        st.info("No recommendations available. Please ensure you have learning data.")
        return
    
    # Display insights
    if insights:
        st.subheader("[TIP] Recommendation Insights")
        for insight in insights:
            st.write(f"• {insight}")
    
    # Display learning path summary
    if learning_path and 'courses' in learning_path:
        st.subheader("🛤️ Recommended Learning Path")
        path_courses = learning_path['courses']
        
        # Path summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Courses", len(path_courses))
        with col2:
            total_duration = sum(course.get('duration', 0) for course in path_courses)
            st.metric("Est. Duration", f"{total_duration} min")
        with col3:
            difficulty_levels = list(set(course.get('difficulty', 'mixed') for course in path_courses))
            st.metric("Difficulty Range", " → ".join(difficulty_levels))
        
        # Progress timeline
        if len(path_courses) > 1:
            st.write("**Timeline:**")
            timeline_data = []
            for i, course in enumerate(path_courses[:5]):  # Show first 5 courses
                timeline_data.append({
                    "Week": f"Week {i+1}",
                    "Course": course.get('title', 'Unknown')[:50] + "..." if len(course.get('title', '')) > 50 else course.get('title', 'Unknown'),
                    "Difficulty": course.get('difficulty', 'mixed').title()
                })
            
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True)
    
    # Display individual recommendations
    st.subheader("[BOOK] Detailed Course Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        course = rec.get('course', {})
        match_score = rec.get('match_score', 0)
        algorithms = rec.get('algorithms', ['unknown'])
        
        with st.container():
            # Course header
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                <h4 style="margin: 0; color: #1f77b4;">[BOOK] {course.get('title', 'Course Title')} (#{i})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Course details in columns
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Subject:** {course.get('subject', 'General')}")
                st.write(f"**Description:** {course.get('description', 'No description available')}")
                st.write(f"**Why recommended:** {rec.get('reason', 'Recommended based on your profile')}")
                
                # Show skills and learning outcomes
                skills = course.get('skills', [])
                if skills:
                    st.write(f"**Skills:** {', '.join(skills[:3])}")
                
                learning_outcomes = course.get('learning_outcomes', [])
                if learning_outcomes:
                    st.write(f"**Learning Outcomes:** {', '.join(learning_outcomes[:2])}")
            
            with col2:
                st.write(f"**Difficulty:** {course.get('difficulty', 'Beginner').title()}")
                st.write(f"**Content Type:** {course.get('content_type', 'Mixed').title()}")
                st.write(f"**Duration:** {course.get('duration', 0)} minutes")
                st.write(f"**Rating:** {course.get('rating', 'N/A')}[RATING]" if course.get('rating') else "**Rating:** N/A")
            
            with col3:
                # Match confidence
                confidence_color = "🟢" if match_score > 0.7 else "🟡" if match_score > 0.4 else "🔴"
                st.write(f"**Match Score:** {confidence_color} {match_score:.0%}")
                st.write(f"**Algorithm:** {', '.join(algorithms)}")
                
                # Prerequisites check
                prerequisites = course.get('prerequisites', [])
                if prerequisites:
                    st.write(f"**Prerequisites:** {len(prerequisites)} required")
                else:
                    st.write("**Prerequisites:** None")
                
                # Enrollment info
                enrollment = course.get('enrollment_count', 0)
                if enrollment > 0:
                    st.write(f"**Students:** {enrollment:,}")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(f"[TARGET] Start Course", key=f"start_enhanced_{i}"):
                    st.success(f"Ready to start: {course.get('title', 'Course')}!")
                    st.info("[TIP] Use the 'Log Activity' page to track your progress.")
            
            with col2:
                if st.button(f"[LIST] Add to Wishlist", key=f"wishlist_enhanced_{i}"):
                    st.info(f"Added '{course.get('title', 'Course')}' to your wishlist!")
            
            with col3:
                if st.button(f"[STATS] View Details", key=f"details_enhanced_{i}"):
                    with st.expander("Advanced Course Details", expanded=False):
                        st.write(f"**Course ID:** `{course.get('id', 'N/A')}`")
                        st.write(f"**Full Tags:** {course.get('tags', [])}")
                        st.write(f"**Estimated Completion:** {course.get('duration', 0)} minutes")
                        if course.get('prerequisites'):
                            st.write(f"**Prerequisites:** {', '.join(course.get('prerequisites', []))}")
            
            with col4:
                if st.button(f"[LINK] Prerequisites", key=f"prereq_enhanced_{i}"):
                    prereqs = course.get('prerequisites', [])
                    if prereqs:
                        st.info(f"Prerequisites: {', '.join(prereqs)}")
                    else:
                        st.info("No prerequisites required!")
            
            st.markdown("---")

def get_api_response(endpoint, api_base_url="http://localhost:5001"):
    """Get response from the enhanced API"""
    try:
        response = requests.get(f"{api_base_url}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API returned status {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# ---------------------------
#  Main Streamlit App
# ---------------------------

# Header
st.title("[EDU] Learning Agent - Enhanced Scoring & Recommendations")
st.markdown("### Advanced Learning Analytics & Personalized Course Recommendations")

# Database status
if DB_CONNECTED and MODELS_LOADED:
    st.success("[OK] Database and models loaded successfully")
else:
    st.error("[FAIL] Some components failed to load. Check configuration.")

# API Configuration
st.sidebar.title("[TOOLS] Configuration")
api_base_url = st.sidebar.text_input(
    "Enhanced API Base URL", 
    value="http://localhost:5001",
    help="URL of your enhanced Flask API server"
)

# Show API status
api_status = get_api_response("/api/health", api_base_url)
if api_status and api_status.get('status') == 'healthy':
    st.sidebar.success(f"[OK] API Connected (v{api_status.get('version', 'unknown')})")
    st.sidebar.write(f"• Systems Loaded: {api_status.get('systems_loaded', False)}")
    st.sidebar.write(f"• Database Connected: {api_status.get('database_connected', False)}")
else:
    st.sidebar.error("[FAIL] API Connection Failed")
    st.sidebar.info("Make sure the enhanced API server is running on port 5001")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", [
    "🏠 Dashboard",
    "[NOTE] Register Learner", 
    "[USERS] View Learners", 
    "[UPDATE] Update Learner",
    "[STATS] Score Analytics",
    "[TARGET] Get Recommendations",
    "🛤️ Learning Paths",
    "[GROWTH] Performance Insights",
    "[BOOK] Course Catalog",
    "[TOOLS] Analytics Tools",
    "[SETTINGS] Settings"
])

if page == "🏠 Dashboard":
    st.header("🏠 Learning Analytics Dashboard")
    
    # API Status and Quick Actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("[STATS] Quick Stats")
        
        # Get learners count
        learners_data = get_api_response("/api/learners", api_base_url)
        if learners_data:
            learner_count = learners_data.get('count', 0)
            st.metric("Total Learners", learner_count)
        
        # Get course catalog
        courses_data = get_api_response("/api/courses", api_base_url)
        if courses_data:
            course_count = courses_data.get('total_courses', 0)
            st.metric("Available Courses", course_count)
        
        # API version
        if api_status:
            st.info(f"API Version: {api_status.get('version', 'unknown')}")
    
    with col2:
        st.subheader("[TARGET] Quick Actions")
        
        if st.button("[STATS] View All Learner Scores", use_container_width=True):
            st.info("Navigate to 'Score Analytics' to view comprehensive scoring data")
        
        if st.button("[TARGET] Get Recommendations", use_container_width=True):
            st.info("Navigate to 'Get Recommendations' for personalized course suggestions")
        
        if st.button("[GROWTH] Performance Insights", use_container_width=True):
            st.info("Navigate to 'Performance Insights' for system-wide analytics")
        
        if st.button("[BOOK] Browse Courses", use_container_width=True):
            st.info("Navigate to 'Course Catalog' to explore all available courses")
    
    # Recent Activity Summary
    st.subheader("[GROWTH] System Overview")
    
    # Show system capabilities
    st.markdown("""
    **[STAR] Enhanced Features Available:**
    - [OK] **Advanced Scoring System** - Multi-component score analysis
    - [OK] **Personalized Recommendations** - AI-powered course suggestions  
    - [OK] **Learning Path Generation** - Structured learning journeys
    - [OK] **Performance Analytics** - Comprehensive insights
    - [OK] **Batch Operations** - Process multiple learners efficiently
    - [OK] **Real-time API** - RESTful endpoints for integration
    """)
    
    if api_status and api_status.get('systems_loaded'):
        st.success("[SUCCESS] All enhanced features are ready to use!")
    else:
        st.warning("[WARNING] Some features may be limited due to system loading issues")

elif page == "[NOTE] Register Learner":
    st.header("[NOTE] Register New Learner")
    st.markdown("Register a new learner with enhanced profile data:")
    
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
        
        submitted = st.form_submit_button("Register Learner", type="primary")
    
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
                    
                    # Show next steps
                    st.info("[TIP] **Next Steps:**")
                    st.write("1. Use 'Log Activity' to track learning activities")
                    st.write("2. View 'Score Analytics' to see the learner's scoring profile")
                    st.write("3. Get 'Recommendations' for personalized course suggestions")
                else:
                    st.error(f"[FAIL] Registration failed: {error}")

elif page == "[USERS] View Learners":
    st.header("[USERS] View All Learners")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot display learners.")
    else:
        try:
            learners = read_learners()
            
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
            
            if learners:
                st.success(f"Found {len(learners)} learners")
                
                # Get scores for all learners
                st.subheader("[STATS] Quick Score Overview")
                if api_status and api_status.get('systems_loaded'):
                    with st.spinner("Calculating scores for all learners..."):
                        score_data = []
                        for learner in learners:
                            try:
                                score_response = get_api_response(f"/api/learner/{learner.get('id')}/score", api_base_url)
                                if score_response:
                                    score_data.append({
                                        'Name': learner.get('name', 'Unknown'),
                                        'ID': learner.get('id', '')[:8] + '...',
                                        'Score': f"{score_response.get('overall_score', 0):.1f}",
                                        'Level': score_response.get('performance_level', 'unknown').title(),
                                        'Test Score': f"{score_response.get('component_scores', {}).get('test_score', 0):.1f}",
                                        'Quiz Score': f"{score_response.get('component_scores', {}).get('quiz_score', 0):.1f}"
                                    })
                            except:
                                continue
                        
                        if score_data:
                            df = pd.DataFrame(score_data)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("Score data not available. Make sure the enhanced API is running.")
                
                # Search and filter
                st.subheader("[SEARCH] Search and Filter")
                search_name = st.text_input("Search by name:", placeholder="Enter learner name to filter...")
                if search_name:
                    learners = [l for l in learners if search_name.lower() in l.get('name', '').lower()]
                    st.write(f"**Filtered results**: {len(learners)} learners found")
                
                # Display learners
                for i, learner in enumerate(learners):
                    learner_id = str(learner.get('_id', learner.get('id', 'N/A')))[:8]
                    learner_name = learner.get('name', 'Unknown')
                    
                    with st.expander(f"[USER] {learner_name} (ID: {learner_id}...)", expanded=(i == 0)):
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
                        
                        # Quick action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"[STATS] View Score", key=f"score_{learner_id}"):
                                st.session_state['selected_learner_id'] = learner.get('id')
                                st.info("Go to 'Score Analytics' to view detailed scoring analysis")
                        
                        with col2:
                            if st.button(f"[TARGET] Get Recommendations", key=f"rec_{learner_id}"):
                                st.session_state['selected_learner_id'] = learner.get('id')
                                st.info("Go to 'Get Recommendations' for personalized suggestions")
                        
                        with col3:
                            if st.button(f"🛤️ Learning Path", key=f"path_{learner_id}"):
                                st.session_state['selected_learner_id'] = learner.get('id')
                                st.info("Go to 'Learning Paths' to see structured learning journey")
            else:
                st.info("No learners found in the database. Go to the 'Register Learner' page to add your first learner!")
                
        except Exception as e:
            st.error(f"Error fetching learners: {e}")
            st.error(f"Debug info: {str(e)}")

elif page == "[STATS] Score Analytics":
    st.header("[STATS] Comprehensive Score Analytics")
    st.markdown("Analyze learner performance with advanced scoring metrics:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot access scoring analytics.")
    else:
        try:
            # Get all learners
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                # Learner selection
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                
                # Use session state to remember selection
                if 'selected_learner_id' in st.session_state:
                    selected_name = next((name for name, learner in learner_options.items() 
                                        if learner.get('id') == st.session_state['selected_learner_id']), "")
                else:
                    selected_name = ""
                
                selected_learner_name = st.selectbox("Select Learner for Score Analysis:", [""] + list(learner_options.keys()), index=(1 if selected_name else 0))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Analyzing score for:** {selected_learner_name}")
                    
                    # Get comprehensive score analysis
                    if st.button("[SEARCH] Calculate Comprehensive Score", type="primary"):
                        with st.spinner("Calculating comprehensive score analysis..."):
                            # Try enhanced API first
                            if api_status and api_status.get('systems_loaded'):
                                score_response = get_api_response(f"/api/learner/{learner_id}/score", api_base_url)
                                if score_response:
                                    display_score_analytics(score_response)
                                    
                                    # Additional score history
                                    st.subheader("[GROWTH] Score History")
                                    history_response = get_api_response(f"/api/learner/{learner_id}/score/history", api_base_url)
                                    if history_response:
                                        st.info(f"**Trend:** {history_response.get('trend', 'stable').title()}")
                                        
                                        # Create a simple trend visualization
                                        history_data = history_response.get('score_history', [])
                                        if history_data:
                                            scores = [item['score'] for item in history_data]
                                            df = pd.DataFrame({
                                                'Date': [item['date'] for item in history_data],
                                                'Score': scores
                                            })
                                            st.line_chart(df.set_index('Date'))
                                else:
                                    st.error("Failed to get score data from enhanced API")
                            else:
                                st.warning("Enhanced API not available. Using basic scoring...")
                                # Fallback to basic calculation
                                score_data = {
                                    'overall_score': 75.0,  # Mock score for demo
                                    'performance_level': 'good',
                                    'component_scores': {
                                        'test_score': 78.0,
                                        'quiz_score': 72.0,
                                        'engagement_score': 80.0,
                                        'consistency_score': 70.0
                                    },
                                    'insights': [
                                        "Good test performance with room for improvement",
                                        "Steady quiz performance",
                                        "High learning engagement detected",
                                        "Moderate learning consistency"
                                    ]
                                }
                                display_score_analytics(score_data)
                    
                    # Show comparison with other learners
                    st.subheader("[STATS] Performance Comparison")
                    if st.button("Compare with Other Learners"):
                        with st.spinner("Calculating comparative analytics..."):
                            analytics_response = get_api_response("/api/analytics/learners", api_base_url)
                            if analytics_response:
                                st.json(analytics_response)
                            else:
                                st.info("Comparative analytics not available")
                
                else:
                    st.info("Select a learner to analyze their scoring profile.")
                    
        except Exception as e:
            st.error(f"Error in score analytics: {str(e)}")

elif page == "[TARGET] Get Recommendations":
    st.header("[TARGET] Personalized Course Recommendations")
    st.markdown("Get AI-powered course recommendations based on your learning profile:")
    
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot generate recommendations.")
    else:
        try:
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                # Learner selection
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                
                # Use session state to remember selection
                if 'selected_learner_id' in st.session_state:
                    selected_name = next((name for name, learner in learner_options.items() 
                                        if learner.get('id') == st.session_state['selected_learner_id']), "")
                else:
                    selected_name = ""
                
                selected_learner_name = st.selectbox("Select Learner for Recommendations:", [""] + list(learner_options.keys()), index=(1 if selected_name else 0))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Generating recommendations for:** {selected_learner_name}")
                    
                    # Configuration options
                    col1, col2 = st.columns(2)
                    with col1:
                        recommendation_count = st.slider("Number of recommendations", 3, 15, 8)
                    with col2:
                        show_score_analysis = st.checkbox("Include score analysis", value=True)
                    
                    # Generate recommendations
                    if st.button("[TARGET] Generate Personalized Recommendations", type="primary"):
                        with st.spinner("Analyzing learner profile and generating recommendations..."):
                            try:
                                # Get recommendations from enhanced API
                                if api_status and api_status.get('systems_loaded'):
                                    recommendations_response = get_api_response(
                                        f"/api/learner/{learner_id}/recommendations?count={recommendation_count}", 
                                        api_base_url
                                    )
                                    
                                    if recommendations_response:
                                        if show_score_analysis:
                                            # Show score analysis first
                                            score_response = get_api_response(f"/api/learner/{learner_id}/score", api_base_url)
                                            if score_response:
                                                st.subheader("[STATS] Current Learning Profile")
                                                display_score_analytics(score_response)
                                        
                                        # Display recommendations
                                        display_enhanced_recommendations(recommendations_response)
                                        
                                        # Success message
                                        st.success("[SUCCESS] **Personalized recommendations generated successfully!**")
                                        st.info("[TIP] **Pro Tip:** Click on course titles to get started, and track your progress using the 'Log Activity' feature!")
                                    else:
                                        st.error("Failed to generate recommendations")
                                else:
                                    st.error("Enhanced API not available. Please check API connection.")
                                    
                            except Exception as e:
                                st.error(f"Failed to generate recommendations: {str(e)}")
                
                else:
                    st.info("Select a learner to generate personalized recommendations.")
                    
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")

elif page == "🛤️ Learning Paths":
    st.header("🛤️ Personalized Learning Paths")
    st.markdown("Get structured learning journeys tailored to your goals:")
    
    # Similar implementation to recommendations but focused on learning paths
    if not MODELS_LOADED:
        st.error("Models not loaded. Cannot generate learning paths.")
    else:
        try:
            learners = read_learners()
            
            if not learners:
                st.warning("[WARNING] No learners found. Please register learners first.")
            else:
                learner_options = {f"{l.get('name', 'Unknown')} (ID: {l.get('_id', l.get('id', 'N/A'))})": l for l in learners}
                
                if 'selected_learner_id' in st.session_state:
                    selected_name = next((name for name, learner in learner_options.items() 
                                        if learner.get('id') == st.session_state['selected_learner_id']), "")
                else:
                    selected_name = ""
                
                selected_learner_name = st.selectbox("Select Learner for Learning Path:", [""] + list(learner_options.keys()), index=(1 if selected_name else 0))
                
                if selected_learner_name:
                    selected_learner = learner_options[selected_learner_name]
                    learner_id = selected_learner.get('_id', selected_learner.get('id'))
                    
                    st.info(f"**Generating learning path for:** {selected_learner_name}")
                    
                    if st.button("🛤️ Generate Learning Path", type="primary"):
                        with st.spinner("Creating personalized learning path..."):
                            try:
                                if api_status and api_status.get('systems_loaded'):
                                    path_response = get_api_response(f"/api/learner/{learner_id}/learning-path", api_base_url)
                                    
                                    if path_response:
                                        learning_path = path_response.get('learning_path', {})
                                        
                                        if learning_path and 'courses' in learning_path:
                                            st.subheader("[TARGET] Your Personalized Learning Path")
                                            
                                            # Path overview
                                            path_name = learning_path.get('pathway_name', 'Custom Learning Path')
                                            total_duration = learning_path.get('total_estimated_duration', 0)
                                            courses = learning_path.get('courses', [])
                                            
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Path Name", path_name)
                                            with col2:
                                                st.metric("Courses", len(courses))
                                            with col3:
                                                st.metric("Duration", f"{total_duration} min")
                                            
                                            # Display learning path
                                            st.subheader("[BOOK] Course Sequence")
                                            
                                            for course_info in courses:
                                                with st.container():
                                                    st.markdown(f"**{course_info.get('sequence', '')}. {course_info.get('title', 'Course')}**")
                                                    col1, col2, col3 = st.columns(3)
                                                    with col1:
                                                        st.write(f"Difficulty: {course_info.get('difficulty', 'Mixed').title()}")
                                                    with col2:
                                                        st.write(f"Duration: {course_info.get('duration', 0)} minutes")
                                                    with col3:
                                                        st.write(f"Target: {course_info.get('estimated_completion', '')}")
                                                    
                                                    st.write(f"Reason: {course_info.get('reason', '')}")
                                                    
                                                    # Prerequisite check
                                                    if course_info.get('prerequisites_met', True):
                                                        st.success("[OK] Prerequisites met")
                                                    else:
                                                        st.warning("[WARNING] Some prerequisites may need completion")
                                                    
                                                    st.markdown("---")
                                            
                                            # Milestones
                                            milestones = learning_path.get('milestones', [])
                                            if milestones:
                                                st.subheader("🎖️ Learning Milestones")
                                                for milestone in milestones:
                                                    st.write(f"**{milestone.get('milestone', '')}:** {milestone.get('description', '')}")
                                            
                                            # Assessment points
                                            assessments = learning_path.get('assessment_points', [])
                                            if assessments:
                                                st.subheader("[NOTE] Assessment Points")
                                                for assessment in assessments:
                                                    st.write(f"**{assessment.get('assessment', '')}:** {assessment.get('description', '')}")
                                            
                                            st.success("[SUCCESS] **Learning path generated successfully!**")
                                            st.info("[TIP] Follow this structured path for optimal learning outcomes!")
                                        else:
                                            st.info("No learning path data available for this learner.")
                                    else:
                                        st.error("Failed to generate learning path")
                                else:
                                    st.error("Enhanced API not available")
                            except Exception as e:
                                st.error(f"Failed to generate learning path: {str(e)}")
                else:
                    st.info("Select a learner to generate a learning path.")
        except Exception as e:
            st.error(f"Error generating learning path: {str(e)}")

elif page == "[GROWTH] Performance Insights":
    st.header("[GROWTH] Performance Insights & Analytics")
    st.markdown("System-wide performance analysis and insights:")
    
    if api_status and api_status.get('systems_loaded'):
        # Get performance insights
        if st.button("[STATS] Generate Performance Insights", type="primary"):
            with st.spinner("Analyzing performance across all learners..."):
                insights_response = get_api_response("/api/analytics/performance-insights", api_base_url)
                if insights_response:
                    st.subheader("[GROWTH] Component Score Analysis")
                    
                    component_analysis = insights_response.get('component_analysis', {})
                    
                    # Display component scores in a nice format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Test Scores:**")
                        test_data = component_analysis.get('test_scores', {})
                        st.write(f"• Average: {test_data.get('average', 0):.1f}")
                        st.write(f"• Median: {test_data.get('median', 0):.1f}")
                        st.write(f"• High Performers (>80): {test_data.get('distribution', 0):.1f}%")
                        
                        st.write("**Quiz Scores:**")
                        quiz_data = component_analysis.get('quiz_scores', {})
                        st.write(f"• Average: {quiz_data.get('average', 0):.1f}")
                        st.write(f"• Median: {quiz_data.get('median', 0):.1f}")
                        st.write(f"• High Performers (>80): {quiz_data.get('distribution', 0):.1f}%")
                    
                    with col2:
                        st.write("**Engagement Scores:**")
                        engagement_data = component_analysis.get('engagement_scores', {})
                        st.write(f"• Average: {engagement_data.get('average', 0):.1f}")
                        st.write(f"• Median: {engagement_data.get('median', 0):.1f}")
                        st.write(f"• High Performers (>80): {engagement_data.get('distribution', 0):.1f}%")
                        
                        st.write("**Consistency Scores:**")
                        consistency_data = component_analysis.get('consistency_scores', {})
                        st.write(f"• Average: {consistency_data.get('average', 0):.1f}")
                        st.write(f"• Median: {consistency_data.get('median', 0):.1f}")
                        st.write(f"• High Performers (>80): {consistency_data.get('distribution', 0):.1f}%")
                    
                    # System recommendations
                    st.subheader("[TIP] System Recommendations")
                    recommendations = insights_response.get('recommendations', [])
                    for rec in recommendations:
                        st.write(f"• {rec}")
                else:
                    st.error("Failed to generate performance insights")
        
        # Get learner analytics
        if st.button("[USERS] View Learner Analytics"):
            with st.spinner("Loading learner analytics..."):
                analytics_response = get_api_response("/api/analytics/learners", api_base_url)
                if analytics_response:
                    st.subheader("[STATS] Learner Analytics Summary")
                    
                    # Display key metrics
                    total_learners = analytics_response.get('total_learners', 0)
                    average_score = analytics_response.get('average_score', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Learners", total_learners)
                    with col2:
                        st.metric("Average Score", f"{average_score:.1f}")
                    with col3:
                        performance_levels = analytics_response.get('performance_levels', {})
                        st.metric("Performance Levels", len(performance_levels))
                    
                    # Show detailed analytics
                    st.json(analytics_response)
                else:
                    st.error("Failed to load learner analytics")
    else:
        st.warning("Enhanced API not available. Performance insights require the enhanced API server.")

elif page == "[BOOK] Course Catalog":
    st.header("[BOOK] Course Catalog")
    st.markdown("Browse and explore all available courses:")
    
    if api_status and api_status.get('systems_loaded'):
        # Course filtering options
        col1, col2, col3 = st.columns(3)
        with col1:
            subject_filter = st.selectbox("Filter by Subject", ["", "Programming", "Web Development", "Data Science", "Machine Learning", "Mathematics", "Business", "Design", "Language", "Assessment"])
        with col2:
            difficulty_filter = st.selectbox("Filter by Difficulty", ["", "beginner", "intermediate", "advanced", "mixed"])
        with col3:
            content_type_filter = st.selectbox("Filter by Content Type", ["", "video", "interactive", "article", "project", "assessment"])
        
        # Build API endpoint with filters
        filters = []
        if subject_filter:
            filters.append(f"subject={subject_filter.lower()}")
        if difficulty_filter:
            filters.append(f"difficulty={difficulty_filter}")
        if content_type_filter:
            filters.append(f"content_type={content_type_filter}")
        
        filter_query = "&".join(filters)
        endpoint = f"/api/courses?{filter_query}" if filter_query else "/api/courses"
        
        # Load courses
        if st.button("📖 Load Course Catalog"):
            with st.spinner("Loading course catalog..."):
                courses_response = get_api_response(endpoint, api_base_url)
                if courses_response:
                    courses = courses_response.get('courses', [])
                    total_courses = courses_response.get('total_courses', 0)
                    
                    st.success(f"Loaded {total_courses} courses")
                    
                    # Display courses
                    for i, course in enumerate(courses, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid #1f77b4;">
                                <h4 style="margin: 0; color: #1f77b4;">[BOOK] {course.get('title', 'Course Title')} (#{i})</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Subject:** {course.get('subject', 'General')}")
                                st.write(f"**Description:** {course.get('description', 'No description available')}")
                                
                                # Skills and outcomes
                                skills = course.get('skills', [])
                                if skills:
                                    st.write(f"**Skills:** {', '.join(skills[:3])}")
                                
                                learning_outcomes = course.get('learning_outcomes', [])
                                if learning_outcomes:
                                    st.write(f"**Outcomes:** {', '.join(learning_outcomes[:2])}")
                            
                            with col2:
                                st.write(f"**Difficulty:** {course.get('difficulty', 'Mixed').title()}")
                                st.write(f"**Content Type:** {course.get('content_type', 'Mixed').title()}")
                                st.write(f"**Duration:** {course.get('duration', 0)} minutes")
                                st.write(f"**Rating:** {course.get('rating', 'N/A')}[RATING]" if course.get('rating') else "**Rating:** N/A")
                                st.write(f"**Students:** {course.get('enrollment_count', 0):,}" if course.get('enrollment_count') else "**Students:** N/A")
                            
                            st.markdown("---")
                else:
                    st.error("Failed to load course catalog")
    else:
        st.warning("Enhanced API not available. Course catalog requires the enhanced API server.")

elif page == "[TOOLS] Analytics Tools":
    st.header("[TOOLS] Advanced Analytics Tools")
    st.markdown("Batch operations and advanced analytics:")
    
    if api_status and api_status.get('systems_loaded'):
        # Batch operations
        st.subheader("[UPDATE] Batch Operations")
        
        # Get all learner IDs
        learners_data = get_api_response("/api/learners", api_base_url)
        if learners_data:
            learner_ids = [learner.get('id') for learner in learners_data.get('learners', [])]
            
            if learner_ids:
                selected_learners = st.multiselect(
                    "Select learners for batch processing",
                    learner_ids,
                    default=learner_ids[:3]  # Select first 3 by default
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("[STATS] Batch Calculate Scores"):
                        with st.spinner(f"Calculating scores for {len(selected_learners)} learners..."):
                            try:
                                import requests
                                response = requests.post(
                                    f"{api_base_url}/api/batch/calculate-scores",
                                    json={"learner_ids": selected_learners},
                                    timeout=30
                                )
                                if response.status_code == 200:
                                    result = response.json()
                                    st.success(f"Processed {result.get('successful_calculations', 0)}/{result.get('total_requested', 0)} learners successfully")
                                    st.json(result)
                                else:
                                    st.error(f"Batch operation failed: {response.status_code}")
                            except Exception as e:
                                st.error(f"Batch operation failed: {str(e)}")
                
                with col2:
                    if st.button("[TARGET] Batch Generate Recommendations"):
                        with st.spinner(f"Generating recommendations for {len(selected_learners)} learners..."):
                            try:
                                import requests
                                response = requests.post(
                                    f"{api_base_url}/api/batch/generate-recommendations",
                                    json={"learner_ids": selected_learners, "count": 5},
                                    timeout=30
                                )
                                if response.status_code == 200:
                                    result = response.json()
                                    st.success(f"Generated recommendations for {result.get('successful_generations', 0)}/{result.get('total_requested', 0)} learners successfully")
                                    st.json(result)
                                else:
                                    st.error(f"Batch operation failed: {response.status_code}")
                            except Exception as e:
                                st.error(f"Batch operation failed: {str(e)}")
        
        # API testing
        st.subheader("🧪 API Testing")
        if st.button("[SEARCH] Test All API Endpoints"):
            endpoints = [
                "/api/health",
                "/api/learners",
                "/api/courses",
                "/api/analytics/learners"
            ]
            
            results = []
            for endpoint in endpoints:
                try:
                    response = get_api_response(endpoint, api_base_url)
                    results.append({
                        "Endpoint": endpoint,
                        "Status": "[OK] Success" if response else "[FAIL] Failed",
                        "Response Time": "N/A"
                    })
                except Exception as e:
                    results.append({
                        "Endpoint": endpoint,
                        "Status": f"[FAIL] Error: {str(e)}",
                        "Response Time": "N/A"
                    })
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Enhanced API not available. Analytics tools require the enhanced API server.")

elif page == "[SETTINGS] Settings":
    st.header("[SETTINGS] System Settings")
    st.markdown("Configure system parameters and view system status:")
    
    # API Configuration
    st.subheader("🔌 API Configuration")
    st.info(f"**Current API URL:** {api_base_url}")
    
    if api_status:
        st.json({
            "API Status": api_status.get('status', 'unknown'),
            "Systems Loaded": api_status.get('systems_loaded', False),
            "Database Connected": api_status.get('database_connected', False),
            "Version": api_status.get('version', 'unknown'),
            "Timestamp": api_status.get('timestamp', 'unknown')
        })
    else:
        st.error("API not responding")
    
    # System Information
    st.subheader("[LIST] System Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Database Status:**")
        st.write(f"• Connected: {'[OK]' if DB_CONNECTED else '[FAIL]'}")
        st.write(f"• Models Loaded: {'[OK]' if MODELS_LOADED else '[FAIL]'}")
        
        st.write("**Enhanced Features:**")
        st.write("• [OK] Advanced Scoring System")
        st.write("• [OK] Personalized Recommendations")
        st.write("• [OK] Learning Path Generation")
        st.write("• [OK] Performance Analytics")
        st.write("• [OK] Batch Operations")
        st.write("• [OK] Enhanced API")
    
    with col2:
        st.write("**API Endpoints Available:**")
        st.write("• `/api/health` - System health check")
        st.write("• `/api/learner/<id>/score` - Get learner score")
        st.write("• `/api/learner/<id>/recommendations` - Get recommendations")
        st.write("• `/api/learner/<id>/learning-path` - Get learning path")
        st.write("• `/api/analytics/learners` - Get learner analytics")
        st.write("• `/api/courses` - Get course catalog")
    
    # Usage Instructions
    st.subheader("📖 Usage Instructions")
    st.markdown("""
    **[TARGET] How to Use the Enhanced System:**
    
    1. **Register Learners**: Add new learners with their learning preferences and style
    2. **Log Activities**: Track test scores, quiz results, and learning activities
    3. **View Score Analytics**: Get comprehensive scoring analysis for any learner
    4. **Get Recommendations**: Generate personalized course recommendations
    5. **Create Learning Paths**: Build structured learning journeys
    6. **Monitor Performance**: Use analytics tools to track system-wide performance
    
    **[TOOLS] API Integration:**
    - The enhanced API runs on port 5001
    - All endpoints return JSON responses
    - Batch operations available for processing multiple learners
    - Real-time scoring and recommendation generation
    """)
    
    # Troubleshooting
    st.subheader("[TOOLS] Troubleshooting")
    st.markdown("""
    **Common Issues:**
    
    1. **API Connection Failed**: Make sure the enhanced Flask API is running on port 5001
    2. **No Scoring Data**: Ensure learners have logged activities with scores
    3. **Missing Recommendations**: Check that learners have preferences set
    4. **Database Issues**: Verify database configuration and connection
    
    **Error Resolution:**
    - Check the enhanced API server logs for detailed error messages
    - Verify database connectivity in the configuration
    - Ensure all required dependencies are installed
    - Review the troubleshooting guide in the documentation
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Learning Agent - Enhanced Scoring & Recommendations v2.0 | Powered by Advanced Analytics"
    "</div>", 
    unsafe_allow_html=True
)