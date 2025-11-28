#!/usr/bin/env python3
"""
DAY 4 - Instructor Dashboard
Dedicated interface for instructors with analytics overview, at-risk learner alerts,
and cohort performance comparison
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
import numpy as np
from typing import List, Dict, Any

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Learning Agent - Instructor Dashboard",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
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
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #ff9800;
    }
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #2196f3;
    }
    .cohort-table {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        border: 1px solid #ddd;
    }
    .performance-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .badge-excellent { background-color: #4caf50; }
    .badge-good { background-color: #8bc34a; }
    .badge-average { background-color: #ff9800; }
    .badge-poor { background-color: #f44336; }
    .badge-struggling { background-color: #9c27b0; }
</style>
""", unsafe_allow_html=True)

class APIManager:
    """Enhanced API manager with loading states and error handling for instructor features"""
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None, timeout: int = 15):
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
    
    def get_all_learners(self):
        """Get all learners for instructor overview"""
        return self._make_request("/api/learners")
    
    def get_learner_analytics(self, learner_id: str):
        """Get comprehensive learner analytics"""
        return self._make_request(f"/api/analytics/learner/{learner_id}")
    
    def get_cohort_analytics(self, group_by: str = "learning_style"):
        """Get cohort comparison analytics"""
        return self._make_request(f"/api/analytics/cohort?group_by={group_by}")
    
    def get_performance_insights(self):
        """Get system-wide performance insights"""
        return self._make_request("/api/analytics/performance-insights")
    
    def batch_calculate_scores(self, learner_ids: List[str]):
        """Batch calculate scores for multiple learners"""
        return self._make_request("/api/batch/calculate-scores", 'POST', {"learner_ids": learner_ids})
    
    def batch_generate_recommendations(self, learner_ids: List[str], count: int = 5):
        """Batch generate recommendations for multiple learners"""
        return self._make_request("/api/batch/generate-recommendations", 'POST', 
                                {"learner_ids": learner_ids, "count": count})

class RiskAssessmentEngine:
    """Engine to identify at-risk learners based on multiple factors"""
    
    def __init__(self):
        self.risk_thresholds = {
            'low_score': 60,
            'low_engagement': 40,
            'inconsistent_activity': 30,
            'declining_trend': -10,  # percentage decline
            'low_activity_count': 3
        }
    
    def assess_learner_risk(self, learner_data: Dict, score_data: Dict = None) -> Dict[str, Any]:
        """Assess risk level for a single learner"""
        risk_factors = []
        risk_score = 0
        risk_level = "low"
        
        # Score-based risk assessment
        if score_data:
            overall_score = score_data.get('overall_score', 0)
            if overall_score < self.risk_thresholds['low_score']:
                risk_factors.append(f"Low overall score: {overall_score:.1f}")
                risk_score += 30
                risk_level = "high" if overall_score < 40 else "medium"
            
            # Component score analysis
            component_scores = score_data.get('component_scores', {})
            if component_scores.get('engagement_score', 0) < self.risk_thresholds['low_engagement']:
                risk_factors.append("Low engagement score")
                risk_score += 20
                risk_level = "high"
        
        # Activity-based risk assessment
        activities = learner_data.get('activities', [])
        if len(activities) < self.risk_thresholds['low_activity_count']:
            risk_factors.append(f"Low activity count: {len(activities)}")
            risk_score += 15
            if risk_level == "low":
                risk_level = "medium"
        
        # Recent activity analysis
        recent_activities = [a for a in activities if a.get('timestamp')]
        if len(recent_activities) < 2:
            risk_factors.append("Insufficient recent activity")
            risk_score += 25
            risk_level = "high"
        
        # Score trend analysis (if available)
        # This would require historical data - using mock for demo
        if len(activities) >= 3:
            scores = [a.get('score', 0) for a in activities[-3:] if a.get('score')]
            if len(scores) >= 2:
                trend = (scores[-1] - scores[0]) / scores[0] * 100
                if trend < self.risk_thresholds['declining_trend']:
                    risk_factors.append(f"Declining performance trend: {trend:.1f}%")
                    risk_score += 20
                    if risk_level == "low":
                        risk_level = "medium"
        
        # Final risk level determination
        if risk_score >= 60:
            risk_level = "critical"
        elif risk_score >= 40:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': self._get_risk_recommendation(risk_level, risk_factors)
        }
    
    def _get_risk_recommendation(self, risk_level: str, risk_factors: List[str]) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'critical': "Immediate intervention required. Consider one-on-one mentoring and course adjustment.",
            'high': "Regular check-ins recommended. Provide additional support and motivation.",
            'medium': "Monitor progress closely. Offer supplementary resources.",
            'low': "Continue current approach. Regular encouragement is sufficient."
        }
        return recommendations.get(risk_level, "Monitor progress and provide standard support.")

