#!/usr/bin/env python3
"""
Enhanced Learning Agent - Complete System Runner
This script starts the enhanced API server and Streamlit application
"""

import os
import sys
import subprocess
import time
import threading
import signal
import json
from datetime import datetime

class EnhancedSystemRunner:
    """Manages the enhanced learning system components"""
    
    def __init__(self):
        self.api_process = None
        self.streamlit_process = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_port = 5001
        self.streamlit_port = 8502
        
    def check_dependencies(self):
        """Check if all required files exist"""
        required_files = [
            "enhanced_flask_api.py",
            "enhanced_streamlit_app.py", 
            "enhanced_scoring_system.py",
            "advanced_recommendation_engine.py",
            "comprehensive_system_test.py",
            "config/db_config.py",
            "models/learner.py",
            "utils/crud_operations.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(self.base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print("[FAIL] Missing required files:")
            for file_path in missing_files:
                print(f"   • {file_path}")
            return False
        
        print("[OK] All required files found")
        return True
    
    def install_dependencies(self):
        """Install required Python dependencies"""
        print("📦 Installing dependencies...")
        
        requirements = [
            "flask",
            "flask-cors", 
            "pydantic",
            "streamlit",
            "requests",
            "pandas",
            "python-dotenv"
        ]
        
        for package in requirements:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[OK] {package} installed")
            except subprocess.CalledProcessError:
                print(f"[WARNING] Failed to install {package}, continuing...")
    
    def start_api_server(self):
        """Start the enhanced Flask API server"""
        print(f"[START] Starting Enhanced API Server on port {self.api_port}...")
        
        try:
            self.api_process = subprocess.Popen([
                sys.executable, "enhanced_flask_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            if self.api_process.poll() is None:
                print(f"[OK] Enhanced API Server started successfully (PID: {self.api_process.pid})")
                return True
            else:
                print("[FAIL] API Server failed to start")
                return False
                
        except Exception as e:
            print(f"[FAIL] Failed to start API Server: {str(e)}")
            return False
    
    def start_streamlit_app(self):
        """Start the enhanced Streamlit application"""
        print(f"[ART] Starting Enhanced Streamlit App on port {self.streamlit_port}...")
        
        try:
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "enhanced_streamlit_app.py",
                "--server.port", str(self.streamlit_port),
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment for app to start
            time.sleep(5)
            
            if self.streamlit_process.poll() is None:
                print(f"[OK] Enhanced Streamlit App started successfully (PID: {self.streamlit_process.pid})")
                return True
            else:
                print("[FAIL] Streamlit App failed to start")
                return False
                
        except Exception as e:
            print(f"[FAIL] Failed to start Streamlit App: {str(e)}")
            return False
    
    def test_api_health(self):
        """Test if the API is responding"""
        import requests
        
        print("[SEARCH] Testing API health...")
        
        try:
            response = requests.get(f"http://localhost:{self.api_port}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] API is healthy (v{data.get('version', 'unknown')})")
                return True
            else:
                print(f"[FAIL] API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] API health check failed: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run the comprehensive test suite"""
        print("🧪 Running Comprehensive System Tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "comprehensive_system_test.py",
                "--api-url", f"http://localhost:{self.api_port}",
                "--save-results"
            ], capture_output=True, text=True, timeout=120)
            
            print("Test Output:")
            print("=" * 50)
            print(result.stdout)
            
            if result.returncode == 0:
                print("[OK] All tests passed!")
                return True
            else:
                print("[FAIL] Some tests failed!")
                print("Error Output:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("[FAIL] Tests timed out")
            return False
        except Exception as e:
            print(f"[FAIL] Test execution failed: {str(e)}")
            return False
    
    def show_system_info(self):
        """Display system information and URLs"""
        print("\n" + "=" * 60)
        print("[EDU] ENHANCED LEARNING AGENT - SYSTEM INFORMATION")
        print("=" * 60)
        
        print(f"[STATS] Enhanced API Server: http://localhost:{self.api_port}")
        print(f"[ART] Enhanced Streamlit App: http://localhost:{self.streamlit_port}")
        print(f"🏥 API Health Check: http://localhost:{self.api_port}/api/health")
        print(f"[BOOK] Course Catalog: http://localhost:{self.api_port}/api/courses")
        print(f"[GROWTH] Learner Analytics: http://localhost:{self.api_port}/api/analytics/learners")
        
        print("\n[START] NEW FEATURES:")
        print("[OK] Advanced Multi-Component Scoring System")
        print("[OK] AI-Powered Personalized Course Recommendations") 
        print("[OK] Structured Learning Path Generation")
        print("[OK] Comprehensive Performance Analytics")
        print("[OK] Batch Operations Support")
        print("[OK] Real-time Scoring and Insights")
        
        print("\n[LIST] AVAILABLE API ENDPOINTS:")
        endpoints = [
            "GET /api/health - System health check",
            "GET /api/learner/<id>/score - Comprehensive learner scoring",
            "GET /api/learner/<id>/recommendations - Enhanced recommendations", 
            "GET /api/learner/<id>/learning-path - Personalized learning paths",
            "GET /api/analytics/learners - System-wide learner analytics",
            "GET /api/analytics/performance-insights - Performance insights",
            "GET /api/courses - Complete course catalog",
            "POST /api/batch/calculate-scores - Batch score calculation",
            "POST /api/batch/generate-recommendations - Batch recommendations"
        ]
        
        for endpoint in endpoints:
            print(f"   • {endpoint}")
    
    def cleanup(self):
        """Clean up running processes"""
        print("\n🧹 Cleaning up processes...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("[OK] API Server stopped")
            except:
                self.api_process.kill()
                print("[WARNING] API Server force stopped")
        
        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
                print("[OK] Streamlit App stopped")
            except:
                self.streamlit_process.kill()
                print("[WARNING] Streamlit App force stopped")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"\n[WARNING] Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

def main():
    """Main execution function"""
    print("Enhanced Learning Agent - System Launcher")
    print("=" * 60)
    
    runner = EnhancedSystemRunner()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    try:
        # Check dependencies
        if not runner.check_dependencies():
            print("[FAIL] Dependency check failed. Please ensure all required files are present.")
            return 1
        
        # Install dependencies
        runner.install_dependencies()
        
        # Start API server
        if not runner.start_api_server():
            print("[FAIL] Failed to start API server. Exiting.")
            return 1
        
        # Wait for API to be ready
        print("⏳ Waiting for API server to be ready...")
        for i in range(10):
            time.sleep(1)
            if runner.test_api_health():
                break
            print(f"   Attempt {i+1}/10...")
        else:
            print("[FAIL] API server not responding after 10 seconds")
            return 1
        
        # Start Streamlit app
        if not runner.start_streamlit_app():
            print("[FAIL] Failed to start Streamlit app. API server will continue running.")
        
        # Run tests if API is working
        test_success = runner.run_comprehensive_tests()
        
        # Show system information
        runner.show_system_info()
        
        if test_success:
            print("\n[SUCCESS] SYSTEM READY! All tests passed successfully.")
        else:
            print("\n[WARNING] SYSTEM RUNNING! Some tests failed, but system is operational.")
        
        print("\n[TIP] USAGE INSTRUCTIONS:")
        print("1. Open your browser and go to the Streamlit URL above")
        print("2. Register learners and log their activities")
        print("3. View score analytics and get recommendations")
        print("4. Generate learning paths for structured learning")
        print("5. Monitor performance insights in the Analytics section")
        
        print(f"\n[STATS] API Documentation:")
        print(f"   Base URL: http://localhost:{runner.api_port}")
        print(f"   Health: http://localhost:{runner.api_port}/api/health")
        print(f"   Documentation: Open Streamlit app → Settings section")
        
        print("\n" + "=" * 60)
        print("[TARGET] Enhanced Learning Agent is now running!")
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if runner.api_process and runner.api_process.poll() is not None:
                    print("[FAIL] API server stopped unexpectedly")
                    break
                if runner.streamlit_process and runner.streamlit_process.poll() is not None:
                    print("[WARNING] Streamlit app stopped unexpectedly")
                    # Don't break here, keep API running
        except KeyboardInterrupt:
            print("\n👋 Shutting down gracefully...")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 System launcher failed: {str(e)}")
        return 1
    finally:
        runner.cleanup()

if __name__ == "__main__":
    sys.exit(main())