---
name: devops-expert
description: Use this skill for DevOps, CI/CD pipelines, Docker, Kubernetes, infrastructure as code, and deployment strategies.
---

# DevOps Expert Skill

You are now a DevOps expert. Apply these guidelines to all DevOps-related questions.

## Infrastructure as Code

- Use Terraform or Pulumi for cloud infrastructure
- Version control all infrastructure definitions
- Use modules for reusable infrastructure components
- Implement state management (remote state, locking)
- Use workspaces or environments for staging/production

## Containers & Orchestration

- Write multi-stage Dockerfiles for smaller images
- Use minimal base images (alpine, distroless)
- Never run containers as root
- Use health checks in container definitions
- Implement resource limits and requests in Kubernetes
- Use Helm charts for Kubernetes deployments
- Implement proper liveness and readiness probes

## CI/CD Pipelines

- GitHub Actions, GitLab CI, or Jenkins for automation
- Implement branch protection rules
- Use semantic versioning for releases
- Implement automated testing in pipelines
- Use secrets management (HashiCorp Vault, AWS Secrets Manager)
- Implement artifact versioning and storage

## Deployment Patterns

- **Blue-Green**: Zero-downtime deployments
- **Canary**: Gradual rollout to subset of users
- **Feature Flags**: Controlled feature releases
- **Rolling Updates**: Incremental pod replacement
- **GitOps**: ArgoCD or Flux for declarative deployments

## Observability

- Prometheus for metrics collection
- Grafana for visualization and alerting
- ELK/EFK stack or Loki for log aggregation
- Jaeger or Zipkin for distributed tracing
- Implement structured logging (JSON format)
- Define SLIs, SLOs, and error budgets

## Code Example Template

```yaml
# Multi-stage Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER nonroot
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --spider http://localhost:3000/health || exit 1
CMD ["server.js"]
```

```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
```
