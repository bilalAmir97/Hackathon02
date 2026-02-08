# Authentication & Security Integration Quickstart

## Overview
This guide provides step-by-step instructions to set up the authentication and security integration between Next.js frontend using Better Auth and FastAPI backend with JWT verification.

## Prerequisites
- Node.js 18+ with npm
- Python 3.9+
- Poetry (for Python dependency management)
- Neon PostgreSQL account
- Git

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy environment files
cp Phase-II/backend/.env.example Phase-II/backend/.env
cp Phase-II/frontend/.env.example Phase-II/frontend/.env.local
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd Phase-II/backend

# Install Python dependencies
poetry install

# Activate virtual environment
poetry shell

# Set up BETTER_AUTH_SECRET in .env
export BETTER_AUTH_SECRET="your-secret-key-here"
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd Phase-II/frontend

# Install Node.js dependencies
npm install

# Set up BETTER_AUTH_SECRET in .env.local
echo "NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key-here" >> .env.local
```

### 4. Database Setup
```bash
# In backend directory
cd Phase-II/backend

# Run database migrations
alembic upgrade head
```

### 5. Better Auth Configuration
1. Configure Better Auth in `Phase-II/frontend/src/lib/auth.ts`
2. Set JWT token lifetime to 30 minutes
3. Configure httpOnly cookies for secure token storage

### 6. FastAPI JWT Middleware
1. Set up JWT verification middleware in `Phase-II/backend/src/middleware/jwt_auth.py`
2. Configure token validation with shared secret
3. Implement user_id extraction and validation

## Running the Applications

### Start Backend Server
```bash
cd Phase-II/backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Server
```bash
cd Phase-II/frontend
npm run dev
```

## Testing Authentication Flow

1. Visit the registration page: http://localhost:3000/register
2. Register a new account with valid credentials
3. Log in with the registered credentials
4. Verify JWT token is received and stored securely
5. Access protected endpoints to verify user isolation

## Common Issues and Solutions

### Issue: Invalid Token Error
**Solution**: Ensure BETTER_AUTH_SECRET is identical in both frontend and backend environments

### Issue: User Isolation Not Working
**Solution**: Verify that JWT user_id claim matches the path user_id in API requests

### Issue: Token Expiration Problems
**Solution**: Check system clocks are synchronized and token lifetime is correctly configured

### Issue: Cookie Storage Problems
**Solution**: Ensure httpOnly and secure flags are properly set based on your deployment environment