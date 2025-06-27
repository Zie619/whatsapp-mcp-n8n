#!/usr/bin/env python3
"""
TCP-based MCP server for WhatsApp integration with n8n.
This runs the same MCP server but over TCP instead of stdio.
"""
import asyncio
import sys
import traceback
import os
from mcp.server.fastmcp import FastMCP
from main import mcp  # Import the configured MCP server from main.py

async def tcp_server_handler(reader, writer):
    """Handle TCP client connections for MCP protocol."""
    client_addr = writer.get_extra_info('peername')
    print(f"Client connected: {client_addr}", file=sys.stderr)
    
    try:
        # Create transport for this connection
        transport = TCPTransport(reader, writer)
        
        # Run the MCP server with this transport
        await mcp.run_async(transport=transport)
        
    except Exception as e:
        print(f"Error handling client {client_addr}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Client disconnected: {client_addr}", file=sys.stderr)

class TCPTransport:
    """TCP transport adapter for MCP."""
    
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
    
    async def read(self):
        """Read a message from the TCP connection."""
        try:
            # Read JSON-RPC message (assuming newline-delimited)
            line = await self.reader.readline()
            if not line:
                return None
            return line.decode().strip()
        except Exception as e:
            print(f"Error reading from TCP: {e}", file=sys.stderr)
            return None
    
    async def write(self, message):
        """Write a message to the TCP connection."""
        try:
            self.writer.write((message + '\n').encode())
            await self.writer.drain()
        except Exception as e:
            print(f"Error writing to TCP: {e}", file=sys.stderr)

async def main():
    """Start the TCP MCP server."""
    print("Starting WhatsApp MCP TCP Server...", file=sys.stderr)
    
    try:
        # Test dependencies first
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
        
        # Start TCP server
        server = await asyncio.start_server(
            tcp_server_handler,
            '0.0.0.0',  # Listen on all interfaces
            9000        # Port 9000
        )
        
        addr = server.sockets[0].getsockname()
        print(f"WhatsApp MCP TCP server running on {addr[0]}:{addr[1]}", file=sys.stderr)
        print("Ready to accept connections from n8n", file=sys.stderr)
        
        # Run forever
        async with server:
            await server.serve_forever()
            
    except Exception as e:
        print(f"Error starting TCP server: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 