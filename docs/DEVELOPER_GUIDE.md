# Developer Guide — tkk-UniversalValidator

## Prerequisites

| Tool | Minimum Version |
|---|---|
| Python | 3.13 |
| Poetry | 1.8+ |
| Node.js | 20+ |
| npm | 10+ |
| Docker | 24+ |
| Git | 2.40+ |

---

## Repository Layout

```
tkk-UniversalValidator/
├── backend/          Python 3.13 + FastAPI backend
├── frontend/         React 19 + TypeScript + Vite SPA
├── tests/
│   ├── performance/  k6 load / stress / benchmark profiles
│   └── e2e/          Playwright API and navigation tests
├── docker/           Compose files and monitoring configs
├── kubernetes/       Raw manifests and Helm chart
├── terraform/        AWS / Azure / GCP infrastructure modules
├── scripts/          Backup, restore, migration, DR, performance
└── docs/             All engineering and user documentation
```

---

## Backend Quick Start

```bash
cd backend
cp .env.example .env          # fill in secrets
poetry install
poetry run backend-api        # starts on http://localhost:8000
```

Interactive API docs: `http://localhost:8000/docs`

### Key environment variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | `local` / `dev` / `stage` / `prod` |
| `DATABASE_URL` | asyncpg PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET_KEY` | ≥ 32 character signing secret |
| `CONFIG_ENCRYPTION_KEY` | ≥ 32 character Fernet key material |
| `OTEL_ENABLED` | Set to `true` to enable tracing |

### Running backend tests

```bash
cd backend
poetry run pytest tests/unit -q
poetry run pytest tests/integration -q
poetry run pytest tests/unit/test_security_controls.py -v
```

### Linting and static analysis

```bash
poetry run ruff check app tests
poetry run bandit -r app -c pyproject.toml -ll
```

### Database migrations

```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Create a new migration
poetry run alembic revision --autogenerate -m "your description"

# Check current revision
poetry run alembic current
```

---

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev       # starts on http://localhost:5173
```

### Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Development server with HMR |
| `npm run build` | Production TypeScript compile + Vite bundle |
| `npm run lint` | ESLint |
| `npm test` | Vitest unit test suite |
| `npm run test:coverage` | Coverage report |

---

## Running the Full Stack Locally

```bash
# Base services only
docker compose up -d

# Base services + full observability overlay
docker compose -f docker-compose.yml \
  -f docker/monitoring/docker-compose.monitoring.yml up -d --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Kibana | http://localhost:5601 |

---

## Code Architecture

### Application factory

`backend/app/core/application.py` — `create_app()` builds the FastAPI instance, registers middleware, exception handlers, and routes. Import this function rather than the bare `app` object.

### Dependency injection

All services and repositories are resolved through FastAPI `Depends()`. The `AppContainer` dataclass (`app/dependencies/container.py`) holds pre-built singletons that are attached to `app.state` at startup.

### Adding a new API endpoint

1. Create a router in `backend/app/api/v1/your_module.py`.
2. Register it in `backend/app/api/router.py`.
3. Add request/response schemas in `backend/app/schemas/`.
4. Implement business logic in `backend/app/services/`.
5. Add data access in `backend/app/repositories/`.
6. Write unit tests in `backend/tests/unit/` and integration tests in `backend/tests/integration/`.

### Frontend routing

Routes are defined in `frontend/src/App.tsx`. Navigation items in `frontend/src/config/navigation.ts` control which paths appear in the sidebar and which roles can see them. Every new page must be added to both files.

### Role-based navigation

Use `navItems[i].roles` to restrict visibility. Use `ProtectedRoute` in `App.tsx` to redirect unauthorised access at the routing layer.

---

## CI/CD Pipelines

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push / PR | Lint, unit tests, integration tests, frontend build |
| `comprehensive-testing.yml` | Push / PR | Full matrix including security tests and E2E API |
| `security-scan.yml` | Push / PR + weekly | bandit, pip-audit, npm audit |
| `docker-release.yml` | Push to main / tag | Build and publish GHCR images |
| `deploy.yml` | Manual | Helm deploy to dev / stage / prod |
| `performance.yml` | Manual | k6 load / stress / benchmark |
| `backup-dr.yml` | Manual | Kubernetes backup / restore / migration |
