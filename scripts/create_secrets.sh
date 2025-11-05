#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   NAMESPACE=web-intelligence DB_PASSWORD=... JWT_SECRET=... [ANTHROPIC_API_KEY=...] ./scripts/create_secrets.sh

NAMESPACE="${NAMESPACE:-web-intelligence}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${JWT_SECRET:?JWT_SECRET is required}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"

kubectl get ns "$NAMESPACE" >/dev/null 2>&1 || kubectl create ns "$NAMESPACE"

echo "Creating/Updating postgres-secret in $NAMESPACE..."
kubectl -n "$NAMESPACE" create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Creating/Updating backend-secrets in $NAMESPACE..."
SECRETS_ARGS=(
  --from-literal=SECRET_KEY="$JWT_SECRET"
)
if [[ -n "$ANTHROPIC_API_KEY" ]]; then
  SECRETS_ARGS+=( --from-literal=ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" )
fi

kubectl -n "$NAMESPACE" create secret generic backend-secrets \
  "${SECRETS_ARGS[@]}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets applied."
