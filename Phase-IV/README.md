# Phase IV: Containerized & Kubernetes-Deployed AI Todo Application

**Status**: ✅ Complete (Docker + Kubernetes Deployment)
**Last Updated**: 2026-02-12
**Branch**: `001-todo`

## Overview

Phase IV extends Phase III by containerizing the application with Docker and deploying it to a local Kubernetes cluster (Minikube). This phase demonstrates production-ready deployment practices with container orchestration, service discovery, and scalable infrastructure.

### What's New in Phase IV

- ✅ **Docker Containerization**: Multi-stage Dockerfiles for optimized production images
- ✅ **Kubernetes Deployment**: Helm charts for declarative infrastructure
- ✅ **Service Discovery**: Internal DNS-based communication between services
- ✅ **Local Kubernetes**: Minikube deployment for local development and testing
- ✅ **Port Forwarding**: Secure access to services via kubectl port-forward
- ✅ **Production-Ready Images**: Optimized Docker images with security best practices
- ✅ **Helm Charts**: Reusable deployment templates with values configuration

### Inherited Features from Phase III

- ✅ **AI Chat Assistant**: Natural language task management through conversational interface
- ✅ **MCP Tools Integration**: Model Context Protocol tools for structured task operations
- ✅ **Real-time Streaming**: Token-by-token response streaming for better UX
- ✅ **Tool Call Transparency**: Users see exactly what actions the AI is performing
- ✅ **Conversation Persistence**: Chat history stored and retrieved across sessions
- ✅ **Multi-Provider Support**: Groq (primary) and OpenAI (fallback) for reliability
- ✅ **User Authentication**: Secure JWT-based authentication
- ✅ **Task Management**: Full CRUD operations for tasks

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Local Machine                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Minikube (Kubernetes Cluster)             │ │
│  │                                                        │ │
│  │  ┌──────────────────┐      ┌──────────────────┐      │ │
│  │  │  Backend Pod     │      │  Frontend Pod    │      │ │
│  │  │                  │      │                  │      │ │
│  │  │  FastAPI         │      │  Next.js         │      │ │
│  │  │  Port: 8000      │      │  Port: 3000      │      │ │
│  │  │                  │      │                  │      │ │
│  │  │  Image:          │      │  Image:          │      │ │
│  │  │  phase-iv-       │      │  phase-iv-       │      │ │
│  │  │  backend:latest  │      │  frontend:latest │      │ │
│  │  └────────┬─────────┘      └────────┬─────────┘      │ │
│  │           │                         │                │ │
│  │  ┌────────▼─────────┐      ┌────────▼─────────┐      │ │
│  │  │ Backend Service  │      │ Frontend Service │      │ │
│  │  │ (ClusterIP)      │      │ (NodePort)       │      │ │
│  │  │ 10.109.6.1:8000  │      │ 10.98.157.21:3000│      │ │
│  │  └──────────────────┘      └──────────────────┘      │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Port Forwarding (kubectl)                 │ │
│  │                                                        │ │
│  │  localhost:8000 ──────────► Backend Service           │ │
│  │  localhost:3000 ──────────► Frontend Service          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Browser Access                        │ │
│  │                                                        │ │
│  │  http://localhost:3000 ──► Frontend                   │ │
│  │  http://localhost:8000 ──► Backend API                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

