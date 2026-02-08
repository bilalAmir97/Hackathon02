# Quickstart Guide: Frontend Application & Full-Stack Integration

## Prerequisites

- Node.js 18+ installed
- Yarn or npm package manager
- Access to the Phase II backend API
- BETTER_AUTH_SECRET environment variable

## Project Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd Phase-II/frontend
   ```

2. **Install dependencies**:
   ```bash
   yarn install
   # or
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp .env.local.example .env.local
   ```

   Update the following variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
   BETTER_AUTH_SECRET=your-secret-key-here
   ```

## Development Server

1. **Start the development server**:
   ```bash
   yarn dev
   # or
   npm run dev
   ```

2. **Open your browser** to `http://localhost:3000`

## Available Scripts

- `yarn dev` - Start development server with hot reload
- `yarn build` - Build for production
- `yarn start` - Start production server
- `yarn lint` - Run linter
- `yarn test` - Run unit tests
- `yarn test:e2e` - Run end-to-end tests

## Key Directories

- `src/app/` - Next.js App Router pages and layouts
- `src/components/` - Reusable UI components
- `src/lib/` - Utility functions and API clients
- `src/hooks/` - Custom React hooks
- `public/` - Static assets

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL` - Backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_URL` - Auth service URL
- `BETTER_AUTH_SECRET` - Secret for JWT signing (backend)
- `NEXT_PUBLIC_APP_NAME` - Application name for UI

## API Integration

The frontend uses a centralized API client that:
- Automatically attaches JWT tokens to requests
- Handles authentication errors
- Provides loading and error states
- Implements retry logic for failed requests

## Authentication Flow

1. User visits `/login` or `/register`
2. Credentials sent to backend via Better Auth
3. JWT token received and stored in browser
4. Token attached to all subsequent API requests
5. Protected routes check for valid authentication

## Running Tests

- **Unit tests**: `yarn test:unit`
- **Component tests**: `yarn test:components`
- **E2E tests**: `yarn test:e2e`

## Deployment

1. Build the application: `yarn build`
2. Set production environment variables
3. Deploy to hosting platform (Vercel recommended)
4. Ensure backend API is accessible from deployed frontend

## Troubleshooting

**Issue**: "Invalid token" errors
**Solution**: Verify BETTER_AUTH_SECRET matches between frontend and backend

**Issue**: CORS errors
**Solution**: Configure CORS in backend to allow frontend domain

**Issue**: "User not found" errors
**Solution**: Ensure user_id in JWT matches the user_id in API calls