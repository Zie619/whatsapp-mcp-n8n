#!/usr/bin/env python3
"""
Test script to list WhatsApp chats through the MCP server
"""
import json
import subprocess
import sys
import time

def send_mcp_request(process, request):
    """Send a request to the MCP server"""
    request_json = json.dumps(request) + "\n"
    print(f"Sending: {request_json.strip()}")
    process.stdin.write(request_json)
    process.stdin.flush()

def read_mcp_response(process):
    """Read a response from the MCP server"""
    response = process.stdout.readline()
    if response:
        return json.loads(response)
    return None

def list_chats():
    """List chats through the MCP server"""
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            ["docker", "exec", "-i", "whatsapp-mcp-server", "python", "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a moment for the server to start
        time.sleep(1)
        
        # Initialize the MCP session
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        send_mcp_request(process, init_request)
        response = read_mcp_response(process)
        print(f"Init response: {response}")
        
        if not response or "error" in response:
            print("Failed to initialize MCP session")
            return False
        
        # Send initialized notification
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        send_mcp_request(process, initialized_request)
        
        # Now list chats
        chats_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_chats",
                "arguments": {
                    "limit": 5
                }
            }
        }
        
        send_mcp_request(process, chats_request)
        response = read_mcp_response(process)
        print(f"Chats response: {response}")
        
        # Close the process
        process.terminate()
        process.wait(timeout=5)
        
        return response and "error" not in response
        
    except subprocess.TimeoutExpired:
        print("Request timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Listing WhatsApp chats through MCP...")
    success = list_chats()
    
    if success:
        print("✅ Chats listed successfully through MCP!")
    else:
        print("❌ Failed to list chats through MCP") 