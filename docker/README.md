# docker

## Purpose
Hosts container strategy documentation, runtime orchestration, and production image guidance.

## Responsibilities
- Define and maintain backend and frontend production image baselines.
- Provide Docker Compose orchestration for local and pre-prod validation.
- Document secure container runtime expectations.
- Define image versioning and vulnerability management requirements.

## Ownership
DevSecOps Platform Team

## Coding Standards
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.

## Artifacts
- Root compose stack: `docker-compose.yml`
- Monitoring overlay stack: `docker/monitoring/docker-compose.monitoring.yml`
- Backend production image: `backend/Dockerfile`
- Frontend production image: `frontend/Dockerfile`
- Frontend runtime web server config: `frontend/nginx.conf`

## Build Production Images
From repository root:

```bash
docker build -t tkk-uv-backend:latest ./backend
docker build -t tkk-uv-frontend:latest ./frontend
```

## Run with Docker Compose
From repository root:

```bash
docker compose up -d --build
```

Services:
- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Run with Monitoring Overlay (Prompt 41)
From repository root:

```bash
docker compose -f docker-compose.yml -f docker/monitoring/docker-compose.monitoring.yml up -d --build
```

Observability endpoints:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Kibana: `http://localhost:5601`

## Prompt 42 Backup and DR
- Backup, restore, migration, and DR operational runbook: `docs/BACKUP_RESTORE_DR.md`
- Operational scripts: `scripts/backup`, `scripts/restore`, `scripts/migration`, `scripts/dr`

Shutdown:

```bash
docker compose down
```

Remove database volume as well:

```bash
docker compose down -v
```
