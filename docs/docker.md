# Docker Deployment

This document covers Docker-based deployment options for the Udemy Downloader, including containerization, orchestration, and production deployment strategies.

## Docker Overview

### Why Use Docker?

#### Benefits
- **Consistent Environment**: Same runtime across different systems
- **Dependency Management**: All external tools pre-installed and configured
- **Isolation**: Separate from host system dependencies
- **Scalability**: Easy to deploy multiple instances
- **Portability**: Run anywhere Docker is supported

#### Use Cases
- **Development**: Consistent development environment
- **CI/CD**: Automated course downloading in pipelines
- **Production**: Reliable deployment in server environments
- **Multi-platform**: Run on different operating systems

## Dockerfile Analysis

### Base Image Selection
```dockerfile
FROM python:3.12-slim-bullseye
```

**Rationale:**
- **python:3.12**: Latest stable Python version
- **slim-bullseye**: Minimal Debian-based image
- **Size optimization**: Smaller attack surface and faster builds

### System Dependencies
```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    aria2 \
    unzip \
    xz-utils \
    jq \
    && rm -rf /var/lib/apt/lists/*
```

**Installed Tools:**
- **curl/wget**: HTTP download utilities
- **aria2**: High-speed download manager
- **unzip/xz-utils**: Archive extraction
- **jq**: JSON processing for dynamic downloads

**Optimization:**
- Single RUN command reduces layers
- Cache cleanup removes package lists
- Minimal tool selection for functionality

### FFmpeg Installation
```dockerfile
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar xvf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-*-amd64-static* \
    && chmod +x /usr/local/bin/ffmpeg \
    && chmod +x /usr/local/bin/ffprobe
```

**Features:**
- **Static build**: No additional dependencies
- **Latest version**: Always downloads current release
- **Cleanup**: Removes temporary files
- **Permissions**: Ensures executability

### Shaka Packager Installation
```dockerfile
RUN LATEST_TAG=$(curl -s https://api.github.com/repos/shaka-project/shaka-packager/releases/latest | jq -r .tag_name) && \
    wget https://github.com/shaka-project/shaka-packager/releases/download/$LATEST_TAG/packager-linux-x64 -O /usr/local/bin/shaka-packager && \
    chmod +x /usr/local/bin/shaka-packager && \
    echo "Shaka Packager version $LATEST_TAG installed."
```

**Dynamic Installation:**
- **API query**: Gets latest release tag
- **Version logging**: Records installed version
- **Direct download**: Single binary installation

### Application Setup
```dockerfile
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
```

**Structure:**
- **Working directory**: `/app` for all operations
- **Source copy**: Complete application code
- **Dependencies**: Python package installation

## Docker Compose Configuration

### Service Definition
```yaml
services:
  udemy-downloader:
    image: udemy-downloader:latest
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./output:/app/out_dir:rw
      - ./keyfile.json:/app/keyfile.json:ro
    env_file:
      - .env
    command: python main.py -c $COURSE_URL
```

### Volume Management

#### Output Directory
```yaml
volumes:
  - ./output:/app/out_dir:rw
```
- **Host path**: `./output` (relative to compose file)
- **Container path**: `/app/out_dir` (application default)
- **Permissions**: Read-write for file creation

#### Configuration Files
```yaml
volumes:
  - ./keyfile.json:/app/keyfile.json:ro
  - ./cookies.txt:/app/cookies.txt:ro  # Optional
```
- **Read-only**: Prevents accidental modification
- **Host binding**: Direct file mapping
- **Configuration**: Essential for DRM decryption

### Environment Configuration
```yaml
env_file:
  - .env
```

**Environment Variables:**
```bash
# .env file content
UDEMY_BEARER=your_bearer_token_here
COURSE_URL=https://www.udemy.com/course/example/
```

## Building and Running

### Build Process

#### Build Image
```bash
# Build from Dockerfile
docker build -t udemy-downloader .

# Build with specific tag
docker build -t udemy-downloader:v1.0 .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t udemy-downloader .
```

#### Build Optimization
```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t udemy-downloader .

# Multi-stage build (if implemented)
docker build --target production -t udemy-downloader .
```

### Running Containers

#### Docker Compose (Recommended)
```bash
# Start services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Direct Docker Run
```bash
# Basic run
docker run -it udemy-downloader

# With volume mounts
docker run -it \
  -v $(pwd)/output:/app/out_dir \
  -v $(pwd)/keyfile.json:/app/keyfile.json:ro \
  -e UDEMY_BEARER="your_token" \
  udemy-downloader \
  python main.py -c "course_url"

# Interactive shell
docker run -it udemy-downloader /bin/bash
```

### Advanced Usage

#### Custom Commands
```bash
# Course information only
docker run -it udemy-downloader \
  python main.py -c "course_url" --info

# Specific quality and assets
docker run -it udemy-downloader \
  python main.py -c "course_url" -q 720 --download-assets

# Debug mode
docker run -it udemy-downloader \
  python main.py -c "course_url" --log-level DEBUG
```

#### Resource Limits
```bash
# Memory and CPU limits
docker run -it \
  --memory=2g \
  --cpus=2 \
  udemy-downloader

# With Docker Compose
services:
  udemy-downloader:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
        reservations:
          memory: 1G
          cpus: '1'
