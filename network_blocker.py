#!/usr/bin/env python3
"""
Network Blocker - Prevents external API calls to avoid errors
This module blocks network calls to external services to prevent API errors
"""

import socket
import urllib.request
import urllib.parse
import urllib.error
import requests
import httplib2
import ssl

# Store original functions for potential restoration
original_socket_connect = socket.socket.connect
original_urlopen = urllib.request.urlopen
original_urlretrieve = urllib.request.urlretrieve
original_getaddrinfo = socket.getaddrinfo

def block_network_call(*args, **kwargs):
    """Block all network calls by raising an exception"""
    raise ConnectionError("Network calls are blocked to prevent API errors")

def activate_network_blocker():
    """Activate the network blocker to prevent external API calls"""
    
    # Block socket connections
    socket.socket.connect = block_network_call
    socket.socket.create_connection = block_network_call
    
    # Block urllib requests
    urllib.request.urlopen = block_network_call
    urllib.request.urlretrieve = block_network_call
    
    # Block requests library
    if hasattr(requests, 'get'):
        requests.get = lambda *args, **kwargs: _blocked_response("GET requests blocked")
        requests.post = lambda *args, **kwargs: _blocked_response("POST requests blocked")
        requests.put = lambda *args, **kwargs: _blocked_response("PUT requests blocked")
        requests.delete = lambda *args, **kwargs: _blocked_response("DELETE requests blocked")
    
    # Block httplib2
    if hasattr(httplib2, 'Http'):
        httplib2.Http.request = lambda *args, **kwargs: _blocked_response("HTTP requests blocked")
    
    print("Network protection active - External API calls blocked")

def _blocked_response(method):
    """Return a blocked response object"""
    class BlockedResponse:
        def __init__(self, method):
            self.method = method
            self.status = 403
            self.reason = "Network calls blocked"
            
        def read(self):
            return f'{{"error": "{self.method}", "blocked": true}}'.encode()
        
        def getheader(self, name, default=None):
            return default
    
    return BlockedResponse(method)

def deactivate_network_blocker():
    """Deactivate the network blocker (restore original functions)"""
    
    # Restore original functions
    socket.socket.connect = original_socket_connect
    urllib.request.urlopen = original_urlopen
    urllib.request.urlretrieve = original_urlretrieve
    
    print("Network protection deactivated")

# Auto-activate when imported
if __name__ != "__main__":
    try:
        activate_network_blocker()
        print("Network protection activated automatically")
    except Exception as e:
        print(f"Warning: Could not activate network protection: {e}")
