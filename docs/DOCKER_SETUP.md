# Axiom AI - Docker Setup Guide

This guide explains how to run Axiom AI using Docker and docker-compose.

---

## Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **OpenAI API Key**

---

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to project directory
cd "Axiom AI"

# Copy environment template
cp env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-your-key-here
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Verify Services

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f axiom-backend
docker-compose logs -f chromadb

# Check metrics endpoint (port 5000)
curl http://localhost:5000/metrics
curl http://localhost:5000/health
curl http://localhost:5000/
```

---

## Service Architecture

```
┌─────────────────────────────────────────────────┐
│               docker-compose                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐       ┌──────────────┐        │
│  │   ChromaDB  │◄──────┤ Axiom Backend│        │
│  │  (Port 8001)│       │  (Port 5000) │        │
│  │             │       │              │        │
│  │ Vector DB   │       │ Metrics API  │        │
│  └─────────────┘       └──────────────┘        │
│                                                  │
│  Network: axiom-network                         │
│  Volume: chroma_data (persistent)               │
└─────────────────────────────────────────────────┘
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `AXIOM_API_KEYS` | Comma-separated API keys for auth | (none) |
| `EMBEDDING_PROVIDER` | `local` or `openai` | `local` |
| `EMBEDDING_MODEL` | Embedding model name | `all-MiniLM-L6-v2` |
| `LLM_PROVIDER` | `openai` (more coming) | `openai` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `LOG_FORMAT` | `text` or `json` | `json` |

---

## Common Commands

### Start Services

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Start only ChromaDB
docker-compose up chromadb

# Rebuild a specific service
docker-compose up --build axiom-backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v

# Stop but keep containers
docker-compose stop
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Logs for specific service
docker-compose logs axiom-backend

# Last 100 lines
docker-compose logs --tail=100

# Enter a running container
docker exec -it axiom-backend bash
```

### Health Checks

```bash
# Check all services status
docker-compose ps

# Check backend health
curl http://localhost:5000/health

# Check metrics
curl http://localhost:5000/metrics

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

---

## Volume Management

### ChromaDB Data Persistence

ChromaDB data is stored in a Docker volume (`chroma_data`) for persistence across container restarts.

```bash
# List volumes
docker volume ls

# Inspect chroma_data volume
docker volume inspect axiom-ai_chroma_data

# Backup volume
docker run --rm -v axiom-ai_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup.tar.gz /data

# Restore volume
docker run --rm -v axiom-ai_chroma_data:/data -v $(pwd):/backup alpine tar xzf /backup/chroma_backup.tar.gz -C /

# Remove volume (DELETES DATA!)
docker volume rm axiom-ai_chroma_data
```

---

## Networking

Services communicate over the `axiom-network` bridge network.

```bash
# Inspect network
docker network inspect axiom-ai_axiom-network

# Backend can reach ChromaDB at: http://chromadb:8000
# Host can reach services at:
#   - Backend metrics: http://localhost:5000
#   - ChromaDB: http://localhost:8001
```

---

## Production Deployment

### Best Practices

1. **Use .env file**: Never hardcode secrets in `docker-compose.yml`
2. **Enable health checks**: Already configured for both services
3. **Set restart policy**: `restart: unless-stopped` is configured
4. **Resource limits**: Add CPU/memory limits if needed
5. **Non-root user**: Backend runs as user `axiom` (UID 1000)
6. **Multi-stage build**: Dockerfile uses multi-stage for smaller images

### Adding Resource Limits

Edit `docker-compose.yml`:

```yaml
axiom-backend:
  # ... existing config ...
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

### SSL/TLS Termination

For production, use a reverse proxy (Nginx/Traefik) for SSL:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "443:443"
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./certs:/etc/nginx/certs:ro
  depends_on:
    - axiom-backend
  networks:
    - axiom-network
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs axiom-backend

# Common issues:
# 1. Missing OPENAI_API_KEY in .env
# 2. Port conflicts (5000 or 8001 already in use)
# 3. ChromaDB not healthy yet (backend waits for it)
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 on host instead
```

### ChromaDB Connection Failed

```bash
# Check ChromaDB is running
docker-compose ps chromadb

# Check health
curl http://localhost:8001/api/v1/heartbeat

# Restart ChromaDB
docker-compose restart chromadb
```

### Permission Denied Errors

```bash
# If you see permission errors for volumes:
# On Linux, ensure the axiom user (UID 1000) can write

# Fix permissions
sudo chown -R 1000:1000 ./logs
sudo chown -R 1000:1000 ./axiom/data
```

### Out of Disk Space

```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df
```

---

## Development vs Production

### Development

```yaml
# docker-compose.yml for development
axiom-backend:
  volumes:
    - ./axiom:/app/axiom  # Hot reload (mount source)
    - ./scripts:/app/scripts
  environment:
    - LOG_LEVEL=DEBUG
```

### Production

```yaml
# Use the default docker-compose.yml
# No source code mounts
# LOG_LEVEL=INFO
# Use specific image tags (not 'latest')
```

---

## Next Steps

After Docker setup:

1. **Ingest documents**: Mount documents to `/app/axiom/data` and run ingestion
2. **Configure API keys**: Set `AXIOM_API_KEYS` for authentication
3. **Monitor metrics**: Access `/metrics` endpoint for Prometheus
4. **Setup CI/CD**: Use GitHub Actions to build/push images

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:5000/health`
3. Review environment variables: `docker-compose config`

---

*Docker setup complete! Your Axiom AI stack is containerized and production-ready.* 🐳

