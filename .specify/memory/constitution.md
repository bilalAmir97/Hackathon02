<!--
Sync Impact Report:
Version change: 1.0.0 → 2.0.0
Modified principles:
  - III. Phase Governance (MAJOR: Complete redefinition of phase boundaries and features)
  - Technology Constraints (MAJOR: Added UV, Better Auth, ChatKit, AIOps tools)
Added sections:
  - X. Feature Progression Governance
  - XI. AGENTS.md Integration (Reusable Intelligence)
  - XII. Deployment & Submission Standards
  - Agentic Dev Stack Workflow
Removed sections: None
Templates requiring updates:
  ✅ spec-template.md - reviewed, aligns with principles
  ✅ plan-template.md - reviewed, aligns with principles
  ✅ tasks-template.md - reviewed, aligns with principles
Follow-up TODOs:
  - Create AGENTS.md template in .specify/templates/
  - Document MCP server setup process
  - Add cloud deployment blueprints
-->

# Evolution of Todo - Project Constitution

## Core Principles

### I. Spec-Driven Development Mandate (NON-NEGOTIABLE)

**No agent may write code without approved specs and tasks.**

All work MUST follow this workflow:
1. Constitution → Specs (via `/sp.specify`)
2. Specs → Plan (via `/sp.plan`)
3. Plan → Tasks (via `/sp.tasks`)
4. Tasks → Implementation (via `/sp.implement`)

**Rationale**: Spec-Driven Development prevents scope creep, ensures alignment between
all stakeholders (human and AI), and creates an auditable trail of decisions. Code
written without approved specifications leads to wasted effort, misaligned features,
and technical debt that compounds across phases.

**Enforcement**:
- All PRs must reference an approved spec file path
- Code review must verify spec compliance
- Any deviation from spec requires spec amendment first
- Specs must be version-controlled and tracked
- No manual coding allowed - refinement occurs at spec level only

### II. Agent Behavior Rules (NON-NEGOTIABLE)

**Agents operate under strict behavioral constraints to maintain project integrity.**

Agents MUST:
- Follow only approved specifications and tasks
- Request spec amendments for any proposed changes
- Refuse requests to manually write code outside the workflow
- Document all decisions in appropriate artifacts (PHR, ADR)
- Use MCP tools and CLI commands as authoritative sources
- Validate against constitution before proceeding with any phase
- Reference Task IDs in all code implementations
- Stop and request clarification if requirements are underspecified

Agents MUST NOT:
- Invent features not specified
- Deviate from approved specifications
- Make architectural decisions without documenting in ADR
- Implement refinements without updating specs first
- Skip or bypass workflow steps
- Assume solutions from internal knowledge without external verification
- Generate code without a referenced Task ID
- Modify architecture without updating plan
- Propose features without updating specification
- Create tasks on their own without spec/plan approval

**Rationale**: AI agents are powerful but require guardrails. Without behavioral
constraints, agents may introduce scope creep, make undocumented decisions, or
implement features that conflict with project goals. These rules ensure agents
remain aligned with project objectives across all five phases.

**Enforcement**:
- Constitution check runs before every phase execution
- PHR created for every user interaction to maintain audit trail
- ADR required for all architecturally significant decisions
- Code reviews verify agent compliance with this section
- Every code file must contain a comment linking it to Task and Spec sections

### III. Phase Governance (NON-NEGOTIABLE)

**Each phase is strictly scoped by its specification. Future-phase features must never
leak into earlier phases.**

#### Phase Boundaries & Feature Requirements

**Phase I: In-Memory Python Console App** (Due: Dec 7, 2025)
- **Objective**: Command-line todo app with in-memory storage
- **Feature Level**: Basic Level ONLY
  - Add Task (create new todo items)
  - Delete Task (remove tasks from list)
  - Update Task (modify existing task details)
  - View Task List (display all tasks)
  - Mark as Complete (toggle task completion status)
- **Technology**: Python 3.13+, UV package manager
- **Storage**: In-memory only (no persistence)
- **Points**: 100

**Phase II: Full-Stack Web Application** (Due: Dec 14, 2025)
- **Objective**: Multi-user web app with persistent storage
- **Feature Level**: Basic Level ONLY (same 5 features as Phase I, now web-based)
- **Technology**: Next.js 16+ (App Router), FastAPI, SQLModel, Neon PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **API**: RESTful endpoints for all CRUD operations
- **Deployment**: Vercel (frontend) + Backend API (publicly accessible)
- **Security**: JWT-based authentication, user isolation
- **Points**: 150

