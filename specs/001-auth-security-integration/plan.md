# Authentication & Security Integration Plan

## Overview
Implement Better Auth on Next.js frontend and JWT verification in FastAPI backend so all API requests are authenticated and user-isolated.

## Project Structure
Work inside Phase-II/frontend/ (Next.js) and Phase-II/backend/ (FastAPI). Use exact Next.js installer: `npx create-next-app@16.0.10`.

## Deliverables
- Next.js app with Better Auth configured to issue JWTs
- Frontend API client that attaches `Authorization: Bearer <token>` to requests
- Env var `BETTER_AUTH_SECRET` added to frontend and backend env examples
- FastAPI JWT verification middleware that validates signature, expiry, and extracts `user_id` claim
- Enforcement that JWT `user_id` matches path `user_id` for all protected endpoints
- Tests verifying 401/403 behavior, token expiry, and cross-user access prevention
- README documenting architecture sketch, decisions, and testing plan

## Architecture Phases

### Phase 0: Research (research.md)
- Resolved 10 technical unknowns from Technical Context
- Decided on HMAC (HS256) JWT signing with shared secret (vs RSA)
- Selected httpOnly cookies for token storage (XSS protection)
- Designed FastAPI dependency pattern for JWT verification
- Defined User schema with password_changed_at and status fields
- Documented frontend API client wrapper pattern
- Established environment variable management strategy
- Defined comprehensive testing strategy (unit, integration, contract)
- Documented performance optimization approach (<50ms p95 latency)
- Outlined OWASP Top 10 security mitigation measures

### Phase 1: Design & Contracts
- Created data-model.md with User entity specification
  - Fields: id, email, password_hash, status, password_changed_at, created_at, updated_at
  - Validation rules for email, password, status transitions
  - State transition diagrams for account status and password changes
  - Database migration scripts and indexing strategy
- Generated API contracts:
  - jwt-claims.json: JSON Schema for JWT token claims (sub, user_id, email, iat, exp)
  - auth-api.yaml: OpenAPI spec for /api/auth/register and /api/auth/login
  - protected-api.yaml: OpenAPI spec for protected endpoints with authentication rules
- Created quickstart.md with step-by-step local development setup
  - Database setup (Neon PostgreSQL)
  - Backend setup (FastAPI with PyJWT)
  - Frontend setup (Next.js 16.0.10 with Better Auth)
  - Testing authentication flow
  - Troubleshooting common issues

## Key Architectural Decisions
1. HMAC (HS256) over RSA - simplicity, performance, sufficient security for Phase II
2. httpOnly cookies over localStorage - XSS protection, Better Auth default
3. Stateless JWT with database validation - verify account status and password changes on each request
4. 30-minute token lifetime - industry standard for access tokens without refresh
5. User isolation enforcement - JWT user_id must match path user_id on all protected endpoints

## Technology Stack
- Frontend: Next.js 16.0.10 with Better Auth
- Backend: FastAPI with PyJWT
- Database: Neon PostgreSQL
- Authentication: JWT tokens with HS256 signing
- Security: httpOnly cookies for token storage

## Implementation Steps
1. Set up Better Auth in Next.js frontend
2. Configure JWT token generation with shared secret
3. Implement frontend API client with Authorization header
4. Create FastAPI JWT verification middleware
5. Enforce user isolation on protected endpoints
6. Implement comprehensive testing strategy
7. Document architecture and setup process