External Services:
├── Neon PostgreSQL (Cloud Database)
├── Groq API (Primary LLM Provider)
└── OpenAI API (Fallback LLM Provider)
```

### Technology Stack

**Backend**:
- **Framework**: FastAPI (Python 3.13+)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel with Alembic migrations
- **AI Integration**: OpenAI Agents SDK
- **LLM Providers**:
  - Primary: Groq (openai/gpt-oss-20b)
  - Fallback: OpenAI (gpt-4o-mini)
- **Authentication**: PyJWT for token verification
- **Testing**: pytest with async support
- **Container**: Docker multi-stage build (Python 3.13-slim)
- **Package Manager**: UV for fast dependency management

**Frontend**:
- **Framework**: Next.js 15.5.12 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Authentication**: Better Auth with JWT plugin
- **UI Components**: Custom Soft Dark theme with glassmorphism
- **Container**: Docker multi-stage build (Node 20-alpine)
- **Output Mode**: Standalone for optimized Docker deployment

**Infrastructure**:
- **Orchestration**: Kubernetes (Minikube for local)
- **Package Manager**: Helm 3.x
- **Container Runtime**: Docker
- **Service Discovery**: Kubernetes DNS
- **Networking**: ClusterIP (backend), NodePort (frontend)
- **Access**: kubectl port-forward

**AI Agent Architecture**:
- **Agent Factory**: Creates and configures AI agents with MCP tools
- **Runner Factory**: Manages OpenAI ChatCompletions with retry logic
- **MCP Adapter**: Converts MCP tools to OpenAI function calling format
- **Agent Orchestration**: Coordinates agent execution, tool calls, and persistence
- **History Manager**: Manages conversation history with truncation

### Project Structure

```
Phase-IV/
├── backend/
│   ├── Dockerfile.production      # Production-optimized Dockerfile
│   ├── .dockerignore             # Docker build exclusions
│   ├── src/
│   │   ├── agent/
│   │   │   ├── agent_factory.py      # AI agent creation
│   │   │   ├── runner_factory.py     # OpenAI client management
│   │   │   ├── mcp_adapter.py        # MCP tool integration
│   │   │   ├── instructions.py       # System prompt
│   │   │   ├── history_manager.py    # Conversation truncation
│   │   │   └── guardrails.py         # Confirmation management
│   │   ├── mcp/
│   │   │   └── tools/
│   │   │       ├── add_task.py       # Create task tool
│   │   │       ├── list_tasks.py     # List tasks tool
│   │   │       ├── update_task.py    # Update task tool
│   │   │       ├── complete_task.py  # Complete task tool
│   │   │       └── delete_task.py    # Delete task tool
│   │   ├── use_cases/
│   │   │   └── agent_orchestration.py # Agent workflow coordination
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── chat.py           # Chat endpoint
│   │   │       ├── chat_stream.py    # Streaming chat endpoint
│   │   │       ├── conversations.py  # Conversation management
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       └── tasks.py          # Task CRUD endpoints
│   │   └── domain/
│   │       └── models.py             # Database models
│   └── tests/
│       └── integration/              # E2E tests
│
├── frontend/
│   ├── Dockerfile                    # Production-optimized Dockerfile
│   ├── .dockerignore                # Docker build exclusions
│   ├── next.config.ts               # Next.js config (standalone mode)
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/            # Main dashboard with chat widget
│   │   │   ├── chat/                 # Chat page
│   │   │   ├── login/                # Login page
│   │   │   └── register/             # Registration page
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWidget.tsx    # Floating chat widget
│   │   │   │   ├── ChatInterface.tsx # Chat UI
│   │   │   │   ├── MessageList.tsx   # Message display
│   │   │   │   ├── ChatInput.tsx     # Message input
│   │   │   │   └── ToolCallIndicator.tsx # Tool execution display
│   │   │   ├── navigation/
│   │   │   │   ├── Sidebar.tsx       # Main navigation
│   │   │   │   └── TopNavigation.tsx # Top bar
│   │   │   └── tasks/
│   │   │       └── TaskCard.tsx      # Task display component
│   │   ├── lib/
│   │   │   ├── api-client.ts         # API client with auth
│   │   │   └── api/
│   │   │       └── chat-client.ts    # Chat-specific API client
│   │   └── hooks/
│   │       ├── useAuth.tsx           # Authentication hook
│   │       └── useChat.tsx           # Chat management hook
│   └── package.json
│
└── todo-chatbot/                     # Helm chart
    ├── Chart.yaml                    # Chart metadata
    ├── values.yaml                   # Configuration values
    └── templates/
        ├── backend-deployment.yaml   # Backend Kubernetes deployment
        ├── backend-service.yaml      # Backend service
        ├── frontend-deployment.yaml  # Frontend Kubernetes deployment
        ├── frontend-service.yaml     # Frontend service
        ├── serviceaccount.yaml       # Service account
        └── NOTES.txt                 # Post-install instructions
