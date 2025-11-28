# app/ml/progress_model.py - Simplified for Hugging Face deployment
def evaluate_progress(hours_studied, modules_completed, assignment_score):
    """
    Evaluate learner progress based on activity metrics
    """
    if hours_studied < 5:
        study_feedback = "You should increase your study time."
    else:
        study_feedback = "Great job maintaining study hours!"

    if modules_completed < 3:
        module_feedback = "Try to complete more modules."
    else:
        module_feedback = "Good progress on modules!"

    if assignment_score < 50:
        score_feedback = "You need more practice on assignments."
    elif assignment_score < 80:
        score_feedback = "You're doing well, keep improving!"
    else:
        score_feedback = "Excellent performance!"

    progress_percentage = (modules_completed * 10) + (assignment_score * 0.5)
    if progress_percentage > 100:
        progress_percentage = 100

    return {
        "progress": round(progress_percentage, 2),
        "study_feedback": study_feedback,
        "module_feedback": module_feedback,
        "score_feedback": score_feedback
    }
