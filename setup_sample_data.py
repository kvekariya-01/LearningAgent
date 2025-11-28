#!/usr/bin/env python3
"""
Setup sample learners and test data for testing score-based recommendations
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_sample_data():
    """Create sample learners and test data for testing recommendations"""
    
    try:
        # Import required modules
        from config.db_config import db
        from models.learner import Learner
        from models.engagement import Engagement
        from models.test_result import TestResult
        from utils.crud_operations import create_learner, create_engagement, read_learners
        
        print("Setting up sample learners and test data...")
        print("=" * 50)
        
        # Check database connection
        if db is None:
            print("X Database not connected. Using in-memory storage.")
            return False
        
        print(f"OK Connected to MongoDB Atlas database: {db.name}")
        
        # Sample learners data
        sample_learners = [
            {
                "id": "alice-demo-001",
                "name": "Alice Johnson",
                "age": 28,
                "gender": "Female",
                "learning_style": "Visual",
                "preferences": ["Python Programming", "Data Science", "Machine Learning"],
                "activities": [
                    {"activity_type": "course_completed", "timestamp": "2024-01-15T10:00:00", "course_id": "python-101"},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-16T14:30:00", "course_id": "python-101", "score": 88},
                    {"activity_type": "assignment_submitted", "timestamp": "2024-01-17T09:15:00", "course_id": "python-101", "score": 92}
                ]
            },
            {
                "id": "bob-demo-002", 
                "name": "Bob Smith",
                "age": 35,
                "gender": "Male",
                "learning_style": "Kinesthetic",
                "preferences": ["Web Development", "JavaScript", "React"],
                "activities": [
                    {"activity_type": "course_completed", "timestamp": "2024-01-14T16:45:00", "course_id": "html-css-101"},
                    {"activity_type": "project_completed", "timestamp": "2024-01-18T11:20:00", "course_id": "html-css-101", "score": 85}
                ]
            },
            {
                "id": "carol-demo-003",
                "name": "Carol Davis", 
                "age": 22,
                "gender": "Female",
                "learning_style": "Auditory",
                "preferences": ["UI/UX Design", "Figma", "User Experience"],
                "activities": [
                    {"activity_type": "portfolio_submitted", "timestamp": "2024-01-19T13:30:00", "course_id": "ui-design-101", "score": 96}
                ]
            },
            {
                "id": "david-demo-004",
                "name": "David Chen",
                "age": 31,
                "gender": "Male", 
                "learning_style": "Reading/Writing",
                "preferences": ["Database Design", "SQL", "Data Management"],
                "activities": [
                    {"activity_type": "course_completed", "timestamp": "2024-01-10T08:00:00", "course_id": "sql-basics"},
                    {"activity_type": "test_completed", "timestamp": "2024-01-20T15:00:00", "course_id": "sql-basics", "score": 78},
                    {"activity_type": "quiz_completed", "timestamp": "2024-01-21T10:30:00", "course_id": "sql-basics", "score": 82}
                ]
            }
        ]
        
        # Create learners
        created_learners = []
        for learner_data in sample_learners:
            try:
                learner = Learner(
                    id=learner_data["id"],
                    name=learner_data["name"],
                    age=learner_data["age"],
                    gender=learner_data["gender"],
                    learning_style=learner_data["learning_style"],
                    preferences=learner_data["preferences"]
                )
                
                result = create_learner(learner)
                if result:
                    created_learners.append(learner_data["id"])
                    print(f"OK Created learner: {learner_data['name']} ({learner_data['id']})")
                else:
                    print(f"X Failed to create learner: {learner_data['name']}")
                    
            except Exception as e:
                print(f"X Error creating learner {learner_data['name']}: {e}")
        
        # Create sample test results for scoring
        test_results = [
            # Alice's test results (strong performance)
            {
                "learner_id": "alice-demo-001",
                "test_id": "quiz_python_basics",
                "test_type": "quiz",
                "course_id": "python-101",
                "content_id": "quiz_python_001",
                "score": 88,
                "max_score": 100,
                "time_taken": 25.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=5)
            },
            {
                "learner_id": "alice-demo-001", 
                "test_id": "test_data_structures",
                "test_type": "test",
                "course_id": "python-101",
                "content_id": "test_python_001",
                "score": 85,
                "max_score": 100,
                "time_taken": 45.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=2)
            },
            
            # Bob's test results (moderate performance)
            {
                "learner_id": "bob-demo-002",
                "test_id": "quiz_html_basics", 
                "test_type": "quiz",
                "course_id": "html-css-101",
                "content_id": "quiz_html_001",
                "score": 75,
                "max_score": 100,
                "time_taken": 30.0,
                "attempts": 2,
                "completed_at": datetime.now() - timedelta(days=7)
            },
            {
                "learner_id": "bob-demo-002",
                "test_id": "test_css_layouts",
                "test_type": "test", 
                "course_id": "html-css-101",
                "content_id": "test_css_001",
                "score": 70,
                "max_score": 100,
                "time_taken": 55.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=3)
            },
            
            # Carol's test results (excellent performance)
            {
                "learner_id": "carol-demo-003",
                "test_id": "quiz_design_principles",
                "test_type": "quiz",
                "course_id": "ui-design-101", 
                "content_id": "quiz_design_001",
                "score": 95,
                "max_score": 100,
                "time_taken": 20.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=1)
            },
            
            # David's test results (improving performance)
            {
                "learner_id": "david-demo-004",
                "test_id": "quiz_sql_select",
                "test_type": "quiz",
                "course_id": "sql-basics",
                "content_id": "quiz_sql_001", 
                "score": 82,
                "max_score": 100,
                "time_taken": 35.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=4)
            },
            {
                "learner_id": "david-demo-004",
                "test_id": "test_sql_joins",
                "test_type": "test",
                "course_id": "sql-basics",
                "content_id": "test_sql_002",
                "score": 78,
                "max_score": 100,
                "time_taken": 50.0,
                "attempts": 1,
                "completed_at": datetime.now() - timedelta(days=1)
            }
        ]
        
        # Create test result engagements
        created_tests = 0
        for test_data in test_results:
            try:
                # Convert to engagement for storage
                engagement_data = {
                    "learner_id": test_data["learner_id"],
                    "engagement_type": f"{test_data['test_type']}_attempt",
                    "content_id": test_data["content_id"],
                    "course_id": test_data["course_id"],
                    "score": test_data["score"],
                    "max_score": test_data["max_score"],
                    "time_spent_minutes": test_data["time_taken"],
                    "attempts": test_data["attempts"],
                    "timestamp": test_data["completed_at"].isoformat(),
                    "completed": True,
                    "passed": test_data["score"] >= 70
                }
                
                engagement = type('Engagement', (), engagement_data)()
                result = create_engagement(engagement)
                
                if result:
                    created_tests += 1
                    print(f"OK Created test result: {test_data['test_id']} for {test_data['learner_id']}")
                else:
                    print(f"X Failed to create test result: {test_data['test_id']}")
                    
            except Exception as e:
                print(f"X Error creating test result {test_data['test_id']}: {e}")
        
        print(f"\nSetup Summary:")
        print(f"   Learners created: {len(created_learners)}")
        print(f"   Test results created: {created_tests}")
        print(f"   Database: {db.name if db else 'In-memory'}")
        
        # Verify learners exist
        learners = read_learners()
        print(f"   Total learners in database: {len(learners) if learners else 0}")
        
        if len(created_learners) > 0:
            print(f"\nReady to test score-based recommendations!")
            print(f"   You can now:")
            print(f"   1. Open the Streamlit app")
            print(f"   2. Select any of these learners:")
            for learner_id in created_learners:
                print(f"      - {learner_id}")
            print(f"   3. Go to 'Score-Based Recommendations'")
            print(f"   4. The 'course' KeyError should be resolved!")
            return True
        else:
            print(f"\nNo learners were created. Check database connection.")
            return False
            
    except Exception as e:
        print(f"X Error setting up sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Learning Agent - Sample Data Setup")
    print("=" * 40)
    success = setup_sample_data()
    
    if success:
        print(f"\nOK Sample data setup completed successfully!")
        print(f"The score-based recommendation fix can now be tested.")
    else:
        print(f"\nX Sample data setup failed.")
        print(f"Please check your MongoDB Atlas connection and try again.")
    
    sys.exit(0 if success else 1)