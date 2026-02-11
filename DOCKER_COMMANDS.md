# 🐳 Docker Quick Reference

## Common Docker Commands

### Building Images

```bash
# Build image from Dockerfile
docker build -t school-library:latest .

# Build with specific Dockerfile
docker build -t school-library:test -f Dockerfile.test .

# Build without cache
docker build --no-cache -t school-library:latest .

# Build with build arguments
docker build --build-arg VERSION=1.0.0 -t school-library:1.0.0 .
```

### Running Containers

```bash
# Run container
docker run -d -p 8000:8000 school-library:latest

# Run container with environment variables
docker run -d -e LOG_LEVEL=DEBUG -p 8000:8000 school-library:latest

# Run container with volume
docker run -d -v /local/path:/app/data -p 8000:8000 school-library:latest

# Run interactive container
docker run -it school-library:latest /bin/bash

# Run container with name
docker run -d --name my-app school-library:latest
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi school-library:latest

# Tag image
docker tag school-library:latest ghcr.io/reeman-idais/school-library:v1.0.0

# Inspect image
docker inspect school-library:latest

# View image history
docker history school-library:latest

# Push image to registry
docker push ghcr.io/reeman-idais/school-library:v1.0.0

# Pull image from registry
docker pull ghcr.io/reeman-idais/school-library:v1.0.0
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop <container_id>

# Start container
docker start <container_id>

# Remove container
docker rm <container_id>

# Remove all stopped containers
docker container prune

# View container logs
docker logs <container_id>

# Follow container logs
docker logs -f <container_id>

# Execute command in container
docker exec -it <container_id> /bin/bash

# Copy file from container
docker cp <container_id>:/app/file.txt ./file.txt

# View container stats
docker stats <container_id>
```

## Docker Compose Commands

### Compose Basics

```bash
# Start services
docker-compose up

# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View services status
docker-compose ps

# View service logs
docker-compose logs

# Follow logs for specific service
docker-compose logs -f app

# Remove containers and volumes
docker-compose down -v --remove-orphans
```

### Building with Compose

```bash
# Build services
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build app

# Pull images
docker-compose pull

# Push images
docker-compose push
```

### Managing Services

```bash
# Start specific service
docker-compose up -d app

# Stop specific service
docker-compose stop app

# Run command in service
docker-compose exec app python -c "print('Hello')"

# Run command with stdin/stdout
docker-compose exec -it app /bin/bash

# Scale service
docker-compose up -d --scale app=3

# Remove service container
docker-compose rm app
```

### Using Profiles

```bash
# Use development profile
docker-compose --profile dev up -d

# Use testing profile
docker-compose --profile test up -d

# Use multiple profiles
docker-compose --profile dev --profile monitoring up -d

# List all profiles
docker-compose config --profiles
```

## Docker Registry

### GitHub Container Registry (GHCR)

```bash
# Login to GHCR
docker login ghcr.io -u USERNAME -p TOKEN

# Push to GHCR
docker tag school-library:latest ghcr.io/reeman-idais/school-library:latest
docker push ghcr.io/reeman-idais/school-library:latest

# Pull from GHCR
docker pull ghcr.io/reeman-idais/school-library:latest

# Logout from GHCR
docker logout ghcr.io
```

### Docker Hub

```bash
# Login to Docker Hub
docker login

# Push to Docker Hub
docker tag school-library:latest username/school-library:latest
docker push username/school-library:latest

# Pull from Docker Hub
docker pull username/school-library:latest
```

## Debugging & Troubleshooting

### Inspecting Containers

```bash
# Inspect container
docker inspect <container_id>

# View resource usage
docker stats <container_id>

# View process list
docker top <container_id>

# Check container health
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

### Looking at Logs

```bash
# View all logs
docker logs <container_id>

# View last 100 lines
docker logs --tail 100 <container_id>

# View logs with timestamps
docker logs -t <container_id>

# Follow logs
docker logs -f <container_id>

# View logs since specific time
docker logs --since 2024-01-01 <container_id>

# Export logs to file
docker logs <container_id> > container.log 2>&1
```

### Debugging Network

```bash
# List networks
docker network ls

# Inspect network
docker network inspect <network_id>

# Connect container to network
docker network connect <network_name> <container_id>

# Disconnect container from network
docker network disconnect <network_name> <container_id>

# DNS resolution test
docker run --rm alpine nslookup app
```

## Storage Management

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect <volume_name>

# Remove volume
docker volume rm <volume_name>

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/volume.tar.gz /data

# Restore volume
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar xzf /backup/volume.tar.gz -C /
```

## System Management

### Cleanup

```bash
# Remove unused images
docker image prune

# Remove unused images and dangling layers
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Full system cleanup
docker system prune -a --volumes
```

### Build Cache

```bash
# Clear build cache
docker builder prune

# Clear all build cache
docker builder prune -a

# View build cache
docker buildx du
```

## Performance Optimization

### Resource Limits

```bash
# Run with CPU limit (0.5 cores)
docker run -d --cpus 0.5 school-library:latest

# Run with memory limit (512MB)
docker run -d -m 512m school-library:latest

# Run with CPU and memory limits
docker run -d --cpus 1 -m 1g school-library:latest

# Set in compose
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Image Optimization

```bash
# Multi-stage build
# Use .dockerignore to exclude files
# Minimize layers
# Use alpine images
# Pin base image versions
```

## Useful Aliases

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Docker aliases
alias dls='docker ps -l -q'
alias di='docker images'
alias dps='docker ps'
alias dai='docker images -a'

# Docker Compose aliases
alias dcup='docker-compose up -d'
alias dcdn='docker-compose down'
alias dcl='docker-compose logs -f'
alias dce='docker-compose exec'

# Cleanup
alias dclean='docker system prune -a'
alias dcleanv='docker system prune -a -v'
```

## Best Practices

1. **Use specific base image versions**: `FROM python:3.10-slim` not `FROM python`
2. **Multi-stage builds**: Reduce final image size
3. **Non-root user**: Run container as unprivileged user
4. **.dockerignore**: Exclude unnecessary files
5. **Health checks**: Monitor container health
6. **Logging**: Send logs to stdout/stderr
7. **Security**: Scan images, don't run as root
8. **Caching**: Order Dockerfile commands from least to most changeable

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Container Security](https://docs.docker.com/engine/security/)