```

## AI Chat Features

### Conversational Task Management

Users can manage tasks through natural language:

**Examples**:
- "Add a task to buy groceries"
- "Mark the medicine task as complete"
- "Delete the task named bro"
- "Show me all my pending tasks"
- "Update the grocery task description to include milk and eggs"

### MCP Tools

The AI assistant has access to 5 MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create a new task | `title`, `description` (optional) |
| `list_tasks` | List user's tasks | `status` (optional: pending/completed/all) |
| `update_task` | Update existing task | `task_id`, `title`, `description` |
| `complete_task` | Toggle task completion | `task_id` |
| `delete_task` | Delete a task | `task_id` |

### Tool Call Transparency

Every tool execution is displayed to the user with:
- Tool name
- Input parameters
- Output result
- Execution status (success/error)
- Timestamp

### Conversation Flow

```
User: "Add a task to buy groceries"
  ↓
AI Agent: Processes intent
  ↓
Tool Call: add_task(title="buy groceries")
  ↓
Database: Creates task
  ↓
AI Response: "I've created a task for you: 'buy groceries'"
  ↓
User sees: Message + Tool execution details
```

## API Endpoints

### Chat Endpoints (Protected)

All chat endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | `/api/{user_id}/chat` | Send message to AI | `{ conversation_id, response, tool_calls }` |
| POST | `/api/{user_id}/chat/stream` | Stream AI response | Server-Sent Events |
| GET | `/api/{user_id}/conversations` | List conversations | `[{ id, created_at, ... }]` |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get conversation history | `[{ role, content, ... }]` |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation | `{ message }` |

### Authentication & Task Endpoints

See Phase II documentation for authentication and task management endpoints.

## Setup Instructions

### Prerequisites

- **Docker**: 20.x+ (for building images)
- **Kubernetes**: Minikube 1.30+ (for local deployment)
- **Helm**: 3.x+ (for deploying charts)
- **kubectl**: 1.28+ (for cluster management)
- **Node.js**: 18.x+ (for local frontend development)
- **Python**: 3.13+ (for local backend development)
- **UV**: Latest (Python package manager)
- **Neon PostgreSQL**: Account with database
- **Groq API**: Key for primary LLM provider
- **OpenAI API**: Key for fallback (optional)

### Environment Variables

**Backend (`.env`)**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=<32+ character secret>
FRONTEND_URL=http://localhost:3000

# AI Providers
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=<your-openai-api-key>  # Optional fallback
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_FALLBACK_ENABLED=true

# Agent Configuration
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_MAX_HISTORY_MESSAGES=20

# CORS
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=3600
```

**Frontend (`.env.local`)**:
```bash
BETTER_AUTH_SECRET=<same as backend>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=<same as backend>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker Deployment

#### Step 1: Build Docker Images

**Build Backend Image:**
```bash
cd Phase-IV/backend
docker build -f Dockerfile.production -t phase-iv-backend:latest .
```

**Build Frontend Image:**
```bash
cd Phase-IV/frontend
docker build -t phase-iv-frontend:latest .
```

**Verify Images:**
```bash
docker images | grep phase-iv
```

#### Step 2: Run with Docker (Optional)

**Run Backend Container:**
```bash
docker run -d \
  --name phase-iv-backend \
  -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e BETTER_AUTH_SECRET="your-secret" \
  -e GROQ_API_KEY="your-groq-key" \
  -e FRONTEND_URL="http://localhost:3000" \
  phase-iv-backend:latest
```

**Run Frontend Container:**
```bash
docker run -d \
  --name phase-iv-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e BETTER_AUTH_SECRET="your-secret" \
  -e DATABASE_URL="your-database-url" \
  phase-iv-frontend:latest
```

### Kubernetes Deployment (Recommended)

#### Step 1: Start Minikube

```bash
minikube start
```

#### Step 2: Load Images into Minikube

```bash
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest
```

**Verify Images:**
```bash
minikube image ls | grep phase-iv
```

#### Step 3: Update Helm Values

Edit `todo-chatbot/values.yaml` with your environment variables:

```yaml
backend:
  env:
    - name: DATABASE_URL
      value: "your-database-url"
    - name: BETTER_AUTH_SECRET
      value: "your-secret"
    - name: GROQ_API_KEY
      value: "your-groq-key"
    # ... other variables

