# API Testing Script
import requests
import json

# Your Hugging Face Space URL (update this with your actual space name)
SPACE_URL = "https://karan-01-learningagent.hf.space"  # Update with your actual space name

def test_api():
    print("🧪 Testing Learning Agent API")
    print("=" * 50)
    
    try:
        # Test 1: Health Check
        print("1. Testing Health Check...")
        response = requests.get(f"{SPACE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test 2: Register Learner
        print("2. Testing Learner Registration...")
        learner_data = {
            "name": "Test User",
            "age": 25,
            "gender": "male",
            "learning_style": "visual",
            "preferences": ["algorithms", "data structures"]
        }
        response = requests.post(f"{SPACE_URL}/api/learner/register", json=learner_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            learner_id = response.json().get("id")
            print(f"Created Learner ID: {learner_id}")
            print()
            
            # Test 3: Log Activity
            print("3. Testing Activity Logging...")
            activity_data = {
                "activity_type": "module_completed",
                "duration": 30.5,
                "score": 85
            }
            response = requests.post(f"{SPACE_URL}/api/learner/{learner_id}/activity", json=activity_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            print()
            
            # Test 4: Get Recommendations
            print("4. Testing Recommendations...")
            response = requests.get(f"{SPACE_URL}/api/learner/{learner_id}/recommendations")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            print()
        
        # Test 5: Get All Learners
        print("5. Testing Get All Learners...")
        response = requests.get(f"{SPACE_URL}/api/learners")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        print("[OK] API Testing Complete!")
        
    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection Error: Make sure your Hugging Face Space is deployed and running")
        print(f"Expected URL format: https://[username]-[spacename].hf.space")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    test_api()