from flask import Blueprint, jsonify, request
bp = Blueprint('learner', __name__, url_prefix='/api/learner')

@bp.route('/<int:learner_id>/profile', methods=['GET'])
def profile(learner_id):
    # load from DB; here sample response
    sample = {
      "id": learner_id,
      "name": "Test Learner",
      "learning_path": [
        {"module": "Intro to Python", "status": "completed"},
        {"module": "Data Structures", "status": "in-progress"},
        {"module": "Algorithms", "status": "locked"}
      ]
    }
    return jsonify(sample)

@bp.route('/<int:learner_id>/progress', methods=['GET'])
def progress(learner_id):
    # return labels and percentages
    sample = {"labels":["Week1","Week2","Week3"], "completedPercent":[10,40,60]}
    return jsonify(sample)

@bp.route('/<int:learner_id>/recommendations', methods=['GET'])
def recommendations(learner_id):
    recs = [
      {"title":"Practice: Sorting algorithms", "reason":"low score on sorting quiz"},
      {"title":"Module: Algorithmic Thinking", "reason":"prerequisite for next module"}
    ]
    return jsonify(recs)
