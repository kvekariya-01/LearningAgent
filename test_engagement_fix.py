#!/usr/bin/env python3
"""
Test script to verify Engagement model fix
==========================================
This script tests that the Engagement model works correctly with .to_dict() method.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.engagement import Engagement, InteractionMetrics, EngagementPattern

def test_engagement_model():
    """Test that Engagement model works correctly"""
    print("Testing Engagement model...")
    
    try:
        # Create an Engagement object
        engagement = Engagement(
            learner_id="test_learner_123",
            content_id="test_content_456", 
            course_id="test_course_789",
            engagement_type="view",
            duration=45.5,
            score=85.0,
            feedback="Great content!",
            metadata={"test_field": "test_value"}
        )
        
        print(f"[OK] Engagement object created successfully")
        print(f"   ID: {engagement.id}")
        print(f"   Learner ID: {engagement.learner_id}")
        print(f"   Content ID: {engagement.content_id}")
        print(f"   Course ID: {engagement.course_id}")
        print(f"   Type: {engagement.engagement_type}")
        
        # Test to_dict() method
        engagement_dict = engagement.to_dict()
        print(f"[OK] to_dict() method works correctly")
        print(f"   Dict keys: {list(engagement_dict.keys())}")
        
        # Verify _id field is added
        if "_id" in engagement_dict:
            print(f"[OK] _id field added correctly")
        else:
            print(f"[ERROR] _id field missing")
            return False
            
        # Verify all required fields are present
        required_fields = ['id', 'learner_id', 'content_id', 'course_id', 'engagement_type', 
                          'duration', 'score', 'feedback', 'interaction_metrics', 
                          'engagement_pattern', 'metadata', 'timestamp', '_id']
        
        missing_fields = [field for field in required_fields if field not in engagement_dict]
        if missing_fields:
            print(f"[ERROR] Missing fields: {missing_fields}")
            return False
        else:
            print(f"[OK] All required fields present")
            
        # Test that to_dict returns a proper dictionary
        if isinstance(engagement_dict, dict):
            print(f"[OK] Returns proper dictionary type")
        else:
            print(f"[ERROR] Does not return dictionary")
            return False
            
        print("\n[SUCCESS] All tests passed! Engagement model fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing Engagement model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_interaction_metrics():
    """Test InteractionMetrics model"""
    print("\nTesting InteractionMetrics model...")
    
    try:
        # Create InteractionMetrics
        metrics = InteractionMetrics(
            click_count=10,
            scroll_depth=0.75,
            pause_count=2,
            replay_count=1,
            completion_percentage=0.85,
            attention_span=120.5,
            interaction_frequency=5.2,
            device_type="desktop",
            browser_type="chrome"
        )
        
        print(f"[OK] InteractionMetrics created successfully")
        print(f"   Click count: {metrics.click_count}")
        print(f"   Scroll depth: {metrics.scroll_depth}")
        print(f"   Completion: {metrics.completion_percentage}")
        
        # Test model_dump()
        metrics_dict = metrics.model_dump()
        print(f"[OK] model_dump() works correctly")
        print(f"   Dict keys: {list(metrics_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing InteractionMetrics: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_engagement_pattern():
    """Test EngagementPattern model"""
    print("\nTesting EngagementPattern model...")
    
    try:
        # Create EngagementPattern
        from datetime import datetime, timezone
        
        pattern = EngagementPattern(
            learning_session_id="session_123",
            engagement_frequency_score=0.8,
            consistency_score=0.75,
            engagement_streak=5,
            preferred_engagement_times=["morning", "evening"],
            engagement_method="guided"
        )
        
        print(f"[OK] EngagementPattern created successfully")
        print(f"   Session ID: {pattern.learning_session_id}")
        print(f"   Frequency score: {pattern.engagement_frequency_score}")
        print(f"   Streak: {pattern.engagement_streak}")
        
        # Test model_dump()
        pattern_dict = pattern.model_dump()
        print(f"[OK] model_dump() works correctly")
        print(f"   Dict keys: {list(pattern_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing EngagementPattern: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("ENGAGEMENT MODEL FIX TEST")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test all components
    all_tests_passed &= test_engagement_model()
    all_tests_passed &= test_interaction_metrics()
    all_tests_passed &= test_engagement_pattern()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("The Engagement model fix is working correctly.")
        print("You should no longer see the 'Engagement object has no attribute to_dict' error.")
    else:
        print("[ERROR] SOME TESTS FAILED!")
        print("Please check the errors above.")
    print("=" * 60)
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)