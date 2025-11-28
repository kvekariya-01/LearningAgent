#!/usr/bin/env python3
"""
DAY 4 - Frontend Integration Launcher
Easy launcher for both Learner and Instructor dashboards with integrated API services
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

def print_banner():
    """Print the DAY 4 banner"""
    print("=" * 80)
    print("🎓 LEARNING AGENT - DAY 4 FRONTEND INTEGRATION")
    print("=" * 80)
    print("📊 Learner Dashboard: Personalized learning paths and progress tracking")
    print("👨‍🏫 Instructor Dashboard: Analytics overview and at-risk learner alerts")
    print("🔗 API Integration: Enhanced Flask API with loading states & error handling")
    print("=" * 80)
    print()

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'requests',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def start_api_server():
    """Start the Flask API server in background"""
    print("🚀 Starting Enhanced Flask API Server...")
    try:
        # Start the enhanced Flask API
        process = subprocess.Popen([
            sys.executable, "enhanced_flask_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for API server to start...")
        time.sleep(3)  # Give server time to start
        
        # Test if server is responsive
        import requests
        try:
            response = requests.get("http://localhost:5001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API Server started successfully on http://localhost:5001")
                return process
            else:
                print("⚠️ API Server started but health check failed")
                return process
        except requests.exceptions.RequestException:
            print("⚠️ API Server may not be responding (this is normal for first startup)")
            return process
            
    except FileNotFoundError:
        print("❌ enhanced_flask_api.py not found. Make sure you're in the correct directory.")
        return None
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_learner_dashboard():
    """Start the Learner Dashboard"""
    print("🎓 Starting Learner Dashboard...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "day4_learner_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Learner Dashboard stopped")
    except Exception as e:
        print(f"❌ Failed to start Learner Dashboard: {e}")

def start_instructor_dashboard():
    """Start the Instructor Dashboard"""
    print("👨‍🏫 Starting Instructor Dashboard...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "day4_instructor_dashboard.py", 
            "--server.port", "8502",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Instructor Dashboard stopped")
    except Exception as e:
        print(f"❌ Failed to start Instructor Dashboard: {e}")

def run_dashboard_choice():
    """Interactive dashboard selection"""
    while True:
        print("\n🎯 Select Dashboard to Launch:")
        print("1. 🎓 Learner Dashboard (http://localhost:8501)")
        print("2. 👨‍🏫 Instructor Dashboard (http://localhost:8502)")
        print("3. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            start_learner_dashboard()
            break
        elif choice == "2":
            start_instructor_dashboard()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Start API server
    api_process = start_api_server()
    
    try:
        # Offer dashboard selection
        run_dashboard_choice()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        # Cleanup
        if api_process:
            print("\n🔄 Stopping API server...")
            try:
                api_process.terminate()
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()
            print("✅ API server stopped")

if __name__ == "__main__":
    main()