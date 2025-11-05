#!/usr/bin/env bash
set -euo pipefail

# Required env vars:
#   REGISTRY           e.g., ghcr.io/your-org
#   VERSION            e.g., v1.0.0 or $(git rev-parse --short HEAD)
#   API_DOMAIN         e.g., api.example.com
#   APP_DOMAIN         e.g., app.example.com
#   DB_PASSWORD        database password for postgres
#   JWT_SECRET         JWT secret for backend
# Optional:
#   NAMESPACE          default: web-intelligence
#   ANTHROPIC_API_KEY  for future LLM usage
#   PUSH               set to 0 to skip push (default 1)

REGISTRY="${REGISTRY:?REGISTRY is required}"
VERSION="${VERSION:?VERSION is required}"
API_DOMAIN="${API_DOMAIN:?API_DOMAIN is required}"
APP_DOMAIN="${APP_DOMAIN:?APP_DOMAIN is required}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD is required}"
JWT_SECRET="${JWT_SECRET:?JWT_SECRET is required}"
NAMESPACE="${NAMESPACE:-web-intelligence}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
PUSH="${PUSH:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S_DIR="$ROOT_DIR/k8s"
BUILD_BACKEND_IMAGE="$REGISTRY/web-intelligence-backend:$VERSION"
BUILD_FRONTEND_IMAGE="$REGISTRY/web-intelligence-frontend:$VERSION"

# 1) Build images
echo "Building Docker images..."
docker build -t "$BUILD_BACKEND_IMAGE" "$ROOT_DIR/backend"
docker build -t "$BUILD_FRONTEND_IMAGE" "$ROOT_DIR/frontend"

# 2) Push images (optional)
if [[ "$PUSH" != "0" ]]; then
  echo "Pushing images to $REGISTRY..."
  docker push "$BUILD_BACKEND_IMAGE"
  docker push "$BUILD_FRONTEND_IMAGE"
else
  echo "Skipping push (PUSH=$PUSH)"
fi

# 3) Namespace
kubectl get ns "$NAMESPACE" >/dev/null 2>&1 || kubectl create ns "$NAMESPACE"

# 4) cert-manager issuer (optional, if cert-manager installed)
if kubectl api-resources | grep -q cert-manager.io; then
  kubectl apply -f "$K8S_DIR/cert-manager/cluster-issuer.yaml"
else
  echo "cert-manager not detected; skipping ClusterIssuer"
fi

# 5) Create secrets
NAMESPACE="$NAMESPACE" DB_PASSWORD="$DB_PASSWORD" JWT_SECRET="$JWT_SECRET" ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  "$ROOT_DIR/scripts/create_secrets.sh"

# 6) Apply Postgres
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/postgres-deployment.yaml"

# 7) Prepare and apply Backend with image + DB URL substitution
BACKEND_TMP="$(mktemp)"
sed -e "s#web-intelligence:backend-latest#$BUILD_BACKEND_IMAGE#g" \
    -e "s#change-this-password-prod#$DB_PASSWORD#g" \
  "$K8S_DIR/backend-deployment.yaml" > "$BACKEND_TMP"

kubectl apply -n "$NAMESPACE" -f "$BACKEND_TMP"
rm -f "$BACKEND_TMP"

# 8) Prepare and apply Frontend with image + API URL substitution
FRONTEND_TMP="$(mktemp)"
sed -e "s#web-intelligence:frontend-latest#$BUILD_FRONTEND_IMAGE#g" \
    -e "s#https://api.example.com/api/v1#https://$API_DOMAIN/api/v1#g" \
  "$K8S_DIR/frontend-deployment.yaml" > "$FRONTEND_TMP"

kubectl apply -n "$NAMESPACE" -f "$FRONTEND_TMP"
rm -f "$FRONTEND_TMP"

# 9) Ingress with domains
INGRESS_TMP="$(mktemp)"
API_DOMAIN="$API_DOMAIN" APP_DOMAIN="$APP_DOMAIN" envsubst < "$K8S_DIR/ingress.yaml" > "$INGRESS_TMP"
kubectl apply -n "$NAMESPACE" -f "$INGRESS_TMP"
rm -f "$INGRESS_TMP"

# 10) Monitoring stack
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/monitoring-stack.yaml"

# 11) Run DB migrations as a Job
MIGRATE_TMP="$(mktemp)"
sed -e "s#web-intelligence:backend-latest#$BUILD_BACKEND_IMAGE#g" \
  "$K8S_DIR/migrate-job.yaml" > "$MIGRATE_TMP"

kubectl delete job db-migrate -n "$NAMESPACE" --ignore-not-found
kubectl apply -n "$NAMESPACE" -f "$MIGRATE_TMP"
rm -f "$MIGRATE_TMP"

# Wait for migration completion
kubectl wait --for=condition=complete job/db-migrate -n "$NAMESPACE" --timeout=180s || true

# 12) Wait for readiness
echo "Waiting for backend and frontend to be ready..."
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=180s || true
kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout=180s || true

# 13) Summary
cat <<EOF

✅ Deployment triggered
Namespace:     $NAMESPACE
Backend image: $BUILD_BACKEND_IMAGE
Frontend image:$BUILD_FRONTEND_IMAGE
API domain:    $API_DOMAIN
App domain:    $APP_DOMAIN

Next:
- Ensure ingress-nginx and cert-manager installed
- Point DNS A records of $API_DOMAIN and $APP_DOMAIN to the Ingress LB
- Verify:   curl -s https://$API_DOMAIN/health | jq
- Open app: https://$APP_DOMAIN
EOF