def create_performance_overview_chart(analytics_data: Dict):
    """Create comprehensive performance overview charts"""
    
    # Performance distribution data
    performance_levels = analytics_data.get('performance_levels', {})
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Performance Distribution', 'Score Statistics', 'Learning Velocity', 'Activity Trends'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # Performance distribution pie chart
    if performance_levels:
        fig.add_trace(go.Pie(
            labels=list(performance_levels.keys()),
            values=list(performance_levels.values()),
            name="Performance Levels"
        ), row=1, col=1)
    
    # Score statistics
    score_stats = analytics_data.get('score_distribution', {})
    if score_stats:
        categories = ['Highest', 'Average', 'Median', 'Lowest']
        values = [
            score_stats.get('highest', 0),
            analytics_data.get('average_score', 0),
            score_stats.get('median', 0),
            score_stats.get('lowest', 0)
        ]
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            name="Score Statistics",
            marker_color='lightblue'
        ), row=1, col=2)
    
    # Learning velocity scatter (mock data for demo)
    weeks = list(range(1, 13))  # 12 weeks
    velocities = np.random.normal(2.5, 0.8, 12)  # Mock velocity data
    
    fig.add_trace(go.Scatter(
        x=weeks,
        y=velocities,
        mode='lines+markers',
        name='Learning Velocity',
        line=dict(color='green', width=3)
    ), row=2, col=1)
    
    # Activity trends (mock data)
    activity_types = ['Modules', 'Quizzes', 'Tests', 'Projects']
    totals = [45, 32, 18, 25]
    
    fig.add_trace(go.Bar(
        x=activity_types,
        y=totals,
        name='Activity Counts',
        marker_color='orange'
    ), row=2, col=2)
    
    fig.update_layout(
        height=700,
        showlegend=False,
        title_text="📊 System Performance Overview",
        title_x=0.5
    )
    
    return fig

