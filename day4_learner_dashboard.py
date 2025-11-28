#!/usr/bin/env python3
"""
DAY 4 - Learner Dashboard
Dedicated interface for learners with learning path display, progress charts, 
recommended next modules, and performance metrics
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Learning Agent - Learner Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffe6e6;
        border-left: 4px solid #ff4d4d;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-low {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .progress-container {
        background-color: #e9ecef;
        border-radius: 1rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .progress-bar {
        background: linear-gradient(90deg, #28a745, #20c997);
        height: 20px;
        border-radius: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class APIManager:
    """Enhanced API manager with loading states and error handling"""
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None, timeout: int = 10):
        """Make API request with enhanced error handling"""
        url = f"{self.api_base_url}{endpoint}"
        try:
            with st.spinner(f"🔄 Connecting to {endpoint}..."):
                if method == 'GET':
                    response = self.session.get(url, timeout=timeout)
                elif method == 'POST':
                    response = self.session.post(url, json=data, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    st.error(f"🔍 Resource not found: {endpoint}")
                    return None
                elif response.status_code == 500:
                    st.error(f"💥 Server error: {response.text}")
                    return None
                else:
                    st.error(f"❌ API Error ({response.status_code}): {response.text}")
                    return None
                    
        except requests.exceptions.Timeout:
            st.error("⏰ Request timeout. The server is taking too long to respond.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Please check if the API server is running.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❓ Unexpected error: {str(e)}")
            return None
    
    def get_learner_data(self, learner_id: str):
        """Get learner profile and basic data"""
        return self._make_request(f"/api/learner/{learner_id}/profile")
    
    def get_learner_score(self, learner_id: str):
        """Get learner comprehensive score"""
        return self._make_request(f"/api/learner/{learner_id}/score")
    
    def get_recommendations(self, learner_id: str, count: int = 5):
        """Get personalized recommendations"""
        return self._make_request(f"/api/learner/{learner_id}/recommendations?count={count}")
    
    def get_learning_path(self, learner_id: str):
        """Get learning path"""
        return self._make_request(f"/api/learner/{learner_id}/learning-path")
    
    def get_score_history(self, learner_id: str):
        """Get score history for charts"""
        return self._make_request(f"/api/learner/{learner_id}/score/history")
    
    def log_activity(self, learner_id: str, activity_data: dict):
        """Log new activity"""
        return self._make_request(f"/api/learner/{learner_id}/activity", 'POST', activity_data)

def display_loading_state(message: str):
    """Display loading animation"""
    with st.spinner(f"⏳ {message}"):
        time.sleep(0.5)

def create_progress_chart(score_data: dict, history_data: dict = None):
    """Create interactive progress charts"""
    
    # Component scores for radar chart
    component_scores = score_data.get('component_scores', {})
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Score Breakdown', 'Performance Level', 'Score Trend', 'Weekly Activity'),
        specs=[[{"type": "polar"}, {"type": "indicator"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # Radar chart for component scores
    categories = ['Test Score', 'Quiz Score', 'Engagement', 'Consistency']
    values = [
        component_scores.get('test_score', 0),
        component_scores.get('quiz_score', 0),
        component_scores.get('engagement_score', 0),
        component_scores.get('consistency_score', 0)
    ]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Component Scores'
    ), row=1, col=1)
    
    # Performance level indicator
    overall_score = score_data.get('overall_score', 0)
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Score"},
        delta={'reference': 70},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 90], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ), row=1, col=2)
    
    # Score trend if history available
    if history_data and history_data.get('score_history'):
        history = history_data['score_history']
        dates = [item['date'] for item in history]
        scores = [item['score'] for item in history]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Score Trend',
            line=dict(color='blue', width=3)
        ), row=2, col=1)
    
    # Weekly activity chart (mock data for demo)
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    activities = [3, 5, 4, 6]
    
    fig.add_trace(go.Bar(
        x=weeks,
        y=activities,
        name='Activities',
        marker_color='lightblue'
    ), row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="📊 Comprehensive Learning Analytics",
        title_x=0.5
    )
    
    return fig

def display_learning_path(learning_path_data: dict):
    """Display learning path with progress tracking"""
    
    learning_path = learning_path_data.get('learning_path', {})
    if not learning_path or 'courses' not in learning_path:
        st.info("🛤️ No learning path available yet. Complete your profile to get personalized recommendations!")
        return
    
    courses = learning_path['courses']
    
    # Path overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Courses", len(courses))
    with col2:
        total_duration = sum(course.get('duration', 0) for course in courses)
        st.metric("⏱️ Est. Duration", f"{total_duration} min")
    with col3:
        st.metric("🎯 Completion Goal", "4-6 weeks")
    
    # Course sequence
    st.subheader("🛤️ Your Learning Journey")
    
    for i, course_info in enumerate(courses[:8]):  # Show first 8 courses
        with st.container():
            # Course header
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{i+1}. {course_info.get('title', 'Course Title')}**")
                st.write(f"📖 {course_info.get('description', 'No description available')}")
                
                # Progress indicator
                completed = course_info.get('completed', False)
                if completed:
                    st.success("✅ Completed")
                else:
                    st.info("⏳ Not started")
            
            with col2:
                difficulty = course_info.get('difficulty', 'beginner').title()
                st.write(f"**Difficulty:** {difficulty}")
                duration = course_info.get('duration', 0)
                st.write(f"**Duration:** {duration} min")
            
            with col3:
                if st.button(f"▶️ Start", key=f"start_{i}", disabled=completed):
                    st.success(f"Ready to start: {course_info.get('title', 'Course')}!")
            
            # Progress bar
            progress = course_info.get('progress', 0)
            if progress > 0:
                st.progress(progress / 100)
                st.write(f"Progress: {progress}%")
            
            st.markdown("---")

def display_recommendations(recommendations_data: dict, api_manager: APIManager, learner_id: str):
    """Display recommended next modules with enhanced UI"""
    
    recommendations = recommendations_data.get('recommendations', [])
    if not recommendations:
        st.info("📝 No recommendations available. Complete more activities to get personalized suggestions!")
        return
    
    st.subheader("🎯 Recommended Next Modules")
    
    for i, rec in enumerate(recommendations[:6]):
        course = rec.get('course', {})
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Course title with emoji based on subject
                subject_emoji = {
                    'Programming': '💻',
                    'Data Science': '📊', 
                    'Web Development': '🌐',
                    'Machine Learning': '🤖',
                    'Mathematics': '🔢',
                    'Design': '🎨',
                    'Business': '💼',
                    'Language': '🗣️'
                }
                emoji = subject_emoji.get(course.get('subject', ''), '📚')
                
                st.markdown(f"### {emoji} {course.get('title', 'Course Title')}")
                st.write(f"**Subject:** {course.get('subject', 'General')}")
                st.write(f"**Why recommended:** {rec.get('reason', 'Based on your learning profile')}")
                
                # Skills preview
                skills = course.get('skills', [])
                if skills:
                    st.write(f"**Skills:** {', '.join(skills[:3])}")
            
            with col2:
                st.write(f"**Difficulty:** {course.get('difficulty', 'beginner').title()}")
                st.write(f"**Duration:** {course.get('duration', 0)} min")
                st.write(f"**Type:** {course.get('content_type', 'mixed').title()}")
            
            with col3:
                # Confidence indicator
                match_score = rec.get('match_score', 0)
                if match_score > 0.8:
                    confidence = "🟢 High"
                elif match_score > 0.6:
                    confidence = "🟡 Medium"
                else:
                    confidence = "🔴 Low"
                
                st.write(f"**Match:** {confidence}")
                
                # Action buttons
                if st.button(f"▶️ Start Course", key=f"rec_start_{i}"):
                    st.success(f"Starting: {course.get('title', 'Course')}!")
                
                if st.button(f"📋 Add to Plan", key=f"rec_plan_{i}"):
                    st.info("Added to your learning plan!")
            
            # Difficulty indicator
            difficulty = course.get('difficulty', 'beginner')
            if difficulty == 'beginner':
                st.markdown('<div class="alert-low">🟢 Beginner Level</div>', unsafe_allow_html=True)
            elif difficulty == 'intermediate':
                st.markdown('<div class="alert-medium">🟡 Intermediate Level</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-high">🔴 Advanced Level</div>', unsafe_allow_html=True)
            
            st.markdown("---")

def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Learning Agent - Learner Dashboard</h1>
        <p>Your personalized learning companion with smart recommendations and progress tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    st.sidebar.title("⚙️ Configuration")
    
    # API Configuration
    st.sidebar.subheader("🔌 API Settings")
    api_base_url = st.sidebar.text_input(
        "API Base URL",
        value="http://localhost:5001",
        help="URL of the enhanced Flask API server"
    )
    
    # Initialize API manager
    api_manager = APIManager(api_base_url)
    
    # Connection status
    if st.sidebar.button("🔍 Test Connection"):
        health_data = api_manager._make_request("/api/health")
        if health_data:
            st.sidebar.success("✅ API Connected Successfully")
            st.sidebar.write(f"Version: {health_data.get('version', 'Unknown')}")
            st.sidebar.write(f"Systems: {'✅' if health_data.get('systems_loaded') else '❌'}")
        else:
            st.sidebar.error("❌ Connection Failed")
    
    # Learner selection
    st.sidebar.subheader("👤 Learner Profile")
    learner_id = st.sidebar.text_input("Learner ID", value="demo-alice-123")
    
    if not learner_id:
        st.warning("👆 Please enter a learner ID to continue")
        return
    
    # Navigation
    st.sidebar.subheader("🧭 Navigation")
    page = st.sidebar.radio("Select View", [
        "📊 Overview Dashboard",
        "🛤️ Learning Path", 
        "🎯 Next Recommendations",
        "📈 Progress Analytics",
        "⚡ Quick Actions"
    ])
    
    # Test API connection on load
    with st.spinner("🔄 Connecting to API..."):
        health_data = api_manager._make_request("/api/health")
        if not health_data:
            st.error("💥 **API Connection Failed** - Make sure the enhanced Flask API is running on the configured URL")
            st.info("💡 **Troubleshooting:**")
            st.write("- Check that the API server is running on the specified URL")
            st.write("- Verify the URL is correct (default: http://localhost:5001)")
            st.write("- Ensure there are no network connectivity issues")
            return
    
    if page == "📊 Overview Dashboard":
        display_overview_dashboard(api_manager, learner_id)
    elif page == "🛤️ Learning Path":
        display_learning_path_page(api_manager, learner_id)
    elif page == "🎯 Next Recommendations":
        display_recommendations_page(api_manager, learner_id)
    elif page == "📈 Progress Analytics":
        display_analytics_page(api_manager, learner_id)
    elif page == "⚡ Quick Actions":
        display_quick_actions(api_manager, learner_id)

def display_overview_dashboard(api_manager: APIManager, learner_id: str):
    """Display the main overview dashboard"""
    
    st.header("📊 Learning Overview")
    
    # Get learner data and score
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Loading states for API calls
        with st.spinner("📊 Loading learner data..."):
            learner_data = api_manager.get_learner_data(learner_id)
        
        with st.spinner("🎯 Loading score analysis..."):
            score_data = api_manager.get_learner_score(learner_id)
    
    if not learner_data or not score_data:
        st.error("❌ Failed to load learner data. Please check the API connection and learner ID.")
        return
    
    # Key metrics
    personal_info = learner_data.get('personal_info', {})
    learning_profile = learner_data.get('learning_profile', {})
    performance_metrics = learner_data.get('performance_metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Overall Score", 
            f"{score_data.get('overall_score', 0):.1f}/100",
            delta=None
        )
    
    with col2:
        total_activities = learning_profile.get('total_activities', 0)
        st.metric(
            "📚 Activities", 
            total_activities,
            delta=None
        )
    
    with col3:
        avg_score = performance_metrics.get('average_score', 0)
        st.metric(
            "📈 Avg Score", 
            f"{avg_score:.1f}",
            delta=None
        )
    
    with col4:
        learning_velocity = learning_profile.get('learning_velocity', 0)
        st.metric(
            "⚡ Velocity", 
            f"{learning_velocity:.1f}/week",
            delta=None
        )
    
    # Performance level indicator
    performance_level = score_data.get('performance_level', 'unknown').title()
    if performance_level.lower() in ['excellent', 'very_good']:
        st.success(f"🌟 **Performance Level:** {performance_level}")
    elif performance_level.lower() in ['good', 'average']:
        st.info(f"📊 **Performance Level:** {performance_level}")
    else:
        st.warning(f"🎯 **Performance Level:** {performance_level}")
    
    # Progress charts
    st.subheader("📈 Visual Analytics")
    
    with st.spinner("📊 Loading progress charts..."):
        history_data = api_manager.get_score_history(learner_id)
        fig = create_progress_chart(score_data, history_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick insights
    st.subheader("💡 Learning Insights")
    insights = score_data.get('insights', [])
    for insight in insights:
        st.write(f"• {insight}")

def display_learning_path_page(api_manager: APIManager, learner_id: str):
    """Display the learning path page"""
    
    st.header("🛤️ Your Learning Path")
    st.markdown("Personalized learning journey based on your goals and progress")
    
    with st.spinner("🛤️ Loading learning path..."):
        learning_path_data = api_manager.get_learning_path(learner_id)
    
    if not learning_path_data:
        st.error("❌ Failed to load learning path. Please check your connection.")
        return
    
    display_learning_path(learning_path_data)

def display_recommendations_page(api_manager: APIManager, learner_id: str):
    """Display the recommendations page"""
    
    st.header("🎯 Recommended Next Modules")
    st.markdown("AI-powered recommendations tailored to your learning style and progress")
    
    with st.spinner("🎯 Generating personalized recommendations..."):
        recommendations_data = api_manager.get_recommendations(learner_id, count=6)
    
    if not recommendations_data:
        st.error("❌ Failed to load recommendations. Please check your connection.")
        return
    
    display_recommendations(recommendations_data, api_manager, learner_id)

def display_analytics_page(api_manager: APIManager, learner_id: str):
    """Display the analytics page"""
    
    st.header("📈 Progress Analytics")
    st.markdown("Detailed performance analysis and learning trends")
    
    with st.spinner("📈 Loading analytics data..."):
        score_data = api_manager.get_learner_score(learner_id)
        history_data = api_manager.get_score_history(learner_id)
    
    if not score_data:
        st.error("❌ Failed to load analytics data.")
        return
    
    # Component score breakdown
    st.subheader("📊 Component Score Analysis")
    component_scores = score_data.get('component_scores', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create component score chart
        categories = ['Test Score', 'Quiz Score', 'Engagement', 'Consistency']
        values = [
            component_scores.get('test_score', 0),
            component_scores.get('quiz_score', 0),
            component_scores.get('engagement_score', 0),
            component_scores.get('consistency_score', 0)
        ]
        
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=values,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )])
        fig.update_layout(
            title="Component Scores",
            xaxis_title="Score Components",
            yaxis_title="Score (0-100)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score distribution
        st.subheader("📈 Score Distribution")
        score_ranges = ['0-20', '21-40', '41-60', '61-80', '81-100']
        # Mock data - in real implementation, this would come from historical data
        distribution = [0, 0, 10, 30, 60]  # Example distribution
        
        fig = go.Figure(data=[go.Pie(
            labels=score_ranges,
            values=distribution,
            hole=0.3
        )])
        fig.update_layout(
            title="Score Distribution",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed insights
    st.subheader("💡 Detailed Insights")
    insights = score_data.get('insights', [])
    for insight in insights:
        st.write(f"• {insight}")
    
    # Recommendations based on score
    st.subheader("🎯 Score-Based Recommendations")
    recommendations = score_data.get('recommendations', [])
    for rec in recommendations:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{rec.get('title', 'Recommendation')}</h4>
            <p>{rec.get('description', '')}</p>
            <p><strong>Priority:</strong> {rec.get('priority', 'medium').title()}</p>
        </div>
        """, unsafe_allow_html=True)

