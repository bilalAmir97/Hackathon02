# AI-Powered Todo Application - Full Stack Journey

**Project Status**: ✅ Phase IV Complete (Containerized & Kubernetes-Deployed)
**Last Updated**: 2026-02-12
**Branch**: `001-todo`
**Live Demo**: [https://rainbow-froyo-cda32b.netlify.app](https://rainbow-froyo-cda32b.netlify.app)

## 🚀 Project Overview

A comprehensive full-stack todo application that evolved from a simple console app to a production-ready, AI-powered, containerized application deployed on Kubernetes. This project demonstrates modern software development practices including authentication, AI integration, containerization, and cloud-native deployment.

### Project Evolution

```
Phase I: Console Application
    ↓
Phase II: Full-Stack Web App + Authentication
    ↓
Phase III: AI-Powered Conversational Interface
    ↓
Phase IV: Docker + Kubernetes Deployment
```

## 📊 Phase-by-Phase Evolution

### Phase I: Console Todo Application
**Status**: ✅ Complete
**Description**: Command-line todo application with basic CRUD operations

**Features**:
- Console-based task management
- In-memory data storage
- Basic CRUD operations (Create, Read, Update, Delete)
- Task status management (pending/completed)

---

### Phase II: Full-Stack Web Application with Authentication
**Status**: ✅ Complete
**Branch**: `001-auth-security-integration`
**Documentation**: [Phase-II/README.md](Phase-II/README.md)

**Key Features**:
- ✅ **User Authentication**: Secure registration and login with JWT tokens
- ✅ **User Isolation**: Each user can only access their own data
- ✅ **Token Security**: 30-minute token expiration with comprehensive validation
- ✅ **RESTful API**: FastAPI backend with OpenAPI documentation
- ✅ **Modern Frontend**: Next.js 16+ with Better Auth integration
- ✅ **Production-Ready**: Structured logging, performance monitoring, CORS configuration

**Technology Stack**:
- **Backend**: FastAPI (Python 3.13+), Neon PostgreSQL, SQLModel, PyJWT
- **Frontend**: Next.js 16.0.10, TypeScript, Tailwind CSS v4, Better Auth
- **Security**: JWT tokens, Bcrypt password hashing, 6-layer token validation

**Architecture Highlights**:
- JWT-based authentication with 30-minute expiration
- User-scoped data isolation enforced at every endpoint
- Structured logging for authentication events
- Performance monitoring (10-30ms typical auth time)
- 79+ comprehensive tests (contract, unit, integration)

---

### Phase III: AI-Powered Conversational Interface
**Status**: ✅ Complete
**Branch**: `001-todo`
**Documentation**: [Phase-III/README.md](Phase-III/README.md)
**Live Demo**: [https://rainbow-froyo-cda32b.netlify.app](https://rainbow-froyo-cda32b.netlify.app)

**Key Features**:
- ✅ **AI Chat Assistant**: Natural language task management through conversational interface
- ✅ **MCP Tools Integration**: Model Context Protocol tools for structured task operations
- ✅ **Real-time Streaming**: Token-by-token response streaming for better UX
- ✅ **Tool Call Transparency**: Users see exactly what actions the AI is performing
- ✅ **Conversation Persistence**: Chat history stored and retrieved across sessions
- ✅ **Multi-Provider Support**: Groq (primary) and OpenAI (fallback) for reliability

**Technology Stack**:
- **AI Integration**: OpenAI Agents SDK, Groq API, OpenAI API (fallback)
- **LLM Models**: Groq (openai/gpt-oss-20b), OpenAI (gpt-4o-mini)
- **MCP Tools**: 5 custom tools (add, list, update, complete, delete tasks)
- **Frontend**: Next.js 15.5.12, Custom chat widget with glassmorphism UI

**AI Capabilities**:
- Natural language task creation: "Add a task to buy groceries"
- Task completion: "Mark the medicine task as complete"
- Task deletion: "Delete the task named bro"
- Task listing: "Show me all my pending tasks"
- Task updates: "Update the grocery task description to include milk and eggs"

**Architecture Highlights**:
- Agent Factory for AI agent creation and configuration
- Runner Factory for OpenAI client management with retry logic
- MCP Adapter for tool integration with OpenAI function calling
- Agent Orchestration for workflow coordination
- History Manager for conversation truncation

---

### Phase IV: Containerized & Kubernetes-Deployed
**Status**: ✅ Complete
**Branch**: `001-todo`
**Documentation**: [Phase-IV/README.md](Phase-IV/README.md)

**Key Features**:
- ✅ **Docker Containerization**: Multi-stage Dockerfiles for optimized production images
- ✅ **Kubernetes Deployment**: Helm charts for declarative infrastructure
- ✅ **Service Discovery**: Internal DNS-based communication between services
- ✅ **Local Kubernetes**: Minikube deployment for local development and testing
- ✅ **Port Forwarding**: Secure access to services via kubectl port-forward
- ✅ **Production-Ready Images**: Optimized Docker images with security best practices
- ✅ **Helm Charts**: Reusable deployment templates with values configuration

**Technology Stack**:
- **Containerization**: Docker multi-stage builds
- **Orchestration**: Kubernetes (Minikube for local)
- **Package Manager**: Helm 3.x
- **Container Runtime**: Docker
- **Service Discovery**: Kubernetes DNS
- **Networking**: ClusterIP (backend), NodePort (frontend)

**Docker Images**:
- **Backend**: 442MB (Python 3.13-slim, multi-stage build)
- **Frontend**: 409MB (Node 20-alpine, multi-stage build)

**Architecture Highlights**:
- Multi-stage Docker builds for optimized image sizes
- Non-root container users for security
- Health checks (liveness and readiness probes)
- Resource limits (CPU and memory)
- Helm charts for declarative infrastructure
- Service discovery with internal cluster DNS

---

## 🏗️ Current Architecture (Phase IV)

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

### Technology Stack (Complete)

**Backend**:
- **Framework**: FastAPI (Python 3.13+)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel with Alembic migrations
- **AI Integration**: OpenAI Agents SDK
- **LLM Providers**: Groq (primary), OpenAI (fallback)
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

**AI & MCP**:
- **Agent Factory**: AI agent creation and configuration
- **Runner Factory**: OpenAI client management with retry logic
- **MCP Adapter**: Tool integration with OpenAI function calling
- **MCP Tools**: 5 custom tools (add, list, update, complete, delete)
- **History Manager**: Conversation truncation and management

---

## ✨ Complete Feature Set

### Authentication & Security
- ✅ User registration and login
- ✅ JWT token-based authentication (30-minute expiration)
- ✅ Bcrypt password hashing
- ✅ 6-layer token validation
- ✅ User-scoped data isolation
- ✅ Account status management
- ✅ Password change invalidation

### Task Management
- ✅ Create tasks (via UI or AI chat)
- ✅ List tasks (all, pending, completed)
- ✅ Update task details
- ✅ Mark tasks as complete/incomplete
- ✅ Delete tasks
- ✅ User-specific task isolation

### AI Conversational Interface
- ✅ Natural language task management
- ✅ Real-time streaming responses
- ✅ Tool call transparency
- ✅ Conversation history persistence
- ✅ Multi-provider LLM support (Groq + OpenAI)
- ✅ Automatic fallback on rate limits
- ✅ Context-aware responses

### MCP Tools (5 Tools)
- ✅ `add_task`: Create new tasks
- ✅ `list_tasks`: List user's tasks
- ✅ `update_task`: Update existing tasks
- ✅ `complete_task`: Toggle task completion
- ✅ `delete_task`: Delete tasks

### Infrastructure & Deployment
- ✅ Docker containerization
- ✅ Kubernetes deployment (Minikube)
- ✅ Helm charts for declarative infrastructure
- ✅ Service discovery with Kubernetes DNS
- ✅ Health checks (liveness and readiness probes)
- ✅ Resource limits and requests
- ✅ Non-root container users
- ✅ Multi-stage Docker builds

---

## 🚀 Quick Start (Phase IV - Kubernetes)

### Prerequisites

- **Docker**: 20.x+ (for building images)
- **Kubernetes**: Minikube 1.30+ (for local deployment)
- **Helm**: 3.x+ (for deploying charts)
- **kubectl**: 1.28+ (for cluster management)
- **Node.js**: 18.x+ (for local frontend development)
- **Python**: 3.13+ (for local backend development)
- **UV**: Latest (Python package manager)

### Step 1: Start Minikube

```bash
minikube start
```

### Step 2: Build Docker Images

```bash
# Build backend image
cd Phase-IV/backend
docker build -f Dockerfile.production -t phase-iv-backend:latest .

# Build frontend image
cd ../frontend
docker build -t phase-iv-frontend:latest .
```

### Step 3: Load Images into Minikube

```bash
minikube image load phase-iv-backend:latest
minikube image load phase-iv-frontend:latest
```

### Step 4: Configure Secrets

Create `Phase-IV/todo-chatbot/values-local.yaml`:

```yaml
backend:
  env:
    - name: DATABASE_URL
      value: "postgresql+asyncpg://user:password@host/database"
    - name: BETTER_AUTH_SECRET
      value: "your-32-character-secret-here"
    - name: GROQ_API_KEY
      value: "your-groq-api-key"

frontend:
  env:
    - name: BETTER_AUTH_SECRET
      value: "your-32-character-secret-here"
    - name: DATABASE_URL
      value: "postgresql://user:password@host/database?sslmode=require"
```

### Step 5: Deploy with Helm

```bash
cd Phase-IV/todo-chatbot
helm install phase-iv-app . -f values.yaml -f values-local.yaml
```

### Step 6: Wait for Pods to be Ready

```bash
kubectl get pods -w
```

### Step 7: Set Up Port Forwarding

```bash
# Backend (in one terminal)
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 > /tmp/backend-pf.log 2>&1 &

# Frontend (in another terminal)
nohup kubectl port-forward svc/phase-iv-app-todo-chatbot-frontend 3000:3000 > /tmp/frontend-pf.log 2>&1 &
```

### Step 8: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📚 API Endpoints

### Authentication Endpoints (Public)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/auth/register` | Register new user | `{ email, password }` | `{ token, user }` |
| POST | `/api/auth/login` | Login existing user | `{ email, password }` | `{ token, user }` |

### Task Endpoints (Protected)

All task endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/api/{user_id}/tasks` | List user's tasks | `[{ id, title, ... }]` |
| POST | `/api/{user_id}/tasks` | Create new task | `{ id, title, ... }` |
| GET | `/api/{user_id}/tasks/{id}` | Get task details | `{ id, title, ... }` |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | `{ id, title, ... }` |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | `{ message }` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | `{ id, completed }` |

### Chat Endpoints (Protected)

All chat endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | `/api/{user_id}/chat` | Send message to AI | `{ conversation_id, response, tool_calls }` |
| POST | `/api/{user_id}/chat/stream` | Stream AI response | Server-Sent Events |
| GET | `/api/{user_id}/conversations` | List conversations | `[{ id, created_at, ... }]` |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get conversation history | `[{ role, content, ... }]` |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation | `{ message }` |

### Health Check (Public)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/api/health` | Health check | `{ status, timestamp }` |

---

## 🧪 Testing

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

```bash
# Test backend image
docker run --rm phase-iv-backend:latest python -c "import src.main; print('Backend OK')"

# Test frontend image
docker run --rm phase-iv-frontend:latest node --version
```

### Kubernetes Deployment Testing

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=phase-iv-app

# Check service endpoints
kubectl get endpoints

# Test backend health
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 &
curl http://localhost:8000/health

# View logs
kubectl logs -l app.kubernetes.io/component=backend -f
kubectl logs -l app.kubernetes.io/component=frontend -f
```

---

## 🌐 Deployment Options

### Local Development (Fastest)

```bash
# Backend
cd Phase-IV/backend
uv run uvicorn src.main:app --reload --port 8000

# Frontend
cd Phase-IV/frontend
npm run dev
```

### Docker Deployment

```bash
# Run backend container
docker run -d -p 8000:8000 --env-file .env phase-iv-backend:latest

# Run frontend container
docker run -d -p 3000:3000 --env-file .env.local phase-iv-frontend:latest
```

### Kubernetes Deployment (Current)

**Status**: ✅ Deployed to Minikube
**Access**: Via kubectl port-forward

See [Quick Start](#-quick-start-phase-iv---kubernetes) section above.

### Production Deployment (Cloud)

**Supported Platforms**:
- AWS EKS (Elastic Kubernetes Service)
- Google GKE (Google Kubernetes Engine)
- Azure AKS (Azure Kubernetes Service)
- DigitalOcean Kubernetes

**Steps**:
1. Push Docker images to container registry (ECR, GCR, ACR, Docker Hub)
2. Create Kubernetes secrets for sensitive data
3. Update Helm values for production configuration
4. Deploy with Helm to production cluster
5. Configure DNS and SSL certificates
6. Set up monitoring and logging

See [Phase-IV/README.md](Phase-IV/README.md) for detailed production deployment instructions.

---

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Port-forward connection refused
**Solution**: Verify service and pod are running, kill existing port-forward processes
```bash
kubectl get svc
kubectl get pods
pkill -f "port-forward"
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000 &
```

**Issue**: Frontend shows "not found" for API calls
**Solution**: Ensure backend is port-forwarded to correct port (8000)
```bash
kubectl port-forward svc/phase-iv-app-todo-chatbot-backend 8000:8000
```

**Issue**: AI responses are empty or incomplete
**Solution**: Check that `GROQ_API_KEY` is valid and has sufficient credits

**Issue**: Pods stuck in "Pending" state
**Solution**: Check pod events and node resources
```bash
kubectl describe pod <pod-name>
kubectl get nodes
kubectl top nodes
```

**Issue**: "ImagePullBackOff" error
**Solution**: Verify image exists in Minikube
```bash
minikube image ls | grep phase-iv
minikube image load phase-iv-backend:latest
```

For more troubleshooting tips, see:
- [Phase-II/README.md](Phase-II/README.md) - Authentication issues
- [Phase-III/README.md](Phase-III/README.md) - AI chat issues
- [Phase-IV/README.md](Phase-IV/README.md) - Docker/Kubernetes issues

---

## 📖 Documentation

### Phase-Specific Documentation
- **Phase II**: [Phase-II/README.md](Phase-II/README.md) - Authentication & Full-Stack Web App
- **Phase III**: [Phase-III/README.md](Phase-III/README.md) - AI-Powered Conversational Interface
- **Phase IV**: [Phase-IV/README.md](Phase-IV/README.md) - Docker & Kubernetes Deployment
- **Commands Reference**: [Phase-IV/COMMANDS.md](Phase-IV/COMMANDS.md) - All deployment commands

### External Resources
- **API Documentation**: http://localhost:8000/docs (when backend running)
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org/docs
- **Better Auth**: https://better-auth.com/docs
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-sdk
- **Groq**: https://console.groq.com/docs
- **Docker**: https://docs.docker.com
- **Kubernetes**: https://kubernetes.io/docs
- **Helm**: https://helm.sh/docs
- **Minikube**: https://minikube.sigs.k8s.io/docs

---

## 🎯 Project Highlights

### Technical Achievements
- ✅ **Full-Stack Development**: Complete frontend and backend implementation
- ✅ **Secure Authentication**: JWT-based auth with 6-layer validation
- ✅ **AI Integration**: Natural language task management with MCP tools
- ✅ **Containerization**: Production-optimized Docker images
- ✅ **Kubernetes Deployment**: Cloud-native deployment with Helm charts
- ✅ **Service Discovery**: Internal DNS-based pod communication
- ✅ **Multi-Provider LLM**: Groq primary with OpenAI fallback
- ✅ **Real-time Streaming**: Token-by-token AI response streaming
- ✅ **Comprehensive Testing**: 79+ tests across contract, unit, and integration
- ✅ **Production-Ready**: Security hardening, health checks, resource limits

### Best Practices Demonstrated
- Multi-stage Docker builds for optimized images
- Non-root container users for security
- Declarative infrastructure with Helm charts
- Structured logging for observability
- Health checks (liveness and readiness probes)
- Resource limits and requests
- User-scoped data isolation
- Token expiration and validation
- Error handling and fallback mechanisms
- Conversation history management

---

## 🤝 Contributing

When adding new features:

1. **Follow existing code patterns and architecture**
2. **Add tests for new functionality**
3. **Update Docker images when dependencies change**
4. **Update Helm charts for infrastructure changes**
5. **Update documentation**
6. **Test locally before deploying**

---

## 📝 License

[Your License Here]

---

## 🙏 Acknowledgments

Built with:
- FastAPI for high-performance backend
- Next.js for modern frontend
- Better Auth for authentication
- OpenAI Agents SDK for AI integration
- Groq for fast LLM inference
- Neon for serverless PostgreSQL
- Docker for containerization
- Kubernetes for orchestration
- Helm for deployment management

---

**Questions or Issues?**
- Check phase-specific README files for detailed documentation
- Review troubleshooting sections for common issues
- Consult external documentation for framework-specific questions

**Current Status**: ✅ Phase IV Complete - Fully functional in local Kubernetes
**Next Steps**: Deploy to cloud Kubernetes for production use