def display_at_risk_learners(at_risk_learners: List[Dict], api_manager: APIManager):
    """Display at-risk learners with detailed alerts"""
    
    if not at_risk_learners:
        st.success("🎉 **No at-risk learners detected!** All learners are performing well.")
        return
    
    # Risk level summary
    risk_counts = {}
    for learner in at_risk_learners:
        risk_level = learner['risk_assessment']['risk_level']
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
    
    st.subheader("🚨 At-Risk Learner Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Count displays with colors
    with col1:
        critical_count = risk_counts.get('critical', 0)
        if critical_count > 0:
            st.markdown(f'<div class="alert-critical"><h4>Critical: {critical_count}</h4></div>', unsafe_allow_html=True)
        else:
            st.metric("🚨 Critical", 0)
    
    with col2:
        high_count = risk_counts.get('high', 0)
        if high_count > 0:
            st.markdown(f'<div class="alert-warning"><h4>High: {high_count}</h4></div>', unsafe_allow_html=True)
        else:
            st.metric("⚠️ High Risk", 0)
    
    with col3:
        medium_count = risk_counts.get('medium', 0)
        if medium_count > 0:
            st.markdown(f'<div class="alert-info"><h4>Medium: {medium_count}</h4></div>', unsafe_allow_html=True)
        else:
            st.metric("🔍 Medium Risk", 0)
    
    with col4:
        st.metric("👥 Total At Risk", len(at_risk_learners))
    
    # Detailed learner list
    st.subheader("👥 At-Risk Learner Details")
    
    for i, learner in enumerate(at_risk_learners):
        risk_assessment = learner['risk_assessment']
        risk_level = risk_assessment['risk_level']
        
        # Choose alert styling based on risk level
        if risk_level == 'critical':
            alert_class = "alert-critical"
            emoji = "🚨"
        elif risk_level == 'high':
            alert_class = "alert-warning"
            emoji = "⚠️"
        else:
            alert_class = "alert-info"
            emoji = "🔍"
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="{alert_class}">
                    <h4>{emoji} {learner.get('name', 'Unknown Learner')} (ID: {learner.get('id', 'N/A')})</h4>
                    <p><strong>Risk Level:</strong> {risk_level.upper()}</p>
                    <p><strong>Risk Score:</strong> {risk_assessment['risk_score']}/100</p>
                    <p><strong>Factors:</strong></p>
                    <ul>
                        {''.join([f'<li>{factor}</li>' for factor in risk_assessment['risk_factors']])}
                    </ul>
                    <p><strong>Recommendation:</strong> {risk_assessment['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Quick actions
                if st.button(f"📊 View Details", key=f"details_{i}"):
                    st.info(f"Detailed analytics for {learner.get('name', 'learner')} will be shown")
                
                if st.button(f"💬 Send Message", key=f"message_{i}"):
                    st.info(f"Messaging interface for {learner.get('name', 'learner')} will be opened")
            
            with col3:
                # Performance metrics
                if 'score_data' in learner:
                    score_data = learner['score_data']
                    st.metric("Score", f"{score_data.get('overall_score', 0):.1f}")
                    st.metric("Activities", learner.get('activity_count', 0))
            
            st.markdown("---")

def display_cohort_comparison(cohort_data: Dict):
    """Display cohort performance comparison"""
    
    st.subheader("📊 Cohort Performance Comparison")
    
    if not cohort_data or 'error' in cohort_data:
        st.warning("⚠️ Cohort comparison data not available")
        return
    
    # Group by learning style as default
    groups = cohort_data.get('groups', {})
    
    if not groups:
        st.info("📈 No cohort data available for comparison")
        return
    
    # Create comparison table
    cohort_df = pd.DataFrame([
        {
            'Group': group_name,
            'Avg Score': group_data.get('average_score', 0),
            'Learners': group_data.get('learner_count', 0),
            'Completion Rate': f"{group_data.get('completion_rate', 0):.1f}%",
            'Engagement': f"{group_data.get('avg_engagement', 0):.1f}"
        }
        for group_name, group_data in groups.items()
    ])
    
    # Display table with styling
    st.markdown('<div class="cohort-table">', unsafe_allow_html=True)
    st.dataframe(cohort_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visual comparison
    if len(groups) > 1:
        st.subheader("📈 Visual Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average score comparison
            fig1 = px.bar(
                x=list(groups.keys()),
                y=[group.get('average_score', 0) for group in groups.values()],
                title="Average Score by Learning Style",
                labels={'x': 'Learning Style', 'y': 'Average Score'}
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Learner count comparison
            fig2 = px.pie(
                values=[group.get('learner_count', 0) for group in groups.values()],
                names=list(groups.keys()),
                title="Learner Distribution"
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

def main():
    """Main instructor dashboard application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>👨‍🏫 Learning Agent - Instructor Dashboard</h1>
        <p>Comprehensive analytics and learner management for education professionals</p>
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
    
    # Initialize API manager and risk assessment engine
    api_manager = APIManager(api_base_url)
    risk_engine = RiskAssessmentEngine()
    
    # Connection status
    if st.sidebar.button("🔍 Test Connection"):
        health_data = api_manager._make_request("/api/health")
        if health_data:
            st.sidebar.success("✅ API Connected Successfully")
            st.sidebar.write(f"Version: {health_data.get('version', 'Unknown')}")
            st.sidebar.write(f"Systems: {'✅' if health_data.get('systems_loaded') else '❌'}")
        else:
            st.sidebar.error("❌ Connection Failed")
    
    # Instructor controls
    st.sidebar.subheader("🎛️ Instructor Controls")
    refresh_data = st.sidebar.button("🔄 Refresh All Data")
    
    # Cohort grouping options
    st.sidebar.subheader("📊 Grouping Options")
    group_by = st.sidebar.selectbox(
        "Group Learners By",
        ["learning_style", "age_group", "performance_level", "preference"]
    )
    
    # Navigation
    st.sidebar.subheader("🧭 Navigation")
    page = st.sidebar.radio("Select View", [
        "📊 Analytics Overview",
        "🚨 At-Risk Learners",
        "👥 Cohort Comparison",
        "⚡ Batch Operations",
        "📈 Performance Trends"
    ])
    
    # Test API connection
    with st.spinner("🔄 Connecting to API..."):
        health_data = api_manager._make_request("/api/health")
        if not health_data:
            st.error("💥 **API Connection Failed** - Make sure the enhanced Flask API is running")
            st.info("💡 **Troubleshooting:**")
            st.write("- Check that the API server is running on the specified URL")
            st.write("- Verify the URL is correct (default: http://localhost:5001)")
            st.write("- Ensure there are no network connectivity issues")
            return
    
    # Load data based on page selection
    if page == "📊 Analytics Overview":
        display_analytics_overview(api_manager, refresh_data)
    elif page == "🚨 At-Risk Learners":
        display_at_risk_learners_page(api_manager, risk_engine, refresh_data)
    elif page == "👥 Cohort Comparison":
        display_cohort_comparison_page(api_manager, group_by, refresh_data)
    elif page == "⚡ Batch Operations":
        display_batch_operations_page(api_manager, refresh_data)
    elif page == "📈 Performance Trends":
        display_performance_trends_page(api_manager, refresh_data)

def display_analytics_overview(api_manager: APIManager, refresh_data: bool = False):
    """Display the main analytics overview"""
    
    st.header("📊 System Analytics Overview")
    st.markdown("Comprehensive performance metrics and system insights")
    
    # Load analytics data
    if refresh_data:
        with st.spinner("📊 Loading comprehensive analytics..."):
            analytics_data = api_manager.get_all_learners()
            performance_insights = api_manager.get_performance_insights()
    else:
        analytics_data = api_manager.get_all_learners()
        performance_insights = api_manager.get_performance_insights()
    
    if not analytics_data:
        st.error("❌ Failed to load analytics data")
        return
    
    # Extract learner data
    learners = analytics_data.get('learners', [])
    total_learners = analytics_data.get('count', 0)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Learners", total_learners)
    
    with col2:
        # Calculate active learners (with recent activity)
        active_learners = len([l for l in learners if l.get('activity_count', 0) > 0])
        st.metric("🎯 Active Learners", active_learners)
    
    with col3:
        # Average activities per learner
        avg_activities = sum(l.get('activity_count', 0) for l in learners) / max(total_learners, 1)
        st.metric("📚 Avg Activities", f"{avg_activities:.1f}")
    
    with col4:
        # System health (based on data availability)
        health_score = min((len(learners) / 10) * 100, 100) if total_learners > 0 else 0
        st.metric("💚 System Health", f"{health_score:.0f}%")
    
    # Performance overview chart
    st.subheader("📈 Performance Overview")
    
    if performance_insights:
        fig = create_performance_overview_chart(performance_insights)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Performance insights not available - using basic analytics")
        
        # Create basic performance chart
        if learners:
            # Mock performance data for demo
            categories = ['Test Scores', 'Quiz Scores', 'Engagement', 'Consistency']
            values = [78, 82, 65, 71]  # Example values
            
            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=values,
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            )])
            fig.update_layout(
                title="System Performance Metrics",
                xaxis_title="Performance Areas",
                yaxis_title="Average Score",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Performance insights
    if performance_insights:
        st.subheader("💡 Performance Insights")
        recommendations = performance_insights.get('recommendations', [])
        for rec in recommendations:
            st.write(f"• {rec}")
    
    # Recent activity summary
    st.subheader("📅 Recent Activity Summary")
    
    recent_activities = []
    for learner in learners[:5]:  # Show recent activities for first 5 learners
        activities = learner.get('activities', [])
        for activity in activities[-2:]:  # Last 2 activities per learner
            recent_activities.append({
                'Learner': learner.get('name', 'Unknown'),
                'Activity': activity.get('activity_type', 'Unknown'),
                'Score': activity.get('score', 'N/A'),
                'Date': activity.get('timestamp', 'N/A')[:10]  # Just the date part
            })
    
    if recent_activities:
        recent_df = pd.DataFrame(recent_activities)
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No recent activity data available")

def display_at_risk_learners_page(api_manager: APIManager, risk_engine: RiskAssessmentEngine, refresh_data: bool):
    """Display the at-risk learners page"""
    
    st.header("🚨 At-Risk Learner Detection")
    st.markdown("AI-powered identification of learners who may need additional support")
    
    # Load learner data
    if refresh_data:
        with st.spinner("🔍 Analyzing learner risk profiles..."):
            learners_data = api_manager.get_all_learners()
    else:
        learners_data = api_manager.get_all_learners()
    
    if not learners_data:
        st.error("❌ Failed to load learner data")
        return
    
    learners = learners_data.get('learners', [])
    
    if not learners:
        st.info("📝 No learners found in the system")
        return
    
    # Risk assessment for all learners
    at_risk_learners = []
    
    with st.spinner("🔍 Assessing learner risk profiles..."):
        for learner in learners:
            # Get learner score data
            score_data = None
            try:
                score_data = api_manager.get_learner_score(learner.get('id'))
            except:
                pass  # Continue without score data
            
            # Perform risk assessment
            risk_assessment = risk_engine.assess_learner_risk(learner, score_data)
            
            # Add to at-risk list if risk level is medium or higher
            if risk_assessment['risk_level'] in ['medium', 'high', 'critical']:
                learner_info = {
                    'id': learner.get('id'),
                    'name': learner.get('name', 'Unknown'),
                    'risk_assessment': risk_assessment,
                    'score_data': score_data,
                    'activity_count': learner.get('activity_count', 0)
                }
                at_risk_learners.append(learner_info)
    
    # Sort by risk level and score
    risk_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    at_risk_learners.sort(key=lambda x: risk_order.get(x['risk_assessment']['risk_level'], 0), reverse=True)
    
    # Display results
    display_at_risk_learners(at_risk_learners, api_manager)
    
    # Bulk actions for at-risk learners
    if at_risk_learners:
        st.subheader("⚡ Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Batch Calculate Scores", use_container_width=True):
                with st.spinner("📊 Calculating scores for at-risk learners..."):
                    learner_ids = [learner['id'] for learner in at_risk_learners]
                    result = api_manager.batch_calculate_scores(learner_ids)
                
                if result:
                    successful = result.get('successful_calculations', 0)
                    st.success(f"✅ Score calculation completed for {successful} learners")
                else:
                    st.error("❌ Batch score calculation failed")
        
        with col2:
            if st.button("🎯 Generate Support Recommendations", use_container_width=True):
                with st.spinner("🎯 Generating support recommendations..."):
                    learner_ids = [learner['id'] for learner in at_risk_learners]
                    result = api_manager.batch_generate_recommendations(learner_ids, count=3)
                
                if result:
                    successful = result.get('successful_generations', 0)
                    st.success(f"✅ Support recommendations generated for {successful} learners")
                else:
                    st.error("❌ Batch recommendation generation failed")

def display_cohort_comparison_page(api_manager: APIManager, group_by: str, refresh_data: bool):
    """Display the cohort comparison page"""
    
    st.header("👥 Cohort Performance Comparison")
    st.markdown(f"Compare learner performance grouped by {group_by.replace('_', ' ').title()}")
    
    # Load cohort data
    if refresh_data:
        with st.spinner(f"📊 Loading cohort data (grouped by {group_by})..."):
            cohort_data = api_manager.get_cohort_analytics(group_by)
    else:
        cohort_data = api_manager.get_cohort_analytics(group_by)
    
    if not cohort_data:
        st.error("❌ Failed to load cohort comparison data")
        return
    
    display_cohort_comparison(cohort_data)
    
    # Detailed cohort analysis
    st.subheader("🔍 Detailed Analysis")
    
    # Additional insights based on cohort data
    if cohort_data and 'groups' in cohort_data:
        groups = cohort_data['groups']
        
        # Performance ranking
        if len(groups) > 1:
            st.subheader("🏆 Performance Ranking")
            
            # Sort groups by average score
            sorted_groups = sorted(groups.items(), 
                                 key=lambda x: x[1].get('average_score', 0), 
                                 reverse=True)
            
            for i, (group_name, group_data) in enumerate(sorted_groups, 1):
                avg_score = group_data.get('average_score', 0)
                learner_count = group_data.get('learner_count', 0)
                
                if i == 1:
                    emoji = "🥇"
                elif i == 2:
                    emoji = "🥈"
                elif i == 3:
                    emoji = "🥉"
                else:
                    emoji = f"{i}."
                
                st.write(f"{emoji} **{group_name.title()}**: {avg_score:.1f} avg score ({learner_count} learners)")

def display_batch_operations_page(api_manager: APIManager, refresh_data: bool):
    """Display batch operations page"""
    
    st.header("⚡ Batch Operations")
    st.markdown("Perform operations on multiple learners simultaneously")
    
    # Load all learners for selection
    with st.spinner("📊 Loading learner list..."):
        learners_data = api_manager.get_all_learners()
    
    if not learners_data:
        st.error("❌ Failed to load learner data")
        return
    
    learners = learners_data.get('learners', [])
    if not learners:
        st.info("📝 No learners available for batch operations")
        return
    
    # Learner selection
    st.subheader("👥 Learner Selection")
    
    learner_options = {f"{learner.get('name', 'Unknown')} (ID: {learner.get('id', 'N/A')})": learner 
                      for learner in learners}
    
    selected_learners = st.multiselect(
        "Select learners for batch operations",
        options=list(learner_options.keys()),
        default=list(learner_options.keys())[:3]  # Select first 3 by default
    )
    
    if not selected_learners:
        st.warning("⚠️ Please select learners for batch operations")
        return
    
    st.info(f"📝 Selected {len(selected_learners)} learners for batch processing")
    
    # Batch operations
    st.subheader("⚙️ Available Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Score Operations")
        
        if st.button("🔄 Recalculate All Scores", use_container_width=True):
            with st.spinner("📊 Recalculating scores..."):
                learner_ids = [learner_options[name]['id'] for name in selected_learners]
                result = api_manager.batch_calculate_scores(learner_ids)
            
            if result:
                successful = result.get('successful_calculations', 0)
                failed = result.get('failed_calculations', 0)
                st.success(f"✅ Score recalculation completed: {successful} successful, {failed} failed")
                
                # Show detailed results
                if result.get('batch_results'):
                    with st.expander("📋 View Detailed Results"):
                        results_df = pd.DataFrame(result['batch_results'])
                        st.dataframe(results_df)
            else:
                st.error("❌ Batch score calculation failed")
    
    with col2:
        st.subheader("🎯 Recommendation Operations")
        
        recommendation_count = st.slider("Number of recommendations per learner", 3, 10, 5)
        
        if st.button("🎯 Generate Recommendations", use_container_width=True):
            with st.spinner(f"🎯 Generating {recommendation_count} recommendations for each learner..."):
                learner_ids = [learner_options[name]['id'] for name in selected_learners]
                result = api_manager.batch_generate_recommendations(learner_ids, recommendation_count)
            
            if result:
                successful = result.get('successful_generations', 0)
                failed = result.get('failed_generations', 0)
                st.success(f"✅ Recommendation generation completed: {successful} successful, {failed} failed")
            else:
                st.error("❌ Batch recommendation generation failed")

def display_performance_trends_page(api_manager: APIManager, refresh_data: bool):
    """Display performance trends page"""
    
    st.header("📈 Performance Trends")
    st.markdown("Analyze learning performance trends over time")
    
    # Load performance insights
    with st.spinner("📈 Loading performance trends..."):
        performance_insights = api_manager.get_performance_insights()
    
    if not performance_insights:
        st.error("❌ Failed to load performance trends data")
        return
    
    # Component analysis
    component_analysis = performance_insights.get('component_analysis', {})
    
    if component_analysis:
        st.subheader("📊 Component Score Trends")
        
        # Create trends visualization
        categories = list(component_analysis.keys())
        averages = [component_analysis[cat].get('average', 0) for cat in categories]
        medians = [component_analysis[cat].get('median', 0) for cat in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=categories,
            y=averages,
            mode='lines+markers',
            name='Average',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=categories,
            y=medians,
            mode='lines+markers',
            name='Median',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title="Score Component Trends",
            xaxis_title="Score Components",
            yaxis_title="Score Value",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trend analysis
    st.subheader("📈 Trend Analysis")
    
    # Mock trend data for demonstration
    weeks = list(range(1, 13))
    overall_performance = np.random.normal(75, 8, 12).tolist()
    engagement = np.random.normal(68, 12, 12).tolist()
    
    trend_df = pd.DataFrame({
        'Week': weeks,
        'Overall Performance': overall_performance,
        'Engagement': engagement
    })
    
    # Line chart for trends
    fig = px.line(trend_df, x='Week', y=['Overall Performance', 'Engagement'],
                  title="12-Week Performance Trends")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance recommendations
    st.subheader("💡 System Recommendations")
    recommendations = performance_insights.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

if __name__ == "__main__":
    main()