**Phase III: AI-Powered Todo Chatbot** (Due: Dec 21, 2025)
- **Objective**: Conversational interface using OpenAI Agents SDK and MCP
- **Feature Level**: Basic Level via natural language
- **Technology**: OpenAI ChatKit (frontend), OpenAI Agents SDK, Official MCP SDK
- **Architecture**: Stateless chat endpoint, MCP server with tools
- **MCP Tools Required**:
  - add_task (with user_id)
  - list_tasks (with user_id and status filter)
  - complete_task (with user_id)
  - delete_task (with user_id)
  - update_task (with user_id)
- **State Management**: Database-persisted conversation history
- **Deployment**: ChatKit UI + Backend API with MCP
- **Points**: 200

**Phase IV: Local Kubernetes Deployment** (Due: Jan 4, 2026)
- **Objective**: Deploy Phase III chatbot on local Kubernetes (Minikube)
- **Feature Level**: Basic Level (same as Phase III)
- **Technology**: Docker, Minikube, Helm Charts, kubectl-ai, kagent, Gordon (Docker AI)
- **Containerization**: Frontend and backend Docker images
- **AIOps**: Use kubectl-ai and kagent for K8s operations
- **Docker AI**: Use Gordon for intelligent Docker operations (if available)
- **Deployment**: Local Minikube cluster with Helm charts
- **Points**: 250

**Phase V: Advanced Cloud Deployment** (Due: Jan 18, 2026)
- **Objective**: Implement advanced features + production cloud deployment
- **Feature Levels**:
  - **Advanced**: Recurring Tasks, Due Dates & Reminders (REQUIRED)
  - **Intermediate**: Priorities, Tags, Search, Filter, Sort (REQUIRED)
  - **Basic**: All existing features (carried forward)
- **Technology**: Kafka, Dapr, Kubernetes (Azure AKS/Google GKE/Oracle OKE/DigitalOcean DOKS)
- **Architecture**: Event-driven microservices with Dapr
- **Kafka Use Cases**:
  - Reminder/Notification System (via Kafka topic: "reminders")
  - Recurring Task Engine (via Kafka topic: "task-events")
  - Activity/Audit Log (via Kafka topic: "task-events")
  - Real-time Sync Across Clients (via Kafka topic: "task-updates")
- **Dapr Components**:
  - Pub/Sub (Kafka integration)
  - State Management (conversation state)
  - Service Invocation (frontend ↔ backend)
  - Jobs API (scheduled reminders - NOT cron bindings)
  - Secrets Management (API keys, credentials)
- **Deployment Sequence**:
  1. Deploy to Minikube with Dapr (local testing)
  2. Deploy to cloud K8s (Azure AKS/Google GKE/Oracle OKE/DigitalOcean DOKS)
  3. Integrate managed Kafka (Redpanda Cloud or self-hosted Strimzi)
  4. Set up CI/CD pipeline (GitHub Actions)
  5. Configure monitoring and logging
- **Points**: 300

#### Phase Rules

1. Each phase has its own complete specification
2. Implementation must deliver ONLY features specified for that phase
3. Architecture may evolve between phases through updated specs and plans
4. Code from Phase N cannot include features designated for Phase N+1
5. Phase transitions require full spec/plan/task cycle for new features
6. Feature levels must be respected:
   - Phase I-IV: Basic Level ONLY
   - Phase V: Basic + Intermediate + Advanced Levels
7. No manual coding allowed - all refinements must update specs first

**Rationale**: Phased development prevents over-engineering and ensures each phase
delivers working, valuable software. Allowing future-phase features to leak into
earlier phases creates unnecessary complexity, delays delivery, and makes it harder
to test and validate each phase independently. The hackathon structure rewards
incremental progress with points at each milestone.

**Enforcement**:
- Specs explicitly mark which phase each feature belongs to
- Specs explicitly mark feature level (Basic/Intermediate/Advanced)
- Code reviews check for future-phase feature leakage
- Architecture reviews validate phase boundaries
- ADRs document phase-specific architectural decisions
- Phase completion requires demo video (max 90 seconds)
- Each phase submission includes GitHub repo, deployed app, and demo video

### IV. Test-Driven Development (NON-NEGOTIABLE)

**Tests written → User approved → Tests fail → Then implement.**

TDD workflow:
1. Write tests that describe expected behavior
2. Get user approval on test scenarios
3. Verify tests fail (red phase)
4. Implement feature to make tests pass (green phase)
5. Refactor if needed while keeping tests passing

