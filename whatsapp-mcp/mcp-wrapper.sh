#!/bin/bash

# Simple wrapper script to run the WhatsApp MCP server
# This will be called by n8n and should just execute the MCP server

# Change to the app directory
cd /app

# Run the MCP server with proper Python path
exec python main.py 