#!/usr/bin/env python3
"""
Simple web server to serve the scoring dashboard
"""

from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Serve the scoring dashboard"""
    try:
        with open('scoring_dashboard.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Dashboard file not found. Make sure scoring_dashboard.html is in the current directory.", 404

@app.route('/dashboard')
def dashboard_route():
    """Alternative route for the dashboard"""
    return dashboard()

@app.route('/api/health')
def health_check():
    """Health check for the web server"""
    return {
        "status": "healthy",
        "service": "scoring-dashboard",
        "version": "1.0.0"
    }

if __name__ == '__main__':
    print("Starting Scoring Dashboard Server...")
    print("Dashboard will be available at: http://localhost:8080")
    print("Direct dashboard link: http://localhost:8080/")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=False
    )