Test requirements:
- **Unit tests**: All business logic, models, and services
- **Integration tests**: API endpoints, database operations, external services
- **Contract tests**: All API contracts defined in `contracts/` directory
- **End-to-end tests**: Critical user journeys for each phase

**Rationale**: TDD ensures code meets requirements, provides regression protection,
documents expected behavior, and prevents over-engineering. Tests written after
implementation often miss edge cases and don't drive design.

**Enforcement**:
- All tasks.md files include test tasks before implementation tasks
- Tests must fail before implementation begins
- Code coverage targets: 80% minimum for business logic
- CI pipeline blocks merges if tests fail

### V. Clean Architecture (NON-NEGOTIABLE)

**Separation of concerns, dependency inversion, and testability.**

Architecture layers (from inner to outer):
1. **Domain/Entities**: Business logic, models (no framework dependencies)
2. **Use Cases/Services**: Application logic, orchestration
3. **Interface Adapters**: Controllers, presenters, gateways
4. **Infrastructure**: Frameworks, databases, external services

Dependency rules:
- Inner layers never depend on outer layers
- Dependencies point inward (Dependency Inversion Principle)
- Use interfaces/protocols to define contracts between layers
- Framework-agnostic core business logic

**Rationale**: Clean architecture ensures testability, maintainability, and
flexibility. It allows the core business logic to remain stable while
infrastructure and frameworks can evolve across phases.

**Enforcement**:
- All plans must diagram layer dependencies
- Code reviews verify dependency direction
- Architecture reviews validate separation of concerns
- Automated linting rules enforce import restrictions

### VI. Stateless Services (Required for Phase III, IV, and V)

**Services must be stateless to enable horizontal scaling and fault tolerance.**

Stateless design requirements:
- No in-memory session storage (use distributed cache or database)
- All state persisted to external stores (database, Redis, etc.)
- Services can be killed and restarted without data loss
- Request context passed explicitly, not stored in service instance

State management:
- User sessions: External session store (Redis, database)
- Application state: Database or distributed cache
- Conversation history: Database-persisted (Phase III+)
- Temporary data: Message queues or distributed cache with TTL
- File uploads: Object storage (S3, GCS, etc.) if needed

**Phase III Stateless Architecture**:
- Chat endpoint receives user message
- Fetches conversation history from database
- Builds message array for agent (history + new message)
- Stores user message in database
- Runs agent with MCP tools
- Stores assistant response in database
- Returns response to client
- Server holds NO state (ready for next request)

**Rationale**: Stateless services are required for AI chatbot architecture
(Phase III) and microservices scalability (Phase IV-V). They enable horizontal
scaling, rolling deployments, and fault tolerance. Conversation history
persists in database, allowing server restarts without data loss.

**Enforcement**:
- Architecture reviews verify stateless design in Phase III+ specs
- Load testing validates service can handle instance restarts
- Code reviews check for in-memory state violations
- ADRs document state management decisions

### VII. Contract-First Design

**APIs and integrations defined before implementation.**

Contract requirements:
- All APIs documented in `specs/<feature>/contracts/` before implementation
- OpenAPI/Swagger specs for REST APIs
- AsyncAPI specs for event-driven communication (Phase V)
- JSON Schema for request/response payloads
- Error schemas with standardized error codes
- MCP tool specifications (Phase III+)

Contract workflow:
1. Define contracts during `/sp.plan` phase
2. Store contracts in `specs/<feature>/contracts/` directory
3. Generate contract tests from specifications
4. Implement services to satisfy contracts
5. Validate with contract testing

**Phase II REST API Contracts**:
```
GET    /api/{user_id}/tasks          - List all tasks
POST   /api/{user_id}/tasks          - Create a new task
GET    /api/{user_id}/tasks/{id}     - Get task details
PUT    /api/{user_id}/tasks/{id}     - Update a task
DELETE /api/{user_id}/tasks/{id}     - Delete a task
PATCH  /api/{user_id}/tasks/{id}/complete - Toggle completion
```

**Phase III MCP Tool Contracts**:
- add_task(user_id, title, description)
- list_tasks(user_id, status)
- complete_task(user_id, task_id)
- delete_task(user_id, task_id)
- update_task(user_id, task_id, title, description)

**Rationale**: Contract-first design ensures clear communication between services,
enables parallel development, and provides documentation that stays in sync with
implementation. Critical for multi-service architecture in Phase IV and V, and
for MCP tool integration in Phase III+.

