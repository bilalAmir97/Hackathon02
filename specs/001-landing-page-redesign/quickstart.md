# Quickstart Guide: Landing Page UI Redesign

## Development Setup

### Prerequisites
- Node.js 18+ (or 20+ for optimal performance)
- PNPM package manager (recommended) or npm/yarn
- Git version control
- Modern web browser (Chrome/Firefox/Edge) for development

### Initial Setup
1. Clone the repository (if not already done):
   ```bash
   git clone <your-repo-url>
   cd Phase-II/frontend
   ```

2. Install dependencies:
   ```bash
   # Using pnpm (recommended)
   pnpm install

   # Or using npm
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.local.example .env.local
   ```

4. Update environment variables in `.env.local`:
   - `NEXT_PUBLIC_BETTER_AUTH_URL`: Your backend API URL
   - `BETTER_AUTH_SECRET`: Your authentication secret
   - Add any other required variables

5. Run the development server:
   ```bash
   # Using pnpm
   pnpm dev

   # Or using npm
   npm run dev
   ```

6. Visit `http://localhost:3000` in your browser to see the application

## Available Scripts

### Development
- `pnpm dev` - Start development server with hot reloading
- `pnpm dev --turbo` - Use Next.js Turbo mode for faster compilation

### Building
- `pnpm build` - Create optimized production build
- `pnpm start` - Run production server (after building)

### Testing
- `pnpm test` - Run unit tests
- `pnpm test:e2e` - Run end-to-end tests
- `pnpm test:watch` - Run tests in watch mode

### Linting & Formatting
- `pnpm lint` - Check code for linting errors
- `pnpm lint:fix` - Automatically fix linting errors
- `pnpm format` - Format code with Prettier
- `pnpm type-check` - Run TypeScript type checking

## Project Structure

### Key Directories
```
Phase-II/frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/         # Authentication pages (login/register)
│   │   ├── dashboard/      # Dashboard pages
│   │   └── globals.css     # Global styles
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Base UI components
│   │   ├── providers/     # Context providers
│   │   └── tasks/         # Task-specific components
│   ├── hooks/              # Custom React hooks
│   │   └── useGsapAnimations.ts # GSAP animation hooks
│   ├── lib/                # Utility functions
│   │   └── gsap-animations.ts # GSAP animation library
│   └── services/           # API services
├── public/                 # Static assets
├── tests/                  # Test files
└── next.config.js          # Next.js configuration
```

### Key Files for Landing Page Redesign
- `src/app/page.tsx` - Main landing page with hero section
- `src/app/(auth)/login/page.tsx` - Login page
- `src/app/(auth)/register/page.tsx` - Registration page
- `src/lib/gsap-animations.ts` - GSAP animation utilities
- `src/hooks/useGsapAnimations.ts` - React hooks for GSAP
- `src/app/globals.css` - Global CSS styles

## Development Workflow

### Making Changes to Landing Page
1. Edit `src/app/page.tsx` for main landing page changes
2. Edit `src/app/(auth)/login/page.tsx` for login page changes
3. Edit `src/app/(auth)/register/page.tsx` for registration page changes
4. Update animations in `src/lib/gsap-animations.ts` or `src/hooks/useGsapAnimations.ts`
5. Add any new global styles to `src/app/globals.css`

### Running with Specific Port
```bash
PORT=4000 pnpm dev
```

### Environment Variables
The application expects the following environment variables:
- `NEXT_PUBLIC_BETTER_AUTH_URL` - Backend API URL for authentication
- `BETTER_AUTH_SECRET` - Secret key for JWT verification
- `DATABASE_URL` - Database connection string (if applicable)
- `NEXT_PUBLIC_APP_ENV` - Application environment ('development', 'production')

## Testing the Changes

### Visual Testing
1. After making UI changes, test in development mode:
   ```bash
   pnpm dev
   ```

2. Visit the following pages to verify changes:
   - Landing page: `http://localhost:3000`
   - Login page: `http://localhost:3000/login`
   - Register page: `http://localhost:3000/register`

### Responsive Testing
Test your changes across different screen sizes using browser dev tools:
- Mobile: 375×667, 414×896
- Tablet: 768×1024, 834×1194
- Desktop: 1366×768, 1920×1080
- Ultra-wide: 2560×1080, 3840×2160

### Performance Testing
1. Use Chrome DevTools Performance tab to check animation performance
2. Run Lighthouse audit to verify performance scores
3. Monitor bundle size to ensure it stays reasonable

## Common Commands

### Check Dependencies
```bash
pnpm outdated
```

### Update Dependencies
```bash
pnpm update
```

### Clean Installation
```bash
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

### Production Build Verification
```bash
pnpm build
pnpm start
```

## Troubleshooting

### Common Issues
- **Module not found errors**: Run `pnpm install` to ensure all dependencies are installed
- **Environment variables missing**: Check `.env.local` file exists with required variables
- **Hot reload not working**: Restart dev server with `pnpm dev`
- **Styles not updating**: Clear browser cache and restart dev server

### Animation Performance Issues
- Check for layout-affecting properties in animations
- Verify only transform and opacity are being animated
- Monitor DevTools Performance tab for frame drops

### Build Errors
- Run `pnpm type-check` to identify TypeScript issues
- Run `pnpm lint` to identify code quality issues
- Check that all imports are valid and files exist

## Deployment Preparation

### Environment Variables for Production
Ensure these variables are set in your hosting environment:
- `NEXT_PUBLIC_BETTER_AUTH_URL` - Production backend URL
- `BETTER_AUTH_SECRET` - Production secret key
- Any other required environment variables

### Optimization
- Verify all images are properly optimized
- Check that animations perform well on target devices
- Run lighthouse audit to identify performance improvements