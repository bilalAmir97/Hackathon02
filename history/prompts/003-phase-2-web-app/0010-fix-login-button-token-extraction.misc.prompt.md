---
id: "0010"
title: "Fix login button token extraction"
stage: "misc"
date: "2026-01-08"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "phase-2-web-app"
branch: "002-reorganize-phase-1"
user: "Human"
command: "debug: why login button not working, better auth setup check"
labels: ["auth", "better-auth", "bug-fix", "frontend"]
links:
  spec: "specs/003-phase-2-web-app/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "phase-2/frontend/src/components/auth/LoginButton.tsx"
  - "phase-2/frontend/src/lib/auth.ts"
  - "phase-2/frontend/src/lib/auth-server.ts"
tests:
  - "null"
---

## Prompt

we were on phase check it out why the frontend login button is not working and whether the better auth is successfully setup or not

## Response snapshot

**Diagnosis:**
The login button was failing because Better Auth v1 returns the JWT token in the response header `set-auth-token`, NOT in `result.data.session.token` as the code expected.

**Root Cause:**
- `LoginButton.tsx` line 32 tried to access `result.data.session.token` which doesn't exist in Better Auth v1 API
- Better Auth v1 requires using the `onSuccess` callback to extract the token from response headers

**Fix Applied:**
Updated `LoginButton.tsx` to:
1. Pass `onSuccess` callback to `signIn.email()` that extracts token from `ctx.response.headers.get("set-auth-token")`
2. Keep fallback for older API patterns

**Better Auth Setup Verification:**
- ✅ Dependencies installed (better-auth@^1.0.0)
- ✅ Server config (`auth-server.ts`) configured with database pool and email/password enabled
- ✅ API route handler (`[...all]/route.ts`) properly exports GET/POST
- ✅ Client config (`auth.ts`) creates auth client with baseURL
- ✅ JWT middleware on backend properly configured
- ⚠️ Port mismatch: frontend expects API at port 8001, backend runs on 8000
- ⚠️ Better Auth URL mismatch: backend config points to localhost:3000, frontend runs on 3001

## Outcome

- ✅ Impact: Fixed login button token extraction to work with Better Auth v1 API
- 🧪 Tests: null
- 📁 Files: Modified LoginButton.tsx to use onSuccess callback for token extraction
- 🔁 Next prompts: Test the login flow after fixing token extraction; address port/URL mismatches between frontend and backend
- 🧠 Reflection: Better Auth v1 changed token delivery mechanism - must extract from response headers, not data object

## Evaluation notes (flywheel)

- Failure modes observed: Login button clicked, API called, but token never extracted because property path was incorrect
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Test the fixed login flow and verify token is properly stored in localStorage