def display_quick_actions(api_manager: APIManager, learner_id: str):
    """Display quick actions page"""
    
    st.header("⚡ Quick Actions")
    st.markdown("Manage your learning activities and track progress")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Log New Activity")
        
        with st.form("activity_form"):
            activity_type = st.selectbox("Activity Type", [
                "module_completed",
                "quiz_completed", 
                "test_completed",
                "assignment_submitted",
                "project_completed"
            ])
            
            score = st.number_input("Score (0-100)", min_value=0, max_value=100, value=75)
            duration = st.number_input("Duration (minutes)", min_value=0, value=30)
            
            submitted = st.form_submit_button("📤 Log Activity")
            
            if submitted:
                activity_data = {
                    "activity_type": activity_type,
                    "score": score,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                }
                
                with st.spinner("📤 Logging activity..."):
                    result = api_manager.log_activity(learner_id, activity_data)
                
                if result:
                    st.success("✅ Activity logged successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to log activity")
    
    with col2:
        st.subheader("🎯 Quick Recommendations")
        
        if st.button("🎯 Get New Recommendations", use_container_width=True):
            with st.spinner("🎯 Generating recommendations..."):
                recommendations_data = api_manager.get_recommendations(learner_id, count=3)
            
            if recommendations_data:
                st.success("✅ New recommendations generated!")
                st.write("Check the 'Next Recommendations' page for full details")
            else:
                st.error("❌ Failed to generate recommendations")
        
        if st.button("🛤️ Update Learning Path", use_container_width=True):
            with st.spinner("🛤️ Updating learning path..."):
                learning_path_data = api_manager.get_learning_path(learner_id)
            
            if learning_path_data:
                st.success("✅ Learning path updated!")
                st.write("Check the 'Learning Path' page for updates")
            else:
                st.error("❌ Failed to update learning path")
    
    # Recent activities
    st.subheader("📊 Recent Activity Summary")
    
    with st.spinner("📊 Loading recent activities..."):
        learner_data = api_manager.get_learner_data(learner_id)
    
    if learner_data:
        recent_activities = learner_data.get('recent_activities', [])[:5]
        
        if recent_activities:
            for activity in recent_activities:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{activity.get('activity_type', 'Unknown').replace('_', ' ').title()}**")
                with col2:
                    st.write(f"Score: {activity.get('score', 'N/A')}")
                with col3:
                    st.write(f"{activity.get('duration', 0)} min")
        else:
            st.info("No recent activities to display")

if __name__ == "__main__":
    main()