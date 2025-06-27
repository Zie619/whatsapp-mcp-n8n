#!/usr/bin/env python3
"""
HTTP-to-MCP bridge for n8n integration.
This creates an HTTP API that translates to MCP protocol calls.
"""
import json
import sys
import asyncio
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
import os

class MCPBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for basic info."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "whatsapp-mcp-bridge"
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for MCP commands."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode())
            
            # Extract command and arguments
            command = request_data.get('command')
            arguments = request_data.get('arguments', {})
            
            if not command:
                self.send_error(400, "Command is required")
                return
            
            # Call the MCP server directly
            result = self.call_mcp_tool(command, arguments)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Error handling request: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self.send_error(500, str(e))
    
    def call_mcp_tool(self, tool_name, arguments):
        """Call an MCP tool directly."""
        try:
            # Import the MCP functions directly
            sys.path.append('/app')
            
            # Map tool names to functions
            if tool_name == 'send_message':
                from whatsapp import send_message
                recipient = arguments.get('recipient')
                message = arguments.get('message')
                success, msg = send_message(recipient, message)
                return {"success": success, "message": msg}
                
            elif tool_name == 'list_chats':
                from whatsapp import list_chats
                chats = list_chats(
                    query=arguments.get('query'),
                    limit=arguments.get('limit', 20),
                    page=arguments.get('page', 0),
                    include_last_message=arguments.get('include_last_message', True),
                    sort_by=arguments.get('sort_by', 'last_active')
                )
                return [{"jid": c.jid, "name": c.name, "last_message_time": c.last_message_time.isoformat() if c.last_message_time else None, "last_message": c.last_message} for c in chats]
                
            elif tool_name == 'list_messages':
                from whatsapp import list_messages
                messages = list_messages(
                    after=arguments.get('after'),
                    before=arguments.get('before'),
                    sender_phone_number=arguments.get('sender_phone_number'),
                    chat_jid=arguments.get('chat_jid'),
                    query=arguments.get('query'),
                    limit=arguments.get('limit', 20),
                    page=arguments.get('page', 0),
                    include_context=arguments.get('include_context', True),
                    context_before=arguments.get('context_before', 1),
                    context_after=arguments.get('context_after', 1)
                )
                return [{"timestamp": m.timestamp.isoformat(), "sender": m.sender, "content": m.content, "is_from_me": m.is_from_me, "chat_jid": m.chat_jid, "id": m.id, "chat_name": m.chat_name} for m in messages]
                
            elif tool_name == 'search_contacts':
                from whatsapp import search_contacts
                query = arguments.get('query')
                contacts = search_contacts(query)
                return [{"phone_number": c.phone_number, "name": c.name, "jid": c.jid} for c in contacts]
                
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"error": str(e)}

def main():
    print("Starting WhatsApp MCP HTTP Bridge...", file=sys.stderr)
    
    try:
        # Test dependencies
        print("Testing database connection...", file=sys.stderr)
        from whatsapp import MESSAGES_DB_PATH
        if not os.path.exists(MESSAGES_DB_PATH):
            print(f"Warning: Database file not found at {MESSAGES_DB_PATH}", file=sys.stderr)
        else:
            print(f"Database found at {MESSAGES_DB_PATH}", file=sys.stderr)
        
        # Test API connection
        print("Testing API connection...", file=sys.stderr)
        import requests
        from whatsapp import get_api_url
        try:
            api_url = get_api_url()
            response = requests.get(f"{api_url}/health", timeout=5)
            print(f"API connection test: {response.status_code}", file=sys.stderr)
        except Exception as api_e:
            print(f"API connection failed: {api_e}", file=sys.stderr)
        
        # Start HTTP server
        server = HTTPServer(('0.0.0.0', 8090), MCPBridgeHandler)
        print(f"WhatsApp MCP HTTP Bridge running on port 8090", file=sys.stderr)
        print("n8n can now connect via HTTP requests", file=sys.stderr)
        server.serve_forever()
        
    except Exception as e:
        print(f"Error starting HTTP bridge: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 