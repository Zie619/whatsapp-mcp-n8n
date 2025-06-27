#!/usr/bin/env python3
"""
STDIO-over-TCP bridge for MCP protocol.
This preserves the MCP stdio protocol but makes it accessible over TCP.
"""
import asyncio
import sys
import json
import subprocess
import os

class StdioTCPBridge:
    def __init__(self, port=9000):
        self.port = port
        self.mcp_process = None
    
    async def handle_client(self, reader, writer):
        """Handle a client connection by bridging to MCP stdio."""
        client_addr = writer.get_extra_info('peername')
        print(f"MCP client connected: {client_addr}", file=sys.stderr)
        
        try:
            # Start the MCP server process
            self.mcp_process = await asyncio.create_subprocess_exec(
                'python', '/app/main.py',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd='/app'
            )
            
            # Bridge data between TCP client and MCP process
            await asyncio.gather(
                self.tcp_to_mcp(reader, self.mcp_process.stdin),
                self.mcp_to_tcp(self.mcp_process.stdout, writer),
                self.log_stderr(self.mcp_process.stderr)
            )
            
        except Exception as e:
            print(f"Error handling client {client_addr}: {e}", file=sys.stderr)
        finally:
            if self.mcp_process:
                self.mcp_process.terminate()
                await self.mcp_process.wait()
            writer.close()
            await writer.wait_closed()
            print(f"MCP client disconnected: {client_addr}", file=sys.stderr)
    
    async def tcp_to_mcp(self, reader, mcp_stdin):
        """Forward data from TCP client to MCP process stdin."""
        try:
            while True:
                data = await reader.read(8192)
                if not data:
                    break
                mcp_stdin.write(data)
                await mcp_stdin.drain()
        except Exception as e:
            print(f"Error in tcp_to_mcp: {e}", file=sys.stderr)
        finally:
            mcp_stdin.close()
    
    async def mcp_to_tcp(self, mcp_stdout, writer):
        """Forward data from MCP process stdout to TCP client."""
        try:
            while True:
                data = await mcp_stdout.read(8192)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except Exception as e:
            print(f"Error in mcp_to_tcp: {e}", file=sys.stderr)
    
    async def log_stderr(self, mcp_stderr):
        """Log MCP process stderr."""
        try:
            while True:
                data = await mcp_stderr.read(8192)
                if not data:
                    break
                sys.stderr.buffer.write(data)
        except Exception as e:
            print(f"Error in log_stderr: {e}", file=sys.stderr)
    
    async def start_server(self):
        """Start the TCP server."""
        print(f"Starting STDIO-TCP bridge for MCP on port {self.port}", file=sys.stderr)
        
        # Test dependencies first
        print("Testing database connection...", file=sys.stderr)
        from whatsapp import MESSAGES_DB_PATH
        if not os.path.exists(MESSAGES_DB_PATH):
            print(f"Warning: Database file not found at {MESSAGES_DB_PATH}", file=sys.stderr)
        else:
            print(f"Database found at {MESSAGES_DB_PATH}", file=sys.stderr)
        
        server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        print(f"MCP STDIO-TCP bridge running on {addr[0]}:{addr[1]}", file=sys.stderr)
        print("n8n can connect with: nc whatsapp-mcp-server 9000", file=sys.stderr)
        
        async with server:
            await server.serve_forever()

async def main():
    bridge = StdioTCPBridge(port=9000)
    await bridge.start_server()

if __name__ == "__main__":
    asyncio.run(main()) 