frontend:
  env:
    - name: NEXT_PUBLIC_API_URL
      value: "http://backend-service:8000"
    - name: BETTER_AUTH_SECRET
      value: "your-secret"
    - name: DATABASE_URL
      value: "your-database-url"
```

#### Step 4: Deploy with Helm

```bash
cd Phase-IV/todo-chatbot
helm install phase-iv-app . --namespace default
```

**Check Deployment Status:**
```bash
kubectl get pods -l app.kubernetes.io/instance=phase-iv-app
kubectl get services -l app.kubernetes.io/instance=phase-iv-app
```

#### Step 5: Access the Application

**Set up Port Forwarding:**
```bash
# Backend (in one terminal)
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000

# Frontend (in another terminal)
kubectl port-forward svc/phase-iv-app-todo-chatbot-frontend 3000:3000
```

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Running Locally (Development)

For local development without Docker/Kubernetes:

**Terminal 1 - Backend**:
```bash
cd Phase-IV/backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd Phase-IV/frontend
npm run dev
```

**Access**:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Testing

### Backend Tests

```bash
cd Phase-IV/backend

# Run all tests
uv run pytest

# Run integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Docker Image Testing

**Test Backend Image:**
```bash
docker run --rm phase-iv-backend:latest python -c "import src.main; print('Backend OK')"
```

**Test Frontend Image:**
```bash
docker run --rm phase-iv-frontend:latest node --version
```

### Kubernetes Deployment Testing

**Check Pod Status:**
```bash
kubectl get pods -l app.kubernetes.io/instance=phase-iv-app
```

**Check Service Endpoints:**
```bash
kubectl get endpoints
```

**Test Backend Health:**
```bash
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 &
curl http://localhost:8000/health
```

**View Logs:**
```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -f

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f
```

### Manual Testing

**Test AI Chat Flow**:
```bash
# 1. Register and login to get token
TOKEN="<your-jwt-token>"
USER_ID="<your-user-id>"

# 2. Send chat message
curl -X POST http://localhost:8000/api/${USER_ID}/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# 3. List conversations
curl http://localhost:8000/api/${USER_ID}/conversations \
  -H "Authorization: Bearer ${TOKEN}"

# 4. Get conversation messages
curl http://localhost:8000/api/${USER_ID}/conversations/1/messages \
  -H "Authorization: Bearer ${TOKEN}"
```

## Deployment

### Local Kubernetes Deployment (Current)

**Status**: ✅ Deployed to Minikube
**Access**: Via kubectl port-forward

**Deployment Details**:
- **Cluster**: Minikube (local Kubernetes)
- **Namespace**: default
- **Helm Release**: phase-iv-app
- **Backend Service**: ClusterIP (internal)
- **Frontend Service**: NodePort (external)
- **Images**: Loaded locally (not from registry)

**Access URLs**:
- Frontend: http://localhost:3000 (via port-forward)
- Backend: http://localhost:8000 (via port-forward)

**Helm Commands**:
```bash
# View deployment
helm list

# Get deployment status
helm status phase-iv-app

# Upgrade deployment
helm upgrade phase-iv-app ./todo-chatbot

# Rollback deployment
helm rollback phase-iv-app

# Uninstall deployment
helm uninstall phase-iv-app
```

### Production Deployment (Future)

For production deployment to cloud Kubernetes:

#### Step 1: Push Images to Registry

```bash
# Tag images for registry
docker tag phase-iv-backend:latest your-registry/phase-iv-backend:v1.0.0
docker tag phase-iv-frontend:latest your-registry/phase-iv-frontend:v1.0.0

# Push to registry
docker push your-registry/phase-iv-backend:v1.0.0
docker push your-registry/phase-iv-frontend:v1.0.0
```

#### Step 2: Update Helm Values for Production

