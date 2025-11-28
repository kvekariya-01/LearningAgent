#!/usr/bin/env python3
"""
API Provider Error Diagnostic and Fix Script

This script helps diagnose and fix the "404 No allowed providers are available for the selected model" error
commonly encountered in Hugging Face Spaces deployments.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class APIProviderDiagnostic:
    def __init__(self):
        self.results = {}
        self.fixes_applied = []
        
    def check_environment_variables(self) -> Dict:
        """Check for required environment variables"""
        print("Checking Environment Variables...")
        
        required_vars = {
            'HF_API_TOKEN': 'Hugging Face API Token',
            'HUGGINGFACE_HUB_TOKEN': 'Alternative Hugging Face Token',
            'MONGO_URI': 'MongoDB Connection String',
            'MONGO_DB': 'Database Name',
            'USE_AI_FEATURES': 'AI Features Toggle',
            'USE_HUGGINGFACE_API': 'HF API Usage Toggle'
        }
        
        env_status = {}
        for var, description in required_vars.items():
            value = os.getenv(var)
            status = "[OK] Found" if value else "[MISSING] Not Found"
            env_status[var] = {
                'status': status,
                'description': description,
                'value': '***HIDDEN***' if var.endswith('TOKEN') or var == 'MONGO_URI' else value
            }
            
        self.results['environment'] = env_status
        return env_status
    
    def check_huggingface_api_availability(self) -> Dict:
        """Test Hugging Face API connectivity"""
        print("Testing Hugging Face API Connectivity...")
        
        api_status = {
            'connection': '[FAILED] Cannot connect',
            'model_access': '[FAILED] Cannot access models',
            'error_message': None
        }
        
        try:
            # Test basic API connectivity
            response = requests.get("https://huggingface.co/api/models", timeout=10)
            if response.status_code == 200:
                api_status['connection'] = '[OK] Connected to Hugging Face API'
            else:
                api_status['error_message'] = f"API returned status {response.status_code}"
                
            # Test with a common public model
            try:
                test_response = requests.get(
                    "https://huggingface.co/api/models/microsoft/DialoGPT-medium",
                    timeout=10
                )
                if test_response.status_code == 200:
                    api_status['model_access'] = '[OK] Model Access Working'
                else:
                    api_status['model_access'] = '[WARNING] Limited Access'
            except Exception as e:
                api_status['error_message'] = str(e)
                
        except Exception as e:
            api_status['error_message'] = str(e)
            
        self.results['api_status'] = api_status
        return api_status
    
    def check_model_availability(self, model_names: List[str]) -> Dict:
        """Check availability of specific models"""
        print("Checking Model Availability...")
        
        model_status = {}
        for model_name in model_names:
            try:
                response = requests.get(
                    f"https://huggingface.co/api/models/{model_name}",
                    timeout=5
                )
                if response.status_code == 200:
                    model_info = response.json()
                    model_status[model_name] = {
                        'status': '[OK] Available',
                        'downloads': model_info.get('downloads', 'N/A'),
                        'last_modified': model_info.get('lastModified', 'N/A')
                    }
                else:
                    model_status[model_name] = {
                        'status': '[FAILED] Not Available',
                        'status_code': response.status_code
                    }
            except Exception as e:
                model_status[model_name] = {
                    'status': '[ERROR] Error checking model',
                    'error': str(e)
                }
                
        self.results['models'] = model_status
        return model_status
    
    def generate_fix_script(self) -> str:
        """Generate a customized fix script based on diagnostics"""
        print("Generating Fix Script...")
        
        fix_script = '''#!/bin/bash
# Auto-generated fix script for API Provider Error

echo "Applying fixes for API Provider Error..."

'''
        
        # Add fixes based on what we found
        env_vars = self.results.get('environment', {})
        
        if env_vars.get('HF_API_TOKEN', {}).get('status') == '[MISSING] Not Found':
            fix_script += '''# Fix 1: Set Hugging Face API Token
echo "Setting Hugging Face API Token..."
read -p "Enter your Hugging Face API token: " hf_token
export HF_API_TOKEN="$hf_token"
export HUGGINGFACE_HUB_TOKEN="$hf_token"

# Add to .env file
echo "HF_API_TOKEN=$hf_token" >> .env
echo "HUGGINGFACE_HUB_TOKEN=$hf_token" >> .env

'''
            self.fixes_applied.append("Added Hugging Face API Token configuration")
        
        if env_vars.get('USE_AI_FEATURES', {}).get('status') == '[MISSING] Not Found':
            fix_script += '''# Fix 2: Configure AI Features
echo "Configuring AI features..."
echo "USE_AI_FEATURES=true" >> .env
echo "USE_HUGGINGFACE_API=true" >> .env

'''
            self.fixes_applied.append("Added AI features configuration")
        
        # Add fallback configuration
        fix_script += '''# Fix 3: Add Fallback Configuration
echo "Adding fallback configuration..."
cat >> .env << 'EOF'

# Fallback Configuration
USE_LOCAL_MODELS=true
ENABLE_FALLBACK_RECOMMENDATIONS=true
DISABLE_EXTERNAL_AI_ON_ERROR=true
EOF

echo "Fixes applied successfully!"
echo ""
echo "Next steps:"
echo "1. Restart your application"
echo "2. Test the API endpoints"
echo "3. Check logs for remaining errors"
'''
        
        return fix_script
    
    def create_fallback_code(self) -> str:
        """Create fallback code for when external AI services fail"""
        print("Creating Fallback Code...")
        
        fallback_code = '''# Fallback recommendation system
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
'''
        
        return fallback_code
    
    def generate_report(self) -> str:
        """Generate a comprehensive diagnostic report"""
        report = f"""
