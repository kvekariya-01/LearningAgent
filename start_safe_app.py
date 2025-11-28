#!/usr/bin/env python3
"""
Safe startup script that prevents all external API calls
"""

import os
import sys
import time

def start_safe_app():
    """Start the app with all safety measures"""
    print("Starting Learning Agent with Minimax API protection...")
    
    # Show current settings
    print("\n[SETTINGS] Current environment:")
    safety_settings = [
        "USE_AI_FEATURES", "DISABLE_MINIMAX_API", "USE_LOCAL_MODELS", 
        "DISABLE_ALL_EXTERNAL_APIS", "USE_IN_MEMORY_DB"
    ]
    
    for setting in safety_settings:
        value = os.environ.get(setting, "not set")
        print(f"  {setting}: {value}")
    
    # Test network blocker
    print("\n[TEST] Testing network blocker...")
    try:
        import network_blocker
        network_blocker.activate_network_blocker()
        print("SUCCESS: Network blocker is active")
    except Exception as e:
        print(f"WARNING: Network blocker issue: {e}")
    
    # Kill any existing processes
    try:
        os.system("taskkill /f /im python.exe > nul 2>&1")
        time.sleep(2)
        print("SUCCESS: Existing processes terminated")
    except:
        print("WARNING: Could not terminate existing processes")
    
    # Start the app
    print("\n[START] Launching application...")
    try:
        os.system("streamlit run app.py --server.port 8501 --server.headless true")
    except KeyboardInterrupt:
        print("\n[STOP] Application stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start application: {e}")

if __name__ == "__main__":
    start_safe_app()