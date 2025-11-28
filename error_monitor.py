#!/usr/bin/env python3
"""
COMPREHENSIVE ERROR MONITOR
Monitors for any Minimax API errors and logs them
"""
import os
import time
import re
from datetime import datetime

def monitor_minimax_errors():
    """Monitor for Minimax API errors specifically"""
    print("Starting comprehensive error monitor...")
    
    error_patterns = [
        r"Minimax error.*2013",
        r"tool.*id.*not found", 
        r"call_function.*not found",
        r"invalid params.*tool",
        r"API Request Failed.*Minimax",
        r"external.*api.*call",
        r"network.*error"
    ]
    
    blocked_count = 0
    
    while True:
        try:
            # Check for any log files
            log_files = ["app.log", "streamlit.log", "minimax_error.log"]
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            content = f.read()
                        
                        for pattern in error_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f"[ALERT] [{timestamp}] MINIMAX ERROR DETECTED:")
                                for match in matches:
                                    print(f"   ERROR: {match}")
                                print(f"   SOURCE: {log_file}")
                                print()
                                
                    except Exception as e:
                        print(f"WARNING: Error reading {log_file}: {e}")
            
            # Check if network blocker is active
            try:
                import ultimate_network_blocker
                blocked = ultimate_network_blocker.ultimate_blocker.get_blocked_count()
                if blocked > blocked_count:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_blocks = blocked - blocked_count
                    print(f"[BLOCK] [{timestamp}] Blocked {new_blocks} external API calls")
                    blocked_count = blocked
            except ImportError:
                pass
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("
STOPPED: Error monitoring stopped")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_minimax_errors()
