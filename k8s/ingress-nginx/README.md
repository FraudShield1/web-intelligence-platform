# Ingress-NGINX Installation (Production)

We recommend installing the official ingress-nginx controller via Helm.

Prerequisites:
- Helm v3 installed
- kubectl connected to your cluster

Commands:
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

kubectl create ns ingress-nginx || true

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.metrics.enabled=true \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"=nlb \
  --set controller.replicaCount=2
```

Verify:
```bash
kubectl -n ingress-nginx get svc ingress-nginx-controller
```

Use the LoadBalancer external IP/hostname for DNS A records:
- APP_DOMAIN -> ingress LB
- API_DOMAIN -> ingress LB
