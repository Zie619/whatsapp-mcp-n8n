# WhatsApp MCP Docker Setup

This document describes how to run the WhatsApp MCP server using Docker containers.

## Architecture

The setup consists of two containers:

1. **whatsapp-bridge**: A Go service that connects to WhatsApp Web and provides a REST API
2. **whatsapp-mcp-server**: A Python MCP server that communicates with the bridge and exposes WhatsApp functionality via MCP

## Prerequisites

- Docker
- Docker Compose
- curl (for testing)

## Quick Start

1. **Build and start the services:**
   ```bash
   docker-compose up -d --build
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs to see QR code for WhatsApp authentication:**
   ```bash
   docker-compose logs whatsapp-bridge
   ```

4. **Scan the QR code** with your WhatsApp mobile app to authenticate

5. **Test the setup:**
   ```bash
   ./test-docker-setup.sh
   ```

## Container Details

### WhatsApp Bridge Container
- **Port**: 8080 (exposed to host)
- **Volume**: `whatsapp_store` (shared database)
- **Purpose**: Connects to WhatsApp Web and provides REST API

### MCP Server Container
- **Communication**: Via stdio (MCP protocol)
- **Volume**: `whatsapp_store` (shared database) + `./media` (media files)
- **Purpose**: Exposes WhatsApp functionality via MCP tools

## Volumes

- `whatsapp_store`: Shared SQLite database for message storage
- `./media`: Local directory for media file uploads/downloads

## Networking

- Both containers are on the same Docker network (`whatsapp-mcp-network`)
- MCP server connects to bridge via container name: `http://whatsapp-bridge:8080/api`

## Usage

### Starting Services
```bash
docker-compose up -d
```

### Stopping Services
```bash
docker-compose down
```

### Viewing Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs whatsapp-bridge
docker-compose logs whatsapp-mcp-server
```

### Rebuilding Services
```bash
docker-compose up -d --build
```

## Troubleshooting

### Bridge Not Responding
1. Check if container is running: `docker-compose ps`
2. View bridge logs: `docker-compose logs whatsapp-bridge`
3. Ensure WhatsApp authentication is complete (QR code scanned)

### MCP Server Issues
1. Check if bridge is accessible: `curl http://localhost:8080/api/send`
2. View MCP server logs: `docker-compose logs whatsapp-mcp-server`
3. Verify database volume is shared correctly

### Media File Issues
1. Ensure `./media` directory exists and has proper permissions
2. Check volume mount in docker-compose.yml

## Development

### Modifying Code
1. Make changes to source code
2. Rebuild containers: `docker-compose up -d --build`
3. Restart services if needed: `docker-compose restart`

### Adding Dependencies
- **Go dependencies**: Update `whatsapp-bridge/go.mod`
- **Python dependencies**: Update `whatsapp-mcp-server/pyproject.toml`

## Security Notes

- The bridge exposes port 8080 to localhost only
- Database files are stored in Docker volumes
- Media files are mounted from local directory
- WhatsApp session data is persisted in the bridge container

## Performance

- Both containers use Alpine Linux for smaller image sizes
- Multi-stage build for Go application reduces final image size
- Shared volumes minimize data duplication 