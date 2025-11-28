# app/ml/rules.py - Simplified for Hugging Face deployment
def recommend_by_rules(profile, recent_scores):
    """
    Rule-based recommendations based on learner profile and recent scores
    """
    recs = []
    
    # Algorithm performance check
    avg_score = recent_scores.get('avg_score', 100)
    if avg_score < 50:
        recs.append({"title": "Algorithm Basics", "reason": "Low score in algorithms"})
    
    # Study time check
    time_spent = recent_scores.get('time_spent', 0)
    if time_spent > 180:  # 3 hours
        recs.append({"title": "Take a break", "reason": "Long study session detected"})
    
    # Learning style check
    learning_style = profile.get('learning_style', '')
    if learning_style == 'visual':
        recs.append({"title": "Visual Learning Resources", "reason": "Matches visual learning style"})
    elif learning_style == 'auditory':
        recs.append({"title": "Audio Learning Materials", "reason": "Matches auditory learning style"})
    
    # Activity frequency check
    if recent_scores.get('activity_count', 0) < 3:
        recs.append({"title": "Increase Activity", "reason": "Need more practice sessions"})
    
    return recs
