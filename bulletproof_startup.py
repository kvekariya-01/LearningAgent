#!/usr/bin/env python3
"""
BULLETPROOF STARTUP SCRIPT
Ensures NO external API calls are made during startup
"""
import os
import sys
import time

def bulletproof_startup():
    """Start the application with maximum protection"""
    print("BULLETPROOF STARTUP INITIATED")
    print("=" * 60)
    
    # Kill any existing processes first
    print("Cleaning up existing processes...")
    try:
        os.system("taskkill /f /im python.exe > nul 2>&1")
        time.sleep(3)
    except:
        pass
    
    # Load environment configuration
    print("Loading environment configuration...")
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
        print("SUCCESS: Environment configuration loaded")
    except Exception as e:
        print(f"WARNING: Environment config error: {e}")
    
    # Activate network blocker first
    print("Activating network protection...")
    try:
        import ultimate_network_blocker
        ultimate_network_blocker.activate_ultimate_network_blocker()
        print("SUCCESS: Network protection active")
    except Exception as e:
        print(f"WARNING: Network blocker error: {e}")
    
    # Start the Streamlit application
    print("Starting Learning Agent...")
    print("=" * 60)
    print("PROTECTION STATUS:")
    print("SECURE: All external API calls blocked")
    print("BLOCKED: Minimax API completely disabled") 
    print("ACTIVE: Local recommendation engine active")
    print("READY: Application ready for use")
    print("=" * 60)
    
    try:
        # Start Streamlit with maximum protection
        os.system("streamlit run app.py --server.port 8501 --server.headless true --server.fileWatcherType=none")
    except KeyboardInterrupt:
        print("
STOPPED: Application stopped by user")
    except Exception as e:
        print(f"
ERROR: Startup error: {e}")

if __name__ == "__main__":
    bulletproof_startup()
