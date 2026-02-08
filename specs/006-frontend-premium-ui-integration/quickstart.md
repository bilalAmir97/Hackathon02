# Quickstart Guide: Frontend Premium UI & Full-Stack Integration

## Overview

This guide provides step-by-step instructions to set up, develop, and run the premium Next.js frontend application with authentication and task management features.

## Prerequisites

- Node.js 18+ (recommended: latest LTS)
- npm or yarn package manager
- Access to backend API (FastAPI server with Better Auth)
- Environment variables configured (see `.env.local` below)

## Setup Instructions

### 1. Clone and Navigate to Frontend Directory

```bash
# Navigate to the frontend directory
cd Phase-II/frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Environment Configuration

Create `.env.local` file in the `Phase-II/frontend` directory:

```env
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # Adjust to your backend URL
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000  # Adjust to your auth URL

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key-here

# Optional: Additional configuration
NEXT_PUBLIC_APP_NAME="Premium Todo App"
NEXT_PUBLIC_DEFAULT_THEME="dark"  # or "light"
```

### 4. Run Development Server

```bash
npm run dev
# or
yarn dev
```

The application will start on `http://localhost:3000`

## Project Structure

```
Phase-II/frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout with global providers
│   │   ├── page.tsx         # Landing page
│   │   ├── login/page.tsx   # Login page
│   │   ├── register/page.tsx # Registration page
│   │   └── dashboard/page.tsx # Protected dashboard
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components
│   │   ├── auth/           # Authentication components
│   │   ├── dashboard/      # Dashboard-specific components
│   │   └── animations/     # GSAP animation components
│   ├── lib/                # Utility functions
│   │   ├── auth.ts         # Better Auth integration
│   │   ├── api-client.ts   # API client with JWT handling
│   │   ├── gsap-utils.ts   # GSAP utility functions
│   │   └── scan-line.ts    # Ambient scan-line animation
│   ├── hooks/              # Custom React hooks
│   ├── styles/             # Global styles and Tailwind config
│   └── types/              # TypeScript type definitions
├── public/                 # Static assets
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

## Key Features Setup

### 1. Authentication Flow

The application uses Better Auth for authentication:

```typescript
// Example usage in components
import { useAuth } from '@/lib/auth';

const { user, signIn, signOut, isLoading } = useAuth();

// Protected routes automatically redirect unauthenticated users
```

### 2. API Client with JWT

All API calls automatically include the JWT token:

```typescript
// Example API call
import { apiClient } from '@/lib/api-client';

const tasks = await apiClient.get(`/api/${userId}/tasks`);
const newTask = await apiClient.post(`/api/${userId}/tasks`, { title: 'New task' });
```

### 3. GSAP Animations

Animations are implemented using GSAP:

```typescript
// Example animation in components
import { animatePageEnter, animateHeroText } from '@/lib/gsap-utils';

// Use in useEffect
useEffect(() => {
  animatePageEnter();
  animateHeroText();
}, []);
```

### 4. Ambient Scan-Line Effect

The scan-line animation is applied globally:

```typescript
// Automatically applied in root layout
// Respects user's reduced motion preferences
```

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

## Development Workflow

### 1. Adding New Pages

Create new pages in the `src/app/` directory following Next.js App Router conventions:

```typescript
// src/app/new-feature/page.tsx
'use client';

export default function NewFeaturePage() {
  return (
    <div className="container mx-auto">
      <h1>New Feature</h1>
    </div>
  );
}
```

### 2. Creating Components

Add reusable components to the appropriate directory:

```typescript
// src/components/ui/button.tsx
import { cn } from '@/lib/utils';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
}

export function Button({ children, variant = 'primary', ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded-md font-medium',
        variant === 'primary' && 'bg-blue-600 text-white',
        variant === 'secondary' && 'bg-gray-200 text-gray-800'
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

### 3. Adding API Endpoints

The frontend consumes existing backend API endpoints:

```typescript
// GET /api/{user_id}/tasks - List all tasks
// POST /api/{user_id}/tasks - Create a new task
// GET /api/{user_id}/tasks/{id} - Get task details
// PUT /api/{user_id}/tasks/{id} - Update a task
// DELETE /api/{user_id}/tasks/{id} - Delete a task
// PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion
```

## Testing

### Unit Tests
```bash
npm run test
# or
npm run test:unit
```

### E2E Tests
```bash
npm run test:e2e
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_BASE_URL | Backend API URL | http://localhost:8000 |
| NEXT_PUBLIC_BETTER_AUTH_URL | Auth server URL | http://localhost:8000 |
| NEXT_PUBLIC_BETTER_AUTH_SECRET | Auth secret key | required |

## Common Issues and Solutions

### 1. Authentication Issues
- Ensure `BETTER_AUTH_SECRET` matches between frontend and backend
- Check that auth endpoints are accessible
- Verify JWT token is properly stored in httpOnly cookie

### 2. API Connection Issues
- Verify backend server is running
- Check API URL configuration
- Ensure CORS is properly configured

### 3. Animation Performance
- Disable animations in browser dev tools if experiencing performance issues
- Check that GSAP is properly imported and configured
- Verify scan-line respects reduced motion preferences

## Deployment

### Build for Production
```bash
npm run build
npm start
```

### Vercel Deployment
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

## Next Steps

1. Implement all Basic Level features (Add, Delete, Update, View, Complete tasks)
2. Add responsive design for all screen sizes
3. Implement GSAP animations for all user interactions
4. Add ambient scan-line effect to all pages
5. Complete authentication flow integration
6. Test user isolation functionality