# Docker Fundamentals

Docker packages applications and their dependencies into portable, reproducible containers.

## Images vs Containers
An **image** is a read-only snapshot of a filesystem and a startup command. A **container** is a running instance of an image — an isolated process with its own filesystem, network, and PID namespace.

## Dockerfile Best Practices
- Base on the smallest reasonable image (`node:22-alpine`, `python:3.12-slim`).
- Order layers from least to most frequently changing (copy `package.json` and `npm ci` before copying source code).
- Run as a non-root user.
- Use multi-stage builds to keep the final image lean:
```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Docker Compose
Define multi-container applications (app + database + cache) in a single `docker-compose.yml`. `docker compose up` starts everything; `docker compose down -v` tears it down including volumes.

## Volumes and Bind Mounts
- **Volume**: managed by Docker, persists data across container restarts. Use for databases.
- **Bind mount**: maps a host path into the container. Use during development for hot reload.

## Networking
Containers in the same Compose project share a default bridge network and can reach each other by service name (`postgres`, `redis`).

## Health Checks
Define a `healthcheck` in Compose so dependent services wait until the dependency is ready:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]
  interval: 5s
  retries: 5
```

## Environment Variables
Pass secrets via `.env` files or Docker secrets. Never bake secrets into images.