**Enforcement**:
- Plans must include contract definitions before implementation
- Contract tests run in CI pipeline
- Code reviews verify implementation matches contracts
- Breaking changes require explicit versioning and migration plan

### VIII. Observability & Monitoring

**All services must emit logs, metrics, and traces.**

Observability requirements:
- **Structured logging**: JSON format with correlation IDs
- **Metrics**: RED method (Rate, Errors, Duration) for all endpoints
- **Distributed tracing**: OpenTelemetry for request tracing (Phase IV+)
- **Health checks**: `/health` and `/ready` endpoints for all services (Phase II+)

Logging standards:
- Log levels: DEBUG, INFO, WARN, ERROR, CRITICAL
- Include: timestamp, correlation_id, user_id (if applicable), service, action
- PII redaction in logs
- Log aggregation (ELK, Datadog, etc.) in Phase IV+

**Rationale**: Observability is essential for debugging production issues,
monitoring service health, and understanding system behavior. Must be built in
from the start, not added later.

**Enforcement**:
- All services must implement structured logging
- Health check endpoints required in Phase II+
- Metrics collection mandatory in Phase III+
- Distributed tracing required in Phase IV+
- Monitoring dashboards and alerts defined in plan.md

### IX. Security & Compliance

**Security must be designed in, not bolted on.**

Security requirements by phase:
- **Phase I**: Input validation, no hardcoded secrets
- **Phase II+**: JWT-based authentication (Better Auth)
- **Phase II+**: User isolation (filter all queries by user_id)
- **Phase III+**: MCP tools include user_id for access control
- **Phase V**: Role-based access control (RBAC) if implementing enterprise features

Authentication & Authorization:
- **Better Auth**: JavaScript/TypeScript auth library (Next.js frontend)
- **JWT Tokens**: Self-contained credentials with user information
- **Shared Secret**: BETTER_AUTH_SECRET used by both frontend and backend
- **Token Flow**:
  1. User logs in → Better Auth creates session + issues JWT
  2. Frontend API calls → Include JWT in `Authorization: Bearer <token>` header
  3. Backend receives request → Extracts token, verifies signature
  4. Backend identifies user → Decodes token to get user_id
  5. Backend filters data → Returns only that user's tasks

Data protection:
- OWASP Top 10 vulnerability prevention
- SQL injection prevention (parameterized queries, ORM)
- XSS prevention (output encoding, CSP headers)
- CSRF protection (tokens, SameSite cookies)
- Rate limiting to prevent abuse

**Rationale**: Security vulnerabilities compound over time and are expensive to fix
in later phases. Building security in from Phase II prevents technical debt and
ensures user data protection. JWT-based authentication enables stateless services
while maintaining security.

**Enforcement**:
- Security review required in all plan.md files
- Automated security scanning in CI pipeline
- No secrets in code or version control
- All API endpoints require valid JWT token (Phase II+)
- Each user only sees/modifies their own tasks
- ADRs for all security-related architectural decisions

### X. Feature Progression Governance (NON-NEGOTIABLE)

**Features are implemented in three levels. Each phase specifies which levels are allowed.**

#### Feature Levels

**Basic Level (Core Essentials)** - Required in ALL phases:
1. Add Task – Create new todo items
2. Delete Task – Remove tasks from the list
3. Update Task – Modify existing task details
4. View Task List – Display all tasks
5. Mark as Complete – Toggle task completion status

**Intermediate Level (Organization & Usability)** - Required ONLY in Phase V:
1. Priorities & Tags/Categories – Assign levels (high/medium/low) or labels (work/home)
2. Search & Filter – Search by keyword; filter by status, priority, or date
3. Sort Tasks – Reorder by due date, priority, or alphabetically

**Advanced Level (Intelligent Features)** - Required ONLY in Phase V:
1. Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
2. Due Dates & Time Reminders – Set deadlines with date/time pickers; browser notifications

#### Feature Progression Rules

1. **Phase I-IV**: ONLY Basic Level features allowed
2. **Phase V**: All three levels required (Basic + Intermediate + Advanced)
3. **No premature implementation**: Intermediate and Advanced features in Phase I-IV
   constitute phase boundary violations
4. **Event-driven architecture required for Advanced features**: Recurring tasks and
   reminders MUST use Kafka and Dapr (Phase V only)

#### Kafka Event-Driven Patterns (Phase V Only)

**Reminder/Notification System**:
- Producer: Chat API (when due date is set)
- Consumer: Notification Service
- Topic: "reminders"
- Purpose: Send reminders at scheduled times

