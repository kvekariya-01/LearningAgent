#!/usr/bin/env python3
"""
Add sample learners and activities to enable immediate testing of recommendations
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_data():
    """Create sample learners and activities for immediate testing"""
    
    try:
        # Import required modules
        from models.learner import Learner
        from utils.crud_operations import create_learner, log_activity
        
        print("Creating sample learners and activities...")
        
        # Sample learners data
        sample_learners = [
            {
                "name": "Alice Johnson",
                "age": 28,
                "gender": "Female",
                "learning_style": "Visual",
                "preferences": ["Data Science", "Machine Learning", "Python", "Statistics"],
                "activities": [
                    {
                        "activity_type": "module_completed",
                        "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                        "duration": 90,
                        "score": 92
                    },
                    {
                        "activity_type": "quiz_completed", 
                        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                        "duration": 45,
                        "score": 88
                    },
                    {
                        "activity_type": "assignment_submitted",
                        "timestamp": datetime.now().isoformat(),
                        "duration": 120,
                        "score": 95
                    }
                ]
            },
            {
                "name": "Bob Smith",
                "age": 35,
                "gender": "Male", 
                "learning_style": "Kinesthetic",
                "preferences": ["Web Development", "JavaScript", "React", "Node.js"],
                "activities": [
                    {
                        "activity_type": "project_completed",
                        "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
                        "duration": 180,
                        "score": 85
                    },
                    {
                        "activity_type": "code_review",
                        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                        "duration": 60,
                        "score": 90
                    }
                ]
            },
            {
                "name": "Carol Davis",
                "age": 22,
                "gender": "Female",
                "learning_style": "Auditory",
                "preferences": ["Design", "UX/UI", "Figma", "Graphic Design"],
                "activities": [
                    {
                        "activity_type": "portfolio_submitted",
                        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                        "duration": 150,
                        "score": 96
                    }
                ]
            }
        ]
        
        created_learners = []
        
        for learner_data in sample_learners:
            try:
                # Create learner
                learner = Learner(
                    name=learner_data["name"],
                    age=learner_data["age"],
                    gender=learner_data["gender"],
                    learning_style=learner_data["learning_style"],
                    preferences=learner_data["preferences"]
                )
                
                # Save learner to database
                learner_id = create_learner(learner)
                
                if learner_id:
                    print(f"[OK] Created learner: {learner_data['name']} (ID: {learner_id})")
                    
                    # Add activities for this learner
                    for activity_data in learner_data["activities"]:
                        try:
                            logged_learner = log_activity(
                                learner_id,
                                activity_data["activity_type"],
                                activity_data["duration"],
                                activity_data["score"]
                            )
                            
                            if logged_learner:
                                print(f"  [OK] Added activity: {activity_data['activity_type']} (Score: {activity_data['score']})")
                            else:
                                print(f"  [WARNING] Failed to add activity: {activity_data['activity_type']}")
                                
                        except Exception as e:
                            print(f"  [FAIL] Error adding activity {activity_data['activity_type']}: {e}")
                    
                    created_learners.append({
                        "id": learner_id,
                        "name": learner_data["name"],
                        "activities_count": len(learner_data["activities"])
                    })
                    
                else:
                    print(f"[FAIL] Failed to create learner: {learner_data['name']}")
                    
            except Exception as e:
                print(f"[FAIL] Error creating learner {learner_data['name']}: {e}")
        
        return created_learners
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        print("Make sure you're running this from the correct directory with all dependencies installed.")
        return []
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return []

def main():
    print("=" * 70)
    print("ADDING SAMPLE DATA FOR IMMEDIATE TESTING")
    print("=" * 70)
    
    print("\nThis will create sample learners and activities so you can immediately")
    print("test the recommendations system without manual registration.")
    
    print("\nCreating sample data...")
    created_learners = create_sample_data()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if created_learners:
        print(f"\n[OK] Successfully created {len(created_learners)} sample learners:")
        for learner in created_learners:
            print(f"  • {learner['name']} (ID: {learner['id']}) - {learner['activities_count']} activities")
        
        print("\n[TARGET] NEXT STEPS:")
        print("1. Restart your Streamlit application: streamlit run app.py")
        print("2. Go to 'View Recommendations' page")
        print("3. You'll now see sample learners to select from")
        print("4. Generate recommendations for any learner to test the system")
        
        print("\n[LIST] SAMPLE LEARNERS CREATED:")
        print("• Alice Johnson - Data Science/Machine Learning focus")
        print("• Bob Smith - Web Development focus") 
        print("• Carol Davis - Design/UX focus")
        
        print("\n[OK] The Minimax API error fix is working AND you now have data to test with!")
        
        return True
    else:
        print("\n[FAIL] No learners were created. Check the error messages above.")
        print("Make sure your database is accessible and the application is running properly.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)