```yaml
# values-production.yaml
backend:
  image:
    repository: your-registry/phase-iv-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP

  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-url
    - name: GROQ_API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: groq-api-key

frontend:
  image:
    repository: your-registry/phase-iv-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent

  service:
    type: LoadBalancer  # or use Ingress

  env:
    - name: NEXT_PUBLIC_API_URL
      value: "https://api.yourdomain.com"

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: app.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.yourdomain.com
```

#### Step 3: Create Kubernetes Secrets

```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url="your-production-db-url" \
  --from-literal=groq-api-key="your-groq-key" \
  --from-literal=better-auth-secret="your-secret"
```

#### Step 4: Deploy to Production Cluster

```bash
# Set kubectl context to production cluster
kubectl config use-context production-cluster

# Deploy with production values
helm install phase-iv-app ./todo-chatbot \
  -f values-production.yaml \
  --namespace production \
  --create-namespace
```

#### Step 5: Configure DNS and SSL

```bash
# Get LoadBalancer IP or Ingress address
kubectl get ingress -n production

# Point your domain DNS to the IP/address
# Configure SSL certificate (Let's Encrypt, etc.)
```

### Cloud Provider Options

**AWS EKS**:
- Use ECR for container registry
- Configure ALB Ingress Controller
- Use RDS for PostgreSQL (or keep Neon)
- Set up CloudWatch for logging

**Google GKE**:
- Use GCR for container registry
- Configure GKE Ingress
- Use Cloud SQL (or keep Neon)
- Set up Cloud Logging

**Azure AKS**:
- Use ACR for container registry
- Configure Application Gateway Ingress
- Use Azure Database for PostgreSQL (or keep Neon)
- Set up Azure Monitor

### Database Migrations

```bash
# Run migrations in Kubernetes
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') \
  -- alembic upgrade head
```

## Recent Changes

### 2026-02-12 (Phase IV)
- ✅ **Docker Containerization**: Created production-optimized Dockerfiles for backend and frontend
- ✅ **Kubernetes Deployment**: Deployed to local Minikube cluster with Helm charts
- ✅ **Service Discovery**: Configured internal DNS for pod-to-pod communication
- ✅ **Port Forwarding**: Set up kubectl port-forward for local access
- ✅ **Multi-stage Builds**: Optimized Docker images with multi-stage builds
- ✅ **Helm Charts**: Created reusable deployment templates with configurable values
- ✅ **Health Checks**: Configured liveness and readiness probes
- ✅ **Resource Limits**: Set CPU and memory limits for pods
- ✅ **Non-root Users**: Security hardening with non-root container users
- ✅ **Image Loading**: Successfully loaded images into Minikube
- ✅ **Full Stack Testing**: Verified authentication, chat, and task operations in Kubernetes

### 2026-02-11 (Phase III)
- ✅ Removed AI Chat navigation from sidebar (chat accessible via widget only)
- ✅ Removed non-functional search bar from top navigation
- ✅ Restored to working state after glassmorphism UI issues
- ✅ Deployed to production (Netlify)

### Key Implementation Details
- Docker images built with security best practices (non-root users, minimal base images)
- Kubernetes deployment uses ClusterIP for backend (internal) and NodePort for frontend
- Helm charts provide declarative infrastructure with easy configuration
- Port-forwarding enables local access without exposing services publicly
- All Phase III features (AI chat, task management, authentication) working in Kubernetes

## Troubleshooting

### Docker Issues

**Issue**: Docker build fails with "no space left on device"
**Solution**: Clean up Docker resources
```bash
docker system prune -a
docker volume prune
```

**Issue**: Image build is very slow
**Solution**: Use .dockerignore to exclude unnecessary files, check Docker daemon resources

**Issue**: Container exits immediately after starting
**Solution**: Check container logs
```bash
docker logs <container-name>
```

### Kubernetes Issues

**Issue**: Pods stuck in "Pending" state
**Solution**: Check pod events and node resources
```bash
kubectl describe pod <pod-name>
kubectl get nodes
kubectl top nodes
```