```

## Production Deployment

### Multi-Stage Dockerfile

#### Optimized Build
```dockerfile
# Build stage
FROM python:3.12-slim-bullseye AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.12-slim-bullseye AS production
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget aria2 unzip xz-utils jq \
    && rm -rf /var/lib/apt/lists/*

# Install external tools
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar xvf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-*-amd64-static*

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 udemy && chown -R udemy:udemy /app
USER udemy

# Update PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "main.py"]
```

### Docker Compose Production

#### Production Configuration
```yaml
version: '3.8'

services:
  udemy-downloader:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
    
    # Restart policy
    restart: unless-stopped
    
    # Volume mounts
    volumes:
      - ./output:/app/out_dir:rw
      - ./keyfile.json:/app/keyfile.json:ro
      - ./logs:/app/logs:rw
    
    # Environment
    env_file:
      - .env.production
    
    # Networking
    networks:
      - udemy-network

networks:
  udemy-network:
    driver: bridge
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: udemy-downloader
spec:
  replicas: 1
  selector:
    matchLabels:
      app: udemy-downloader
  template:
    metadata:
      labels:
        app: udemy-downloader
    spec:
      containers:
      - name: udemy-downloader
        image: udemy-downloader:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: output-volume
          mountPath: /app/out_dir
        - name: config-volume
          mountPath: /app/keyfile.json
          subPath: keyfile.json
        env:
        - name: UDEMY_BEARER
          valueFrom:
            secretKeyRef:
              name: udemy-secrets
              key: bearer-token
      volumes:
      - name: output-volume
        persistentVolumeClaim:
          claimName: udemy-output-pvc
      - name: config-volume
        configMap:
          name: udemy-config
```

#### ConfigMap and Secrets
```yaml
# ConfigMap for keyfile
apiVersion: v1
kind: ConfigMap
metadata:
  name: udemy-config
data:
  keyfile.json: |
    {
      "key_id_1": "decryption_key_1"
    }

---
# Secret for bearer token
apiVersion: v1
kind: Secret
metadata:
  name: udemy-secrets
type: Opaque
data:
  bearer-token: <base64-encoded-token>
```

## Monitoring and Logging

### Log Management

#### Docker Compose Logging
```yaml
services:
  udemy-downloader:
    # ... other config
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
    
    # Or use external logging
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://logserver:514"
```

#### Log Aggregation
```yaml
# ELK Stack integration
services:
  udemy-downloader:
    # ... other config
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://logstash:12201"
        tag: "udemy-downloader"
```

### Health Checks

#### Container Health Check
```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1
```

#### Docker Compose Health Check
```yaml
services:
  udemy-downloader:
    # ... other config
    healthcheck:
      test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/main.py') else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Security Considerations

### Container Security

#### Non-Root User
```dockerfile
# Create and use non-root user
RUN useradd -m -u 1000 udemy
USER udemy
```

#### Read-Only Root Filesystem
```yaml
services:
  udemy-downloader:
    # ... other config
    read_only: true
    tmpfs:
      - /tmp
      - /app/temp
```

#### Security Options
```yaml
services:
  udemy-downloader:
    # ... other config
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
```

### Secrets Management

#### Docker Secrets
```yaml
# docker-compose.yml
services:
  udemy-downloader:
    secrets:
      - bearer_token
      - decryption_keys

secrets:
  bearer_token:
    file: ./secrets/bearer_token.txt
  decryption_keys:
    file: ./secrets/keyfile.json
```

#### Environment Variable Security
```bash
# Use Docker secrets instead of environment variables
docker secret create bearer_token bearer_token.txt
docker service create \
  --secret bearer_token \
  --name udemy-downloader \
  udemy-downloader:latest
```

## Troubleshooting

### Common Issues

#### Permission Problems
```bash
# Fix volume permissions
sudo chown -R $(id -u):$(id -g) ./output

# Run with user mapping
docker run -it \
  --user $(id -u):$(id -g) \
  udemy-downloader
```

#### Memory Issues
```bash
# Increase memory limit
docker run -it --memory=4g udemy-downloader

# Monitor memory usage
docker stats udemy-downloader
```

#### Network Issues
```bash
# Use host networking
docker run -it --network host udemy-downloader

# Check DNS resolution
docker run -it udemy-downloader nslookup udemy.com
```

### Debugging

#### Container Inspection
```bash
# Inspect container
docker inspect udemy-downloader

# View logs
docker logs -f udemy-downloader

# Execute commands in running container
docker exec -it udemy-downloader /bin/bash
```

#### Build Debugging
```bash
# Build with no cache
docker build --no-cache -t udemy-downloader .

# Build specific stage
docker build --target builder -t udemy-downloader-debug .
```

## Best Practices

### Development
1. **Use multi-stage builds** for smaller production images
2. **Pin base image versions** for reproducible builds
3. **Use .dockerignore** to exclude unnecessary files
4. **Layer caching** optimize for faster builds

### Production
1. **Resource limits** prevent resource exhaustion
2. **Health checks** ensure container reliability
3. **Logging strategy** for monitoring and debugging
4. **Security hardening** follow container security best practices

### Maintenance
1. **Regular updates** keep base images current
2. **Vulnerability scanning** check for security issues
3. **Backup strategies** for persistent data
4. **Monitoring** track performance and errors