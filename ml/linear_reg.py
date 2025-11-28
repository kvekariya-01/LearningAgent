# app/ml/linear_reg.py - Simplified for Hugging Face deployment
import numpy as np

def predict_completion_time(avg_score, time_spent, difficulty):
    """
    Simple completion time prediction without external model dependencies
    Uses basic linear relationship based on score, time spent, and difficulty
    """
    # Base completion time calculation
    base_time = time_spent * 2
    
    # Adjust based on score (higher score = faster completion)
    score_factor = max(0.5, 1.5 - (avg_score / 100))
    
    # Adjust based on difficulty (higher difficulty = more time needed)
    difficulty_factor = 1 + (difficulty - 1) * 0.5
    
    predicted_time = base_time * score_factor * difficulty_factor
    
    return round(predicted_time, 2)

# Legacy function for compatibility
def train_linreg(X, y):
    """
    Simplified training function - for compatibility
    Returns a simple prediction function
    """
    return lambda x: np.mean(y)  # Return mean as simple predictor