**Issue**: Pods in "CrashLoopBackOff" state
**Solution**: Check pod logs and events
```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

**Issue**: "ImagePullBackOff" error
**Solution**: Verify image exists in Minikube
```bash
minikube image ls | grep phase-iv
# If missing, reload image
minikube image load phase-iv-backend:latest
```

**Issue**: Port-forward connection refused
**Solution**: Verify service and pod are running
```bash
kubectl get svc
kubectl get pods
# Kill existing port-forward processes
pkill -f "port-forward"
# Restart port-forward
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 &
```

**Issue**: Frontend shows "not found" for API calls
**Solution**: Ensure backend is port-forwarded to correct port (8000)
```bash
# Check what port frontend expects
grep NEXT_PUBLIC_API_URL Phase-IV/frontend/.env.local
# Ensure backend port-forward matches
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000
```

**Issue**: Services can't communicate internally
**Solution**: Check service DNS and endpoints
```bash
kubectl get endpoints
kubectl exec -it <frontend-pod> -- nslookup phase-iv-app-todo-chatbot-backend
```

### Application Issues

**Issue**: AI responses are empty or incomplete
**Solution**: Check that `GROQ_API_KEY` is valid and has sufficient credits

**Issue**: Tool calls fail with "User not found"
**Solution**: Ensure JWT token is valid and user_id matches token claims

**Issue**: Chat shows 404 error
**Solution**: Verify you're logged in and the chat endpoint includes user_id in the path

**Issue**: Delete task not working
**Solution**: Ensure you're authenticated and the task belongs to your user

**Issue**: "Rate limit exceeded" errors
**Solution**: Fallback to OpenAI is automatic if `OPENAI_FALLBACK_ENABLED=true`

**Issue**: Conversation history not loading
**Solution**: Run database migrations to ensure `conversations` and `messages` tables exist

### Minikube Issues

**Issue**: Minikube won't start
**Solution**: Check Docker daemon and system resources
```bash
minikube delete
minikube start --driver=docker
```

**Issue**: Can't access services via NodePort
**Solution**: Use port-forward instead (Minikube with Docker driver on Linux doesn't expose NodePort directly)
```bash
kubectl port-forward svc/<service-name> <local-port>:<service-port>
```

**Issue**: Minikube running out of resources
**Solution**: Increase Minikube resources
```bash
minikube delete
minikube start --cpus=4 --memory=8192
```

## Development Workflow

### Making Changes

1. **Backend AI changes**: Modify files in `src/agent/` or `src/mcp/tools/`
2. **Frontend chat UI**: Modify files in `src/components/chat/`
3. **System prompt**: Edit `src/agent/instructions.py`
4. **Add new MCP tool**: Create tool in `src/mcp/tools/` and register in `mcp_adapter.py`
5. **Docker configuration**: Update `Dockerfile` or `Dockerfile.production`
6. **Kubernetes configuration**: Update Helm chart templates in `todo-chatbot/templates/`
7. **Deployment values**: Modify `todo-chatbot/values.yaml`

### Local Development Cycle

**Option 1: Direct Development (Fastest)**
```bash
# Run backend locally
cd Phase-IV/backend
uv run uvicorn src.main:app --reload --port 8000

# Run frontend locally
cd Phase-IV/frontend
npm run dev
```

**Option 2: Docker Development**
```bash
# Rebuild and run backend
cd Phase-IV/backend
docker build -f Dockerfile.production -t phase-iv-backend:latest .
docker run -p 8000:8000 --env-file .env phase-iv-backend:latest

# Rebuild and run frontend
cd Phase-IV/frontend
docker build -t phase-iv-frontend:latest .
docker run -p 3000:3000 --env-file .env.local phase-iv-frontend:latest
```

**Option 3: Kubernetes Development**
```bash
# Rebuild images
docker build -f Dockerfile.production -t phase-iv-backend:latest ./backend
docker build -t phase-iv-frontend:latest ./frontend

# Load into Minikube
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest

# Upgrade Helm deployment
helm upgrade phase-iv-app ./todo-chatbot

# Restart pods to use new images
kubectl rollout restart deployment phase-iv-app-todo-chatbot-backend
kubectl rollout restart deployment phase-iv-app-todo-chatbot-frontend
```

### Testing Changes

**Test Backend Changes:**
```bash
# Unit tests
cd Phase-IV/backend
uv run pytest

# Test in Docker
docker run --rm phase-iv-backend:latest pytest

