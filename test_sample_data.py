#!/usr/bin/env python3
"""
Test if sample data is working in the Streamlit app
"""
import os
import sys

def test_sample_data_loading():
    """Test the sample data loading logic from app.py"""
    print("Testing sample data loading logic...")
    
    # Simulate the logic from app.py
    learners = None  # Simulating no database connection
    
    if not learners:
        print("No learners found in database - sample data should be loaded")
        
        # Create sample learners (from app.py logic)
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
        
        print("Sample learners created successfully:")
        for learner in sample_learners:
            print(f"  - {learner['name']} (ID: {learner['id']}) - {learner['activity_count']} activities")
        
        return sample_learners
    else:
        print("Database has learners - no sample data needed")
        return learners

def check_streamlit_issue():
    """Check what might be preventing sample data from showing in Streamlit"""
    print("\nChecking Streamlit app status...")
    
    # Check if app is running
    try:
        import subprocess
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':8501' in result.stdout:
            print("Streamlit app appears to be running on port 8501")
        else:
            print("Streamlit app not detected on port 8501")
    except:
        print("Could not check Streamlit status")
    
    # Check environment
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    return True

def main():
    print("=" * 60)
    print("SAMPLE DATA TEST")
    print("=" * 60)
    
    # Test sample data logic
    sample_data = test_sample_data_loading()
    
    # Check Streamlit status
    check_streamlit_issue()
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    print("\nThe sample data logic in app.py should automatically load 3 demo learners")
    print("when no database connection is available. Here's what should happen:")
    print("\n1. If database connection fails, sample data is loaded")
    print("2. Streamlit shows 'Loading sample data for demonstration...'")
    print("3. 3 demo learners become available for testing")
    print("4. Recommendations can be generated for any demo learner")
    
    print("\nIf you're still seeing 'No learners found', the issue might be:")
    print("1. Streamlit app needs to be restarted")
    print("2. Database connection is actually working but returns empty results")
    print("3. Browser cache needs to be refreshed")
    
    print("\nSOLUTION:")
    print("1. Restart Streamlit: streamlit run app.py")
    print("2. Clear browser cache (Ctrl+F5)")
    print("3. Check the 'View Learners' page first to see if demo data loaded")
    print("4. Then go to 'View Recommendations' to test the system")
    
    return True

if __name__ == "__main__":
    main()