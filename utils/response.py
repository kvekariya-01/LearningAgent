# utils/response.py
from flask import jsonify

def success(data=None, message="OK", status=200):
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status

def error(message="Bad Request", status=400, details=None):
    payload = {"status": "error", "message": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status