# API Provider Error Diagnostic Report
Generated: {datetime.now().isoformat()}

## Environment Status
"""
        
        env_vars = self.results.get('environment', {})
        for var, info in env_vars.items():
            report += f"- **{var}**: {info['status']} ({info['description']})\n"
        
        report += "\n## API Status\n"
        api_status = self.results.get('api_status', {})
        for key, value in api_status.items():
            if key != 'error_message':
                report += f"- **{key}**: {value}\n"
        
        if api_status.get('error_message'):
            report += f"- **Error**: {api_status['error_message']}\n"
        
        report += "\n## Model Availability\n"
        models = self.results.get('models', {})
        for model, info in models.items():
            report += f"- **{model}**: {info['status']}\n"
        
        report += "\n## Fixes Applied\n"
        for fix in self.fixes_applied:
            report += f"- {fix}\n"
        
        report += "\n## Recommendations\n"
        
        if env_vars.get('HF_API_TOKEN', {}).get('status') == '[MISSING] Not Found':
            report += "- HIGH PRIORITY: Add Hugging Face API Token\n"
        
        if api_status.get('connection') == '[FAILED] Cannot connect':
            report += "- HIGH PRIORITY: Check internet connectivity and API access\n"
        
        report += "- RECOMMENDED: Implement fallback recommendation system\n"
        report += "- RECOMMENDED: Add proper error handling for external APIs\n"
        report += "- RECOMMENDED: Use environment variables for configuration\n"
        
        return report

def main():
    """Main diagnostic function"""
    print("Starting API Provider Error Diagnostic...")
    print("=" * 50)
    
    diagnostic = APIProviderDiagnostic()
    
    # Run diagnostics
    diagnostic.check_environment_variables()
    diagnostic.check_huggingface_api_availability()
    
    # Test common models
    test_models = [
        "microsoft/DialoGPT-medium",
        "distilbert-base-uncased",
        "sentence-transformers/all-MiniLM-L6-v2"
    ]
    diagnostic.check_model_availability(test_models)
    
    # Generate solutions
    fix_script = diagnostic.generate_fix_script()
    fallback_code = diagnostic.create_fallback_code()
    
    # Save outputs
    try:
        with open('fix_api_error.sh', 'w') as f:
            f.write(fix_script)
        os.chmod('fix_api_error.sh', 0o755)
        print("Generated: fix_api_error.sh (executable fix script)")
    except Exception as e:
        print(f"Could not create fix script: {e}")
    
    try:
        with open('fallback_recommendations.py', 'w') as f:
            f.write(fallback_code)
        print("Generated: fallback_recommendations.py (fallback code)")
    except Exception as e:
        print(f"Could not create fallback code: {e}")
    
    # Generate report
    report = diagnostic.generate_report()
    try:
        with open('api_diagnostic_report.md', 'w') as f:
            f.write(report)
        print("Generated: api_diagnostic_report.md (detailed report)")
    except Exception as e:
        print(f"Could not create report: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnostic Complete!")
    print("\n" + report)
    
    return diagnostic

if __name__ == "__main__":
    main()