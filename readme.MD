Sure! Here’s a concise README file for your instructions:

---

# WhatsApp-MCP Integration with n8n

## 1. Add Folder

Copy or move the `whatsapp-mcp` folder into your Docker workdir where your n8n `docker-compose.yml` file is located.
Example:

```
/your-n8n-docker-workdir/
├── docker-compose.yml
├── whatsapp-mcp/
```

## 2. Update `docker-compose.yml`

Add the following service configuration to your `docker-compose.yml` file (adjust as needed):

```yaml
services:

  whatsapp-bridge:
    build:
      context: ./whatsapp-mcp
      dockerfile: Dockerfile.whatsapp-bridge
    container_name: whatsapp-bridge
    ports:
      - "8081:8080"  # Changed from 8080 to avoid conflict with OpenProject
    volumes:
      - whatsapp_store:/app/store
    environment:
      - TZ=UTC
    restart: unless-stopped
    networks:
      - internal

  whatsapp-mcp-server:
    build:
      context: ./whatsapp-mcp
      dockerfile: Dockerfile.mcp-server
    container_name: whatsapp-mcp-server
    ports:
      - "9000:9000"  # Expose MCP STDIO-TCP bridge for n8n
    volumes:
      - whatsapp_store:/app/store
      - ./whatsapp-mcp/media:/app/media:rw
    environment:
      - TZ=UTC
      - PYTHONUNBUFFERED=1
      - PYTHONIOENCODING=utf-8
    depends_on:
      - whatsapp-bridge
    restart: unless-stopped
    command: python /app/stdio_tcp_bridge.py
    networks:
      - internal


volumes:
  whatsapp_store:

networks:
  internal:
    driver: bridge

```

Place this block under the `services:` section.
Make sure to update paths, environment variables, and ports to fit your use-case.

#docker compose build 
#docker compose up -d 
---
![alt text](<Screenshot from 2025-06-28 00-53-54.png>)


credit to https://github.com/lharries/whatsapp-mcp on the original 