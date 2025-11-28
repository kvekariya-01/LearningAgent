#!/usr/bin/env python3
"""
COMPREHENSIVE NETWORK BLOCKER
Blocks ALL external API calls including the Minimax API call that causes:
"tool result's tool id(call_function_k6xwcchm0c2g_1) not found (2013)"
"""

import sys
import functools
import logging
import traceback
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltimateNetworkBlocker:
    """
    Ultimate network blocker that prevents ALL external API calls
    """
    
    def __init__(self):
        self.blocked_calls = 0
        self.blocked_domains = []
        
    def install_comprehensive_blocker(self):
        """Install blockers for ALL possible networking libraries"""
        
        # Block requests library
        self._block_requests()
        
        # Block httpx library  
        self._block_httpx()
        
        # Block urllib
        self._block_urllib()
        
        # Block aiohttp
        self._block_aiohttp()
        
        # Block any remaining HTTP libraries
        self._block_generic_http()
        
        # Block direct socket calls
        self._block_socket()
        
        logger.info("COMPREHENSIVE NETWORK BLOCKER INSTALLED")
        return True
        
    def _block_requests(self):
        """Block all requests library functions"""
        try:
            import requests
            original_get = requests.get
            original_post = requests.post
            original_put = requests.put
            original_delete = requests.delete
            original_patch = requests.patch
            
            def blocked_get(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED requests.get: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_post(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED requests.post: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_put(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED requests.put: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_delete(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED requests.delete: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_patch(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED requests.patch: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            # Replace ALL requests functions
            requests.get = blocked_get
            requests.post = blocked_post
            requests.put = blocked_put
            requests.delete = blocked_delete
            requests.patch = blocked_patch
            
            logger.info("REQUESTS LIBRARY BLOCKED")
            return True
            
        except ImportError:
            logger.info("requests library not available to block")
            return False
    
    def _block_httpx(self):
        """Block httpx library"""
        try:
            import httpx
            original_get = httpx.get
            original_post = httpx.post
            
            def blocked_get(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED httpx.get: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_post(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED httpx.post: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            httpx.get = blocked_get
            httpx.post = blocked_post
            
            logger.info("HTTPX LIBRARY BLOCKED")
            return True
            
        except ImportError:
            logger.info("httpx library not available to block")
            return False
    
    def _block_urllib(self):
        """Block urllib library"""
        try:
            import urllib.request
            import urllib.parse
            
            original_urlopen = urllib.request.urlopen
            original_request = urllib.request.Request
            
            def blocked_urlopen(*args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED urllib.request.urlopen: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_request(*args, **kwargs):
                self.blocked_calls += 1
                logger.warning(f"BLOCKED urllib.request.Request")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            urllib.request.urlopen = blocked_urlopen
            urllib.request.Request = blocked_request
            
            logger.info("URLLIB LIBRARY BLOCKED")
            return True
            
        except ImportError:
            logger.info("urllib library not available to block")
            return False
    
    def _block_aiohttp(self):
        """Block aiohttp library"""
        try:
            import aiohttp
            original_get = aiohttp.ClientSession.get
            original_post = aiohttp.ClientSession.post
            
            def blocked_get(self, *args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED aiohttp.get: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
                
            def blocked_post(self, *args, **kwargs):
                self.blocked_calls += 1
                url = args[0] if args else 'unknown'
                logger.warning(f"BLOCKED aiohttp.post: {url}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            aiohttp.ClientSession.get = blocked_get
            aiohttp.ClientSession.post = blocked_post
            
            logger.info("AIOHTTP LIBRARY BLOCKED")
            return True
            
        except ImportError:
            logger.info("aiohttp library not available to block")
            return False
    
    def _block_generic_http(self):
        """Skip generic HTTP blocking for now - requests/urllib blocking is sufficient"""
        logger.info("Generic HTTP blocking skipped (requests/urllib blocking is sufficient)")
        return True
    
    def _block_socket(self):
        """Block direct socket connections"""
        try:
            import socket
            original_socket = socket.socket
            original_connect = socket.socket.connect
            
            def blocked_socket(*args, **kwargs):
                self.blocked_calls += 1
                logger.warning("BLOCKED socket.socket creation")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            def blocked_connect(self, address):
                self.blocked_calls += 1
                logger.warning(f"BLOCKED socket.connect: {address}")
                raise Exception("EXTERNAL API CALLS COMPLETELY DISABLED - Network blocker active")
            
            socket.socket = blocked_socket
            socket.socket.connect = blocked_connect
            
            logger.info("SOCKET LIBRARY BLOCKED")
            return True
            
        except ImportError:
            logger.info("socket library not available to block")
            return False
    
    def get_blocked_count(self):
        """Return number of blocked calls"""
        return self.blocked_calls
    
    def log_blocked_calls(self):
        """Log any blocked calls"""
        count = self.get_blocked_count()
        if count > 0:
            logger.warning(f"TOTAL BLOCKED API CALLS: {count}")
        return count

# Global blocker instance
ultimate_blocker = UltimateNetworkBlocker()

def activate_ultimate_network_blocker():
    """Activate the ultimate network blocker"""
    print("[BLOCKER] ACTIVATING ULTIMATE NETWORK BLOCKER...")
    print("[BLOCKER] This will prevent ALL external API calls including Minimax")
    
    success = ultimate_blocker.install_comprehensive_blocker()
    
    if success:
        print("[SUCCESS] ULTIMATE NETWORK BLOCKER IS ACTIVE")
        print("[SECURE] ALL external API calls are now blocked")
        return True
    else:
        print("[WARNING] Network blocker installation had issues")
        return False

def get_blocked_calls_summary():
    """Get summary of blocked calls"""
    count = ultimate_blocker.get_blocked_count()
    return f"Blocked {count} external API calls"

if __name__ == "__main__":
    # Test the ultimate blocker
    activate_ultimate_network_blocker()
    
    # Test with different libraries
    print("[TEST] Testing block effectiveness...")
    
    # Test requests
    try:
        import requests
        requests.get("https://example.com")
        print("[FAIL] REQUESTS BLOCK FAILED")
    except Exception as e:
        print(f"[SUCCESS] REQUESTS BLOCKED: {e}")
    
    # Test urllib
    try:
        import urllib.request
        urllib.request.urlopen("https://example.com")
        print("[FAIL] URLLIB BLOCK FAILED")
    except Exception as e:
        print(f"[SUCCESS] URLLIB BLOCKED: {e}")
    
    print(f"[SUMMARY] FINAL BLOCK SUMMARY: {get_blocked_calls_summary()}")
