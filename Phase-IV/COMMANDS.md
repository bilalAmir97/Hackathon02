# Phase-IV Deployment Commands Reference

## Docker Build Commands

### Build Backend Image
```bash
cd Phase-IV/backend
docker build -f Dockerfile.production -t phase-iv-backend:latest .
```

### Build Frontend Image
```bash
cd Phase-IV/frontend
docker build -t phase-iv-frontend:latest .
```

## Minikube Setup

### Start Minikube
```bash
minikube start
```

### Load Images into Minikube
```bash
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest
```

### Get Minikube IP
```bash
minikube ip
```

## Helm Deployment

### Install Application
```bash
cd Phase-IV/todo-chatbot
helm install phase-iv-app . -f values.yaml -f values-local.yaml
```

### Upgrade Application (after changes)
```bash
helm upgrade phase-iv-app . -f values.yaml -f values-local.yaml
```

### Uninstall Application
```bash
helm uninstall phase-iv-app
```

## Port Forwarding (Required for Local Access)

### Backend Port-Forward (run in background)
```bash
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 > /tmp/backend-pf.log 2>&1 &
```

### Frontend Port-Forward (run in background)
```bash
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-frontend 3000:3000 > /tmp/frontend-pf.log 2>&1 &
```

### Check Port-Forward Processes
```bash
ps aux | grep "kubectl port-forward" | grep -v grep
```

### Kill Port-Forward Processes
```bash
pkill -f "kubectl port-forward"
```

## Kubernetes Monitoring

### Check Pod Status
```bash
kubectl get pods -n default
```

### Check Services
```bash
kubectl get svc -n default
```

### View Backend Logs
```bash
kubectl logs -f phase-iv-app-todo-chatbot-backend-<pod-id>
```

### View Frontend Logs
```bash
kubectl logs -f phase-iv-app-todo-chatbot-frontend-<pod-id>
```

### Describe Pod (for troubleshooting)
```bash
kubectl describe pod phase-iv-app-todo-chatbot-backend-<pod-id>
```

### Restart Deployment
```bash
kubectl rollout restart deployment phase-iv-app-todo-chatbot-backend
kubectl rollout restart deployment phase-iv-app-todo-chatbot-frontend
```

## Access Application

### Frontend URL
```
http://localhost:3000
```

### Backend API URL
```
http://localhost:8000
```

### Backend Health Check
```bash
curl http://localhost:8000/health
```

## Quick Start (Full Deployment)

```bash
# 1. Start Minikube
minikube start

# 2. Build Docker images
cd Phase-IV/backend
docker build -f Dockerfile.production -t phase-iv-backend:latest .
cd ../frontend
docker build -t phase-iv-frontend:latest .

# 3. Load images into Minikube
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest

# 4. Deploy with Helm
cd ../todo-chatbot
helm install phase-iv-app . -f values.yaml -f values-local.yaml

# 5. Wait for pods to be ready
kubectl get pods -w

# 6. Start port-forwards
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 > /tmp/backend-pf.log 2>&1 &
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-frontend 3000:3000 > /tmp/frontend-pf.log 2>&1 &

# 7. Access application at http://localhost:3000
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -ti:8000
lsof -ti:3000

# Kill process
kill -9 <PID>
```

### Pod Not Starting
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check previous container logs (if restarted)
kubectl logs <pod-name> --previous
```

### Rebuild and Redeploy
```bash
# Rebuild images
docker build -f Dockerfile.production -t phase-iv-backend:latest Phase-IV/backend
docker build -t phase-iv-frontend:latest Phase-IV/frontend

# Reload into Minikube
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest

# Restart deployments
kubectl rollout restart deployment phase-iv-app-todo-chatbot-backend
kubectl rollout restart deployment phase-iv-app-todo-chatbot-frontend
```

## Git Commands

### Push to GitHub
```bash
git add .
git commit -m "your commit message"
git push origin 001-todo
```

### Force Push (use with caution)
```bash
git push --force origin 001-todo
```
