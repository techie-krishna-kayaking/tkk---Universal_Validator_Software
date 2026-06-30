# kubernetes

## Purpose
Hosts Kubernetes deployment architecture, Helm packaging, ingress routing, and scaling standards.

## Responsibilities
- Define deployment, autoscaling, and fault-tolerance standards.
- Provide baseline Kubernetes manifests for platform runtime.
- Maintain Helm chart packaging for environment promotion.
- Document ingress routing and horizontal scaling controls.

## Ownership
Cloud Runtime Engineering

## Coding Standards
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.

## Structure
- `manifests/`: raw Kubernetes manifests for namespace, backend, frontend, ingress, and HPA.
- `helm/tkk-universal-validator/`: production Helm chart with configurable values.

## Apply Raw Manifests
From repository root:

```bash
kubectl apply -f kubernetes/manifests/namespace.yaml
kubectl apply -f kubernetes/manifests/
```

## Install with Helm
From repository root:

```bash
helm upgrade --install tkk-uv kubernetes/helm/tkk-universal-validator \
	--namespace tkk-uv \
	--create-namespace
```

## Ingress
- Default ingress host: `tkk.local`
- Frontend route: `/`
- Backend route: `/api`

Set local hosts entry for testing:

```text
127.0.0.1 tkk.local
```

## Scaling
- Backend HPA: min `2`, max `8`, CPU target `70%`
- Frontend HPA: min `2`, max `6`, CPU target `65%`

Manual scale example:

```bash
kubectl scale deploy/tkk-backend --replicas=4 -n tkk-uv
kubectl scale deploy/tkk-frontend --replicas=3 -n tkk-uv
```

## Notes
- This baseline includes in-cluster PostgreSQL and Redis for non-production environments.
- Production deployments should prefer managed PostgreSQL/Redis and external secret stores.
- Prompt 41 observability baseline is documented in `docs/MONITORING_OBSERVABILITY.md`.
- For Kubernetes production observability, deploy Prometheus/Grafana and OpenTelemetry Collector with managed Elastic where possible.
- Prompt 42 backup/restore/migration/DR assets are documented in `docs/BACKUP_RESTORE_DR.md`.

## Prompt 42 Manifests
- `manifests/postgres-backup-cronjob.yaml`: recurring PostgreSQL backups with retention cleanup.
- `manifests/postgres-restore-job.yaml`: one-time restore job from backup storage.
- `manifests/backend-migration-job.yaml`: one-time Alembic migration job.
