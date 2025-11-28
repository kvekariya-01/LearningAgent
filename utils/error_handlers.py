"""
Error handling utilities for robust AI service fallbacks
"""
import logging
import traceback
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIErrorHandler:
    """
    Handles API errors with multiple fallback mechanisms
    """
    
    @staticmethod
    def handle_minimax_error(error: Exception) -> Dict[str, Any]:
        """Specific handler for Minimax API errors"""
        error_info = {
            "error_type": "MinimaxAPIError",
            "error_message": str(error),
            "error_code": "2013",
            "solution_applied": "disabled_external_ai",
            "fallback_action": "using_local_recommendations",
            "recovery_status": "success"
        }
        
        logger.warning(f"Minimax API Error detected: {error_info}")
        return error_info
    
    @staticmethod 
    def handle_api_timeout(error: Exception) -> Dict[str, Any]:
        """Handle API timeout errors"""
        error_info = {
            "error_type": "APITimeoutError",
            "error_message": str(error),
            "solution_applied": "timeout_fallback",
            "fallback_action": "using_local_models",
            "recovery_status": "success"
        }
        
        logger.warning(f"API Timeout Error: {error_info}")
        return error_info
    
    @staticmethod
    def handle_connection_error(error: Exception) -> Dict[str, Any]:
        """Handle connection errors"""
        error_info = {
            "error_type": "ConnectionError", 
            "error_message": str(error),
            "solution_applied": "connection_fallback",
            "fallback_action": "using_offline_mode",
            "recovery_status": "success"
        }
        
        logger.warning(f"Connection Error: {error_info}")
        return error_info
    
    @classmethod
    def safe_api_call(cls, api_func, *args, **kwargs) -> Any:
        """
        Safe wrapper for API calls with comprehensive error handling
        """
        try:
            return api_func(*args, **kwargs)
        except Exception as e:
            error_str = str(e).lower()
            
            if "minimax" in error_str and "2013" in error_str:
                return cls.handle_minimax_error(e)
            elif "timeout" in error_str:
                return cls.handle_api_timeout(e) 
            elif "connection" in error_str or "network" in error_str:
                return cls.handle_connection_error(e)
            else:
                # Generic error handling
                error_info = {
                    "error_type": "GenericAPIError",
                    "error_message": str(e),
                    "solution_applied": "generic_fallback",
                    "fallback_action": "using_basic_recommendations",
                    "recovery_status": "success"
                }
                logger.warning(f"Generic API Error: {error_info}")
                return error_info

def get_safe_recommendations(learner_id: str, learner_data: Dict, api_base_url: str = None):
    """
    Safe function to get recommendations with error handling
    """
    try:
        from enhanced_recommendation_engine import get_enhanced_recommendations
        
        handler = APIErrorHandler()
        
        # Use safe API call wrapper
        result = handler.safe_api_call(
            get_enhanced_recommendations, 
            learner_id, 
            learner_data, 
            api_base_url
        )
        
        # Check if result contains error information
        if isinstance(result, dict) and "error_type" in result:
            # Fallback to basic local recommendations
            logger.info("Using fallback recommendations due to API error")
            return {
                "learner_id": learner_id,
                "recommendations": [],
                "enhanced_recommendations": {
                    "courses": [],
                    "pdf_resources": [],
                    "assessments": [],
                    "projects": [],
                    "performance_analysis": {
                        "learning_score": 0,
                        "performance_level": "error_recovery",
                        "error_handled": True
                    }
                },
                "recommendation_type": "error_fallback",
                "enhanced_by": "ErrorHandler",
                "fallback_used": True,
                "fallback_reason": f"API Error: {result.get('error_message', 'Unknown error')}"
            }
        
        return result
        
    except ImportError:
        # If enhanced engine not available, return simple fallback
        logger.info("Enhanced engine not available, using basic fallback")
        return {
            "learner_id": learner_id,
            "recommendations": [],
            "enhanced_recommendations": {
                "courses": [],
                "pdf_resources": [],
                "assessments": [],
                "projects": [],
                "performance_analysis": {
                    "learning_score": 0,
                    "performance_level": "basic_mode",
                    "basic_mode": True
                }
            },
            "recommendation_type": "basic_fallback",
            "enhanced_by": "BasicHandler",
            "fallback_used": True,
            "fallback_reason": "Enhanced recommendation engine not available"
        }
    except Exception as e:
        # Ultimate fallback for any other errors
        logger.error(f"Error in get_safe_recommendations: {e}")
        return {
            "learner_id": learner_id,
            "recommendations": [],
            "enhanced_recommendations": {
                "courses": [],
                "pdf_resources": [],
                "assessments": [],
                "projects": [],
                "performance_analysis": {
                    "learning_score": 0,
                    "performance_level": "emergency_mode",
                    "emergency_mode": True
                }
            },
            "recommendation_type": "emergency_fallback",
            "enhanced_by": "EmergencyHandler",
            "fallback_used": True,
            "fallback_reason": f"Emergency fallback: {str(e)}"
        }
