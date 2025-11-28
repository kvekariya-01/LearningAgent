# app/ml/recommender.py - Simplified for Hugging Face deployment
import os
import json
import numpy as np
from utils.crud_operations import read_contents

def get_performance_level(avg_score, time_spent, difficulty):
    """
    Simple performance level classification
    """
    # Simple scoring system
    if avg_score >= 85:
        return 'high'
    elif avg_score >= 70:
        return 'medium'
    else:
        return 'low'

def calculate_match_score(content, learner_profile, performance_level):
    """
    Calculate match score for content based on learner profile and performance
    Higher score = better match.
    """
    score = 0

    # Difficulty matching
    diff_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    content_diff = diff_map.get(content.get('difficulty_level', 'intermediate'), 2)
    perf_map = {'low': 1, 'medium': 2, 'high': 3}
    perf_level = perf_map.get(performance_level, 2)

    # Prefer content at or slightly above current performance level
    if content_diff <= perf_level + 1:
        score += 10
    if content_diff == perf_level:
        score += 5

    # Learning style matching (if available)
    learner_style = learner_profile.get('learning_style', '').lower()
    content_type = content.get('content_type', '').lower()
    if learner_style in ['visual', 'auditory', 'reading'] and content_type in ['video', 'audio', 'article']:
        if (learner_style == 'visual' and content_type == 'video') or \
           (learner_style == 'auditory' and content_type == 'audio') or \
           (learner_style == 'reading' and content_type == 'article'):
            score += 5

    # Tags matching (if learner has preferences)
    learner_prefs = learner_profile.get('preferences', [])
    content_tags = content.get('tags', [])
    matching_tags = set(learner_prefs) & set(content_tags)
    score += len(matching_tags) * 2

    return score

def get_top_content_recommendations(learner_profile, performance_level, top_n=3):
    """
    Fetch top N content items by match_score.
    """
    contents = read_contents()
    if not contents:
        return []

    # Calculate match scores
    scored_contents = []
    for content in contents:
        match_score = calculate_match_score(content, learner_profile, performance_level)
        scored_contents.append((content, match_score))

    # Sort by match_score descending
    scored_contents.sort(key=lambda x: x[1], reverse=True)

    # Return top N
    return scored_contents[:top_n]

def hybrid_recommend(learner_id, learner_profile, recent_scores=None):
    """
    Hybrid recommender: Simple rule-based recommendations
    Returns recommendations dict with ML-based and rule-based suggestions.
    """
    if recent_scores is None:
        recent_scores = {}

    # Get features
    avg_score = recent_scores.get('avg_score', 70)
    time_spent = recent_scores.get('time_spent', 50)
    difficulty = recent_scores.get('difficulty', 2)  # 1=beginner, 2=intermediate, 3=advanced

    # Get performance level
    performance_level = get_performance_level(avg_score, time_spent, difficulty)

    # Get top content recommendations
    top_contents = get_top_content_recommendations(learner_profile, performance_level, top_n=3)

    # Rule-based recommendations
    rule_recs = recommend_by_rules(learner_profile, recent_scores)

    # Combine results
    recommendations = {
        'learner_id': learner_id,
        'performance_level': performance_level,
        'ml_recommendations': [
            {
                'content_id': content['id'],
                'title': content['title'],
                'match_score': score,
                'reason': f"Matches {performance_level} performance level"
            } for content, score in top_contents
        ],
        'rule_recommendations': rule_recs,
        'features_used': {
            'avg_score': avg_score,
            'time_spent': time_spent,
            'difficulty': difficulty
        }
    }

    return recommendations

def recommend_for_new_learner(learner_profile):
    """
    Fallback recommendations for new learners with no activity data.
    """
    contents = read_contents()
    if not contents:
        return []

    # Recommend beginner content
    beginner_contents = [c for c in contents if c.get('difficulty_level') == 'beginner']
    if beginner_contents:
        return beginner_contents[:3]

    # If no beginner content, recommend first 3
    return contents[:3]

def recommend_by_rules(profile, recent_scores):
    """
    Rule-based recommendations
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
    
    return recs