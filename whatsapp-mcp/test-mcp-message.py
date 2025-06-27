#!/usr/bin/env python3
"""
Test script to send a WhatsApp message through the MCP server
"""
import json
import subprocess
import sys

def send_mcp_message(recipient, message):
    """Send a message through the MCP server using stdio"""
    
    # MCP request format for calling the send_message tool
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "send_message",
            "arguments": {
                "recipient": recipient,
                "message": message
            }
        }
    }
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            ["docker", "exec", "-i", "whatsapp-mcp-server", "python", "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the request
        request_json = json.dumps(request) + "\n"
        print(f"Sending request: {request_json.strip()}")
        
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        print(f"Response: {stdout}")
        if stderr:
            print(f"Error: {stderr}")
            
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Request timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    recipient = "972536622456"
    message = "Hello from MCP Docker setup! 🐳"
    
    print(f"Sending message to {recipient}: {message}")
    success = send_mcp_message(recipient, message)
    
    if success:
        print("✅ Message sent successfully through MCP!")
    else:
        print("❌ Failed to send message through MCP") 