**Recurring Task Engine**:
- Producer: Task Completed Event
- Consumer: Recurring Task Service
- Topic: "task-events"
- Purpose: Auto-create next occurrence when recurring task is completed

**Activity/Audit Log**:
- Producer: All Task Operations
- Consumer: Audit Service
- Topic: "task-events"
- Purpose: Maintain complete history of all task operations

**Real-time Sync Across Clients**:
- Producer: Task Changed (any client)
- Consumer: WebSocket Service
- Topic: "task-updates"
- Purpose: Broadcast changes to all connected clients in real-time

**Rationale**: Feature progression ensures each phase delivers a complete,
working product at the appropriate complexity level. Basic features form the
foundation and are carried through all phases. Advanced features require
sophisticated infrastructure (Kafka, Dapr) that only exists in Phase V.

**Enforcement**:
- Specs must explicitly mark feature level for each requirement
- Code reviews check for premature feature implementation
- Phase I-IV implementations must reject Intermediate/Advanced features
- Phase V must include all three feature levels
- Advanced features must use event-driven architecture (Kafka + Dapr)

### XI. AGENTS.md Integration (Reusable Intelligence)

**AGENTS.md is the primary instruction file for all AI agents. CLAUDE.md acts as a shim.**

#### AGENTS.md Structure

AGENTS.md must contain:
- **Purpose**: Explains Spec-Driven Development (SDD) workflow
- **Agent Rules**: Strict behavioral constraints
- **Spec-Kit Workflow**: Constitution → Specify → Plan → Tasks → Implement
- **Agent Behavior**: How to reference tasks, specs, plans
- **Failure Modes**: What agents must avoid
- **Developer-Agent Alignment**: Spec as single source of truth

#### CLAUDE.md Shim Pattern

Create `CLAUDE.md` in project root:
```markdown
@AGENTS.md
```

This forwarding ensures Claude Code loads comprehensive agent instructions
immediately upon startup.

#### MCP Server Integration

**Requirements**:
1. Install Spec-Kit Plus: `uv init specifyplus <project_name>`
2. Create Constitution (this file)
3. Add Anthropic's official MCP Builder Skill
4. Use SDD Loop to set up MCP server with prompts from `.claude/commands/**`
5. Register MCP server in Claude Code config (`.mcp.json`)

**MCP Server Configuration** (`.mcp.json`):
```json
{
  "mcpServers": {
    "spec-kit": {
      "command": "spec-kitplus-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

**Available MCP Prompts** (from `.claude/commands/`):
- `/sp.specify` - Create feature specification
- `/sp.plan` - Generate implementation plan
- `/sp.tasks` - Break plan into atomic tasks
- `/sp.implement` - Execute task implementation
- `/sp.adr` - Create Architecture Decision Record
- `/sp.phr` - Create Prompt History Record
- `/sp.constitution` - Update project constitution
- `/sp.clarify` - Ask clarification questions
- `/sp.analyze` - Cross-artifact consistency analysis
- `/sp.checklist` - Generate custom checklist
- `/sp.git.commit_pr` - Create commit and PR
- `/sp.reverse-engineer` - Reverse engineer codebase

#### Agentic Dev Stack Workflow

**Mental Model**:
- **AGENTS.md**: The Brain (cross-agent truth)
- **Spec-Kit Plus**: The Architect (manages spec artifacts)
- **Claude Code**: The Executor (agentic environment)

**Day-to-Day Workflow**:
1. Start Claude Code → Reads CLAUDE.md → AGENTS.md
2. User: "I need a project dashboard"
3. Claude: Calls `speckit_specify` and `speckit_plan` via MCP
4. Claude: Calls `speckit_tasks` to create checklist
5. User: "Execute the first two tasks"
6. Claude: Calls `speckit_implement`, writes code, checks against constitution

**Rationale**: AGENTS.md provides a single source of truth for all AI agents
(Claude, Copilot, Gemini, etc.). MCP server integration enables Claude Code to
execute Spec-Kit commands natively. This ensures consistent, spec-driven
development across all tools and phases.

**Enforcement**:
- AGENTS.md must exist in project root
- CLAUDE.md must reference AGENTS.md
- MCP server must be configured and running
- All agent interactions must follow SDD workflow
- Agents must reference Task IDs in all code
- Agents must stop and request clarification if specs are underspecified

### XII. Deployment & Submission Standards

**Each phase has specific deployment requirements and submission criteria.**

#### Phase-Specific Deployment Requirements

**Phase I Deployment**:
- GitHub repository with source code
- README.md with setup instructions
- CLAUDE.md with agent instructions
- Constitution file (this document)
- /specs folder with all specifications
- Working console application demo

**Phase II Deployment**:
- GitHub repository (full-stack monorepo)
- Vercel deployment (frontend)
- Publicly accessible backend API
- Neon Serverless PostgreSQL database
- Better Auth authentication
- /specs folder with updated specifications

**Phase III Deployment**:
- GitHub repository with chatbot integration
- OpenAI ChatKit frontend deployment
- Backend API with MCP server
- Neon database (conversation history + tasks)
- MCP tools specification in /specs folder
- Domain allowlist configured (OpenAI platform)

**Phase IV Deployment**:
- GitHub repository with Kubernetes manifests
- Docker images (frontend + backend)
- Helm charts for deployment
- Minikube local cluster setup instructions
- kubectl-ai and kagent usage documentation
- Gordon (Docker AI) usage if available

**Phase V Deployment**:
- GitHub repository with full microservices architecture
- Local Minikube deployment with Dapr
- Cloud deployment (Azure AKS/Google GKE/Oracle OKE/DigitalOcean DOKS)
- Kafka integration (Redpanda Cloud or Strimzi self-hosted)
- Dapr components configured (Pub/Sub, State, Jobs API, Secrets)
- CI/CD pipeline (GitHub Actions)
- Monitoring and logging configured

#### Submission Requirements (All Phases)

**Required Submissions**:
1. Public GitHub Repository containing:
   - All source code for completed phase
   - /specs folder with all specification files
   - AGENTS.md (primary agent instructions)
   - CLAUDE.md (shim to AGENTS.md)
   - Constitution file (this document)
   - README.md with comprehensive documentation
   - Clear folder structure for the phase

2. Deployed Application Links:
   - Phase I: GitHub repo only (console app)
   - Phase II: Vercel URL + Backend API URL
   - Phase III-V: Chatbot URL
   - Phase IV: Minikube setup instructions
   - Phase V: Cloud deployment URL

3. Demo Video (maximum 90 seconds):
   - Demonstrate all implemented features
   - Show spec-driven development workflow
   - Judges will only watch first 90 seconds
   - Can use NotebookLM or screen recording

4. WhatsApp Number:
   - For presentation invitation
   - Top submissions invited to present live on Zoom

#### Submission Deadlines

- **Phase I**: Sunday, Dec 7, 2025 (8:00 PM Zoom presentation)
- **Phase II**: Sunday, Dec 14, 2025 (8:00 PM Zoom presentation)
- **Phase III**: Sunday, Dec 21, 2025 (8:00 PM Zoom presentation)
- **Phase IV**: Sunday, Jan 4, 2026 (8:00 PM Zoom presentation)
- **Phase V**: Sunday, Jan 18, 2026 (Final presentation date TBD)

#### Points System

| Phase | Points | Bonus Opportunities |
|-------|--------|---------------------|
| Phase I | 100 | - |
| Phase II | 150 | - |
| Phase III | 200 | - |
| Phase IV | 250 | - |
| Phase V | 300 | - |
| **TOTAL** | **1,000** | **+600** |

**Bonus Points**:
- Reusable Intelligence (Subagents and Skills): +200
- Cloud-Native Blueprints (Agent Skills): +200
- Multi-language Support (Urdu in chatbot): +100
- Voice Commands (voice input for todos): +200

**Rationale**: Clear deployment and submission standards ensure consistency,
enable proper evaluation, and prepare participants for real-world software
delivery. Each phase builds on the previous, creating a complete portfolio
piece by Phase V.

**Enforcement**:
- Submission form required for each phase
- Demo video must be under 90 seconds
- GitHub repository must be public
- All deployment URLs must be publicly accessible
- Specs folder must contain complete specifications
- No phase can be submitted without previous phases complete

## Technology Constraints

**Technology stack is fixed to ensure consistency and prevent fragmentation.**

### Backend Stack
- **Language**: Python 3.13+
- **Package Manager**: UV (required)
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Testing**: pytest, pytest-asyncio

### Frontend Stack (Phase II+)
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **UI Library**: React Server Components
- **Styling**: Tailwind CSS
- **State Management**: React Context + Server Actions
- **Authentication**: Better Auth with JWT tokens
- **Deployment**: Vercel

### AI/Agent Stack (Phase III+)
- **Chatbot UI**: OpenAI ChatKit
- **AI Framework**: OpenAI Agents SDK
- **MCP Protocol**: Official MCP SDK (Model Context Protocol)
- **MCP Server**: Python-based with FastAPI integration
- **Embeddings**: OpenAI text-embedding-ada-002 (if needed)
- **Vector Store**: Pinecone or pgvector (if needed)

### Infrastructure Stack (Phase IV+)
- **Containerization**: Docker
- **Docker AI**: Gordon (Docker AI Agent) - if available
- **Orchestration**: Kubernetes
- **Local K8s**: Minikube
- **Package Manager**: Helm Charts
- **AIOps Tools**: kubectl-ai, kagent
- **Message Broker**: Apache Kafka (Redpanda Cloud or Strimzi)
- **Service Mesh**: Dapr (Distributed Application Runtime)
- **API Gateway**: Kong or Nginx (if needed)
- **Monitoring**: Prometheus + Grafana

### Development Tools
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Code Quality**: Ruff (Python), ESLint (TypeScript)
- **API Documentation**: FastAPI auto-generated OpenAPI docs
- **Environment**: Docker Compose for local development
- **Spec Management**: Spec-Kit Plus
- **Agent Instructions**: AGENTS.md (primary), CLAUDE.md (shim)
- **MCP Integration**: Claude Code with MCP server

### Cloud Platform Options (Phase V)

Choose ONE of the following:

**Option 1: Oracle Cloud (Recommended - Always Free)**
- Sign up: https://www.oracle.com/cloud/free/
- OKE cluster: 4 OCPUs, 24GB RAM (always free)
- No credit card charge after trial
- Best for learning without time pressure

**Option 2: Microsoft Azure (AKS)**
- Sign up: https://azure.microsoft.com/en-us/free/
- US$200 credits for 30 days
- Plus 12 months of selected free services

**Option 3: Google Cloud (GKE)**
- Sign up: https://cloud.google.com/free?hl=en
- US$300 credits, usable for 90 days

**Option 4: DigitalOcean (DOKS)**
- US$200 credit for 60 days (new accounts)

### Kafka Service Options (Phase V)

**For Cloud Deployment**:

**Option 1: Redpanda Cloud (Recommended)**
- Free Serverless tier
- Kafka-compatible, no Zookeeper
- Fast setup, easy to use
- Sign up: https://redpanda.com/cloud

**Option 2: Self-Hosted (Strimzi Operator)**
- Free (just compute cost)
- Production-grade K8s operator
- Full control, learning experience
- Install via kubectl

**For Local Development (Minikube)**:
- Redpanda Docker container (simplest)
- Bitnami Kafka Helm chart
- Strimzi Operator (production-grade)

**Rationale**: Technology constraints prevent decision paralysis, ensure team
expertise applies across all phases, and simplify hiring and onboarding.
These technologies support the project from Phase I through Phase V and align
with industry standards for cloud-native AI applications.

**Substitution Policy**:
- Technology changes require ADR and user approval
- Must demonstrate clear advantage over specified technology
- Migration plan required for existing code
- Must not violate other constitution principles
- Hackathon participants must use specified stack for evaluation

## Development Workflow

**Standardized workflow ensures consistency and quality across all phases.**

### Agentic Dev Stack Workflow

**Mental Model**:
- **AGENTS.md**: The Brain (cross-agent truth, how agents behave)
- **Spec-Kit Plus**: The Architect (manages spec artifacts)
- **Claude Code**: The Executor (agentic environment via MCP)

### Workflow Steps

1. **Constitution Review**:
   - Verify request aligns with constitution principles
   - Check phase boundaries are respected
   - Validate technology constraints
   - Ensure feature level is appropriate for current phase

2. **Specification (`/sp.specify`)**:
   - Write feature specification in `specs/<feature>/spec.md`
   - Define user stories with acceptance criteria
   - Specify functional and non-functional requirements
   - Mark feature level (Basic/Intermediate/Advanced)
   - Mark phase assignment (Phase I-V)
   - Get user approval before proceeding

3. **Planning (`/sp.plan`)**:
   - Research existing codebase and dependencies
   - Design architecture and data models
   - Define API contracts in `specs/<feature>/contracts/`
   - Define MCP tools if Phase III+ (with user_id parameters)
   - Produce `plan.md`, `research.md`, `data-model.md`, `quickstart.md`
   - Document significant decisions in ADRs
   - Get user approval before proceeding

4. **Task Decomposition (`/sp.tasks`)**:
   - Break plan into atomic, testable tasks
   - Organize tasks by user story for independent delivery
   - Mark parallelizable tasks with [P]
   - Mark user story ownership with [US1], [US2], etc.
   - Define test tasks before implementation tasks
   - Output to `specs/<feature>/tasks.md`

5. **Implementation (`/sp.implement`)**:
   - Execute tasks in dependency order
   - Follow TDD: write tests → verify failure → implement → verify pass
   - Reference Task IDs in all code comments
   - Create PHR (Prompt History Record) for every user interaction
   - Commit small, atomic changes
   - Run tests continuously
   - No manual coding - all refinements update specs

6. **Code Review & Quality Gates**:
   - Verify constitution compliance
   - Check spec alignment
   - Review test coverage
   - Run security scans
   - Validate documentation
   - Check for phase boundary violations
   - Verify feature level compliance

7. **Commit & PR (`/sp.git.commit_pr`)**:
   - Create descriptive commit messages
   - Reference spec and task IDs
   - Create pull request with summary
   - Link to relevant specs, ADRs, PHRs
   - Get approval before merge

### Quality Gates

Every PR must pass:
- ✅ Constitution compliance check
- ✅ All tests passing (unit, integration, contract)
- ✅ Code coverage ≥ 80% for business logic
- ✅ Security scan (no high/critical vulnerabilities)
- ✅ Linting and formatting checks
- ✅ Spec reference and alignment verification
- ✅ No future-phase feature leakage
- ✅ Feature level compliance (Basic/Intermediate/Advanced)

### Documentation Requirements

Every feature must include:
- **spec.md**: User-facing requirements and acceptance criteria
- **plan.md**: Architecture, design decisions, complexity justifications
- **tasks.md**: Atomic, testable implementation tasks
- **quickstart.md**: How to run and test the feature locally
- **contracts/**: API specifications (OpenAPI, AsyncAPI, JSON Schema, MCP tools)
- **PHRs**: Prompt History Records for all user interactions
- **ADRs**: Architecture Decision Records for significant decisions
- **AGENTS.md**: Primary agent instruction file (project root)
- **CLAUDE.md**: Shim file referencing AGENTS.md

### MCP Server Development Workflow

**One-Time Setup**:
1. `uv init specifyplus <project_name>`
2. Create Constitution (this file)
3. Add Anthropic's official MCP Builder Skill
4. Use SDD Loop to create MCP server from `.claude/commands/**`
5. Register in `.mcp.json`

**Day-to-Day Usage**:
1. Start Claude Code → Loads AGENTS.md via CLAUDE.md
2. User provides requirement
3. Claude executes `/sp.specify` via MCP
4. Claude executes `/sp.plan` via MCP
5. Claude executes `/sp.tasks` via MCP
6. Claude executes `/sp.implement` via MCP
7. Claude creates PHR automatically

## Governance

**The constitution is the highest authority. All other practices, patterns, and
preferences are subordinate.**

### Amendment Process

1. Propose amendment with rationale and impact analysis
2. Document in ADR with alternatives considered
3. Update constitution with version bump:
   - MAJOR: Backward-incompatible changes (principle removal/redefinition)
   - MINOR: New principles or material expansions
   - PATCH: Clarifications, wording, non-semantic fixes
4. Update all dependent templates and documentation
5. Get user approval before applying
6. Create migration plan for existing code if needed
7. Document in Sync Impact Report

### Compliance Reviews

- All PRs must verify constitution compliance
- Architecture reviews validate adherence to principles
- Phase-end reviews check feature level compliance
- Quarterly audits of specs, plans, and code against constitution
- Non-compliance must be justified and documented in ADR or fixed

### Complexity Justification

Any violation of constitution principles must include:
- Clear explanation of why simpler approach is insufficient
- Documentation in plan.md Complexity Tracking table
- Alternative approaches considered and rejected
- Approval from user before implementation
- Plan to remove complexity in future phase if possible

### Runtime Guidance

For agent-specific runtime guidance and execution details:
- See `AGENTS.md` for primary agent instructions (all agents)
- See `CLAUDE.md` for Claude Code shim (references AGENTS.md)
- See `.claude/commands/*.md` for command workflows
- Constitution principles override agent-specific guidance in case of conflict

### Hierarchy of Authority

In case of conflicts, the precedence order is:
1. **Constitution** (this document) - WHY and core principles
2. **Spec (speckit.specify)** - WHAT to build
3. **Plan (speckit.plan)** - HOW to build it
4. **Tasks (speckit.tasks)** - Breakdown of work
5. **AGENTS.md** - Agent behavior guidelines
6. **Implementation** - Actual code

**Version**: 2.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
