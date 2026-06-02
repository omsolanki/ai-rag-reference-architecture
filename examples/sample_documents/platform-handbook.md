# Platform Engineering Handbook

## Deployment Guidelines

Our platform uses Kubernetes for container orchestration across all environments. Production workloads run on AWS EKS with a minimum of three availability zones for high availability.

### Deployment Pipeline

The CI/CD pipeline follows a GitOps model:

1. Code merged to main triggers automated tests
2. Container images built and pushed to ECR
3. ArgoCD syncs manifests to the target cluster
4. Health checks validate deployment before traffic shift

### Environment Strategy

| Environment | Purpose | Cluster |
|-------------|---------|---------|
| Development | Feature testing | dev-eks |
| Staging | Pre-production validation | staging-eks |
| Production | Live workloads | prod-eks |

Rollbacks are performed via `kubectl rollout undo` or ArgoCD revision rollback. All deployments require at least two healthy replicas before receiving traffic.

## Observability Standards

All services must expose Prometheus metrics on `/metrics` and structured JSON logs with correlation IDs. Distributed tracing uses OpenTelemetry with export to the central collector.

Key SLIs:
- Availability: 99.9% uptime
- Latency P95: < 500ms for API endpoints
- Error rate: < 0.1%

## Security Requirements

All services must authenticate via OIDC. Secrets are managed through AWS Secrets Manager with rotation enabled. No credentials in source code or environment variables in production.

Data classification levels:
- Public: No restrictions
- Internal: Employee access only
- Confidential: Role-based access with audit logging
- Restricted: Executive approval required
