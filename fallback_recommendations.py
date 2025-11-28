# Fallback recommendation system
def get_local_recommendations(learner_data):
    """
    Fallback recommendation system when external AI services are unavailable
    """
    import random
    
    # Basic rule-based recommendations
    recommendations = []
    
    # Learning style based recommendations
    learning_style = learner_data.get('learning_style', 'Mixed')
    preferences = learner_data.get('preferences', [])
    
    # Style-based content mapping
    style_content = {
        'Visual': ['videos', 'infographics', 'diagrams', 'animations'],
        'Auditory': ['podcasts', 'lectures', 'discussions', 'audiobooks'],
        'Kinesthetic': ['hands-on', 'projects', 'labs', 'interactive'],
        'Reading/Writing': ['articles', 'books', 'essays', 'written exercises'],
        'Mixed': ['videos', 'articles', 'interactive', 'projects']
    }
    
    # Generate recommendations based on preferences
    for preference in preferences[:3]:  # Top 3 preferences
        recommendations.append({
            'title': f'Introduction to {preference}',
            'content_type': random.choice(style_content.get(learning_style, style_content['Mixed'])),
            'difficulty': 'beginner',
            'duration': random.randint(30, 120),
            'confidence': 0.7,
            'reason': f'Matches your interest in {preference} and {learning_style} learning style'
        })
    
    return recommendations

# Integration function
def safe_get_recommendations(learner_id, api_base_url="http://localhost:5000"):
    """Safe recommendation getter with fallback"""
    try:
        import requests
        response = requests.get(f"{api_base_url}/api/learner/{learner_id}/recommendations", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned {response.status_code}")
    except Exception as e:
        print(f"WARNING: External API failed: {e}")
        print("Using local fallback recommendations...")
        
        # Get learner data
        try:
            from utils.crud_operations import read_learner
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


            learner_data = read_learner(learner_id)
            
            if learner_data:
                return {
                    'learner_id': learner_id,
                    'recommendations': get_local_recommendations(learner_data),
                    'recommendation_type': 'fallback',
                    'fallback': True,
                    'fallback_reason': 'External AI service unavailable'
                }
            else:
                return {'error': 'Learner not found'}
        except ImportError:
            # If we can't import, return basic fallback
            return {
                'learner_id': learner_id,
                'recommendations': [
                    {
                        'title': 'Python Fundamentals',
                        'content_type': 'video',
                        'difficulty': 'beginner',
                        'duration': 120,
                        'confidence': 0.5,
                        'reason': 'General programming foundation'
                    }
                ],
                'recommendation_type': 'basic_fallback'
            }