# Test in Kubernetes
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- pytest
```

**Test Frontend Changes:**
```bash
# Build test
cd Phase-IV/frontend
npm run build

# Test in Docker
docker build -t phase-iv-frontend:test .
docker run --rm phase-iv-frontend:test node --version
```

### Debugging in Kubernetes

**Access Pod Shell:**
```bash
# Backend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- /bin/bash

# Frontend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh
```

**View Real-time Logs:**
```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -f

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f

# All pods
kubectl logs -l app.kubernetes.io/instance=phase-iv-app -f --all-containers
```

**Check Environment Variables:**
```bash
kubectl exec $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- env | grep -E "DATABASE|GROQ|AUTH"
```

### Testing AI Behavior

```bash
# Test with different prompts
curl -X POST http://localhost:8000/api/${USER_ID}/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your test prompt here"}'
```

## Resources

### Documentation

- **API Documentation**: http://localhost:8000/docs (when backend running)
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-sdk
- **Groq Documentation**: https://console.groq.com/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

### Docker & Kubernetes

- **Docker Documentation**: https://docs.docker.com
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices
- **Kubernetes Documentation**: https://kubernetes.io/docs
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs
- **Helm Documentation**: https://helm.sh/docs
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet

### Container Registries

- **Docker Hub**: https://hub.docker.com
- **AWS ECR**: https://aws.amazon.com/ecr
- **Google GCR**: https://cloud.google.com/container-registry
- **Azure ACR**: https://azure.microsoft.com/en-us/services/container-registry

### Cloud Kubernetes Services

- **AWS EKS**: https://aws.amazon.com/eks
- **Google GKE**: https://cloud.google.com/kubernetes-engine
- **Azure AKS**: https://azure.microsoft.com/en-us/services/kubernetes-service
- **DigitalOcean Kubernetes**: https://www.digitalocean.com/products/kubernetes

## Contributing

When adding new features:

1. **Follow existing code patterns and architecture**
   - Backend: FastAPI with async/await patterns
   - Frontend: Next.js App Router with TypeScript
   - Docker: Multi-stage builds with security best practices
   - Kubernetes: Declarative configuration with Helm

2. **Add MCP tools for new AI capabilities**
   - Create tool in `src/mcp/tools/`
   - Register in `mcp_adapter.py`
   - Update system instructions if needed
   - Add integration tests

3. **Update Docker images when dependencies change**
   - Update `requirements.txt` or `package.json`
   - Rebuild Docker images
   - Test locally before deploying

4. **Update Helm charts for infrastructure changes**
   - Modify templates in `todo-chatbot/templates/`
   - Update `values.yaml` with new configuration
   - Test deployment in Minikube

5. **Add tests for new functionality**
   - Unit tests for business logic
   - Integration tests for API endpoints
   - Docker image tests
   - Kubernetes deployment tests

6. **Update documentation**
   - Update this README with new features
   - Document new environment variables
   - Add troubleshooting tips
   - Update API documentation

7. **Test locally before deploying**
   - Test in local development environment
   - Test in Docker containers
   - Test in Kubernetes (Minikube)
   - Verify all features work end-to-end

## Summary

Phase IV successfully containerizes and deploys the AI-powered todo application to Kubernetes, demonstrating production-ready deployment practices. The application runs in a local Minikube cluster with:

- **Containerized Services**: Backend and frontend running in optimized Docker containers
- **Kubernetes Orchestration**: Managed by Helm charts with declarative configuration
- **Service Discovery**: Internal DNS-based communication between pods
- **Scalability**: Ready to scale horizontally with Kubernetes replica sets
- **Production-Ready**: Security hardening, health checks, resource limits
- **Cloud-Ready**: Easy migration to AWS EKS, GKE, or AKS

**Current Status**: ✅ Fully functional in local Kubernetes
**Next Steps**: Deploy to cloud Kubernetes for production use

## License

[Your License Here]

---

**Questions or Issues?**
- Check the troubleshooting section for common issues
- Review Phase III documentation for AI chat features
- Review Phase II documentation for authentication setup
- Consult Kubernetes and Docker documentation for infrastructure questions
