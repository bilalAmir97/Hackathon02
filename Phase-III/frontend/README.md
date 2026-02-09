# TaskFlow - Premium UI & Full-Stack Integration

Welcome to TaskFlow, a premium todo application with advanced UI/UX featuring futuristic design, smooth animations, and seamless full-stack integration.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [UI System](#ui-system)
- [Animation Principles](#animation-principles)
- [Scan-Line Behavior](#scan-line-behavior)
- [Integration Points](#integration-points)
- [Performance Optimizations](#performance-optimizations)
- [Accessibility Features](#accessibility-features)
- [Responsive Design](#responsive-design)
- [API Integration](#api-integration)
- [Error Handling](#error-handling)
- [Development Setup](#development-setup)

## Architecture Overview

TaskFlow is built with Next.js 16+ using the App Router architecture with the following key technologies:

- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Styling**: Tailwind CSS with custom utility classes
- **Animations**: GSAP (GreenSock Animation Platform) for high-performance animations
- **State Management**: React Context API with custom hooks
- **Authentication**: Better Auth with JWT tokens
- **API Communication**: Custom API client with session management
- **UI Components**: Custom-built component library
- **Error Handling**: Global error boundaries and API error handling

## UI System

### Design Philosophy
The UI follows a futuristic, premium aesthetic with:

- **Glassmorphism Effects**: Semi-transparent frosted glass panels with backdrop blur
- **Gradient Backgrounds**: Subtle gradients for depth and visual interest
- **Neumorphism Accents**: Soft shadows for tactile interface elements
- **Consistent Spacing**: Systematic spacing using Tailwind's spacing scale
- **Typography Hierarchy**: Clear, readable text with appropriate weights and sizes

### Color Palette
- Primary: Blue/Purple gradient (#3B82F6 → #8B5CF6)
- Background: Dark gradient (black to gray-900)
- Glass Panels: RGBA white with 30% transparency
- Text: White/light gray with appropriate contrast ratios

### Component Architecture
Components follow a hierarchical structure:
```
Organisms (Pages)
├── Molecules (Complex UI Elements)
│   ├── Atoms (Basic UI Elements)
│   └── Utilities (Helper Functions)
└── Templates (Layout Patterns)
```

## Animation Principles

### Performance-Focused Animations
All animations are optimized for 60fps performance on mid-range devices:

- **GPU-Accelerated Properties**: Using `transform` and `opacity` exclusively
- **Reduced Duration**: Shorter animation durations (0.2s - 0.6s range)
- **Simple Easing**: Power-based easing functions for performance
- **Overwrite Management**: Proper cleanup to prevent memory leaks
- **Staggered Sequences**: Sequential animations to avoid overwhelming the UI

### Animation Types
1. **Entrance Animations**: Fade-in with slight movement for content appearance
2. **Hover Effects**: Subtle scaling (1.03x) with quick transitions (150ms)
3. **Page Transitions**: Fade transitions between routes
4. **Interactive Feedback**: Quick visual responses to user actions
5. **Loading States**: Skeleton screens and animated placeholders

### GSAP Implementation
- **Timeline Management**: Proper cleanup of GSAP timelines
- **ScrollTrigger Integration**: Scroll-based animations with performance considerations
- **Force3D**: Promotes elements to GPU for better performance
- **Clear Properties**: Removes transform properties after animations complete

## Scan-Line Behavior

### Visual Effect
The scan-line is a signature futuristic element that:
- Moves vertically down the screen continuously
- Creates a cyberpunk/augmented reality aesthetic
- Uses a blue gradient with transparency
- Has a subtle glow effect for depth

### Technical Implementation
```css
.scan-line {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.8), transparent);
  z-index: 9999;
  pointer-events: none;
  animation: scanLine 3s linear infinite;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

@keyframes scanLine {
  0% {
    top: -10px;
  }
  100% {
    top: 100vh;
  }
}
```

### Performance Considerations
- Uses hardware acceleration via CSS transforms
- Single DOM element for minimal overhead
- Disabled on reduced motion preferences
- Fixed positioning to avoid layout recalculations

## Integration Points

### Frontend-Backend Communication
- **API Client**: Centralized API client with Better Auth integration
- **Session Management**: Automatic JWT token handling
- **Error Handling**: Structured error responses with user-friendly messages
- **Loading States**: Global and component-level loading indicators
- **Token Refresh**: Automatic token refresh with request queuing

### Authentication Flow
1. User authenticates via Better Auth
2. JWT token stored in httpOnly cookie
3. Token automatically attached to API requests
4. Token refresh mechanism handles expiration
5. Failed requests queued during refresh process

### Component Integration
- **Context Providers**: Auth, Toast, and Transition providers wrapped around application
- **Custom Hooks**: Reusable logic for common operations
- **Event Handling**: Proper cleanup of event listeners
- **Memory Management**: Prevents memory leaks in animations

## Performance Optimizations

### Animation Performance
- Limited animation duration to 0.6s maximum
- Used `overwrite: 'auto'` to prevent animation conflicts
- Applied `force3D: true` for GPU acceleration
- Implemented proper cleanup with timeline killing

### Loading Optimizations
- Skeleton screens prevent layout shift
- Optimistic updates for immediate UI feedback
- Code splitting for faster initial loads
- Image optimization with Next.js Image component

### Memory Management
- Event listener cleanup in useEffect
- GSAP timeline destruction
- Reference cleanup in components
- Proper state management to prevent unnecessary renders

## Accessibility Features

### ARIA Attributes
- Proper landmark roles (banner, main, region, alert)
- Label associations for form elements
- Status updates for dynamic content
- Focus management for keyboard navigation

### Keyboard Navigation
- Logical tab order
- Visible focus indicators
- Skip links for main content
- Accessible modal and dropdown components

### Screen Reader Support
- Semantic HTML structure
- Alternative text for images
- Live regions for dynamic updates
- Proper heading hierarchy

### Reduced Motion
- Respects `prefers-reduced-motion` media query
- Provides alternatives to motion-based cues
- Maintains functionality without animations

## Responsive Design

### Breakpoints
- **Mobile**: Up to 639px
- **Tablet**: 640px - 1023px
- **Desktop**: 1024px and above

### Responsive Features
- Flexible grid layouts using CSS Grid and Flexbox
- Scalable typography with clamp() for fluid sizing
- Adaptive spacing that scales with viewport
- Touch-friendly targets for mobile interactions
- Orientation-aware layouts

### Mobile-First Approach
- Base styles for mobile devices
- Progressive enhancement for larger screens
- Touch gestures and interactions optimized
- Performance considerations for slower connections

## API Integration

### Client Architecture
- **Centralized Client**: Single API client module
- **Type Safety**: Full TypeScript support with interface definitions
- **Error Handling**: Structured error responses with proper typing
- **Loading States**: Integrated loading state management

### Authentication Integration
- **Session Verification**: Automatic session checks
- **Token Management**: Transparent JWT handling
- **Error Recovery**: Automatic session refresh attempts
- **Redirect Handling**: Proper navigation on auth failures

### Data Operations
- **CRUD Operations**: Complete task management functionality
- **Optimistic Updates**: Immediate UI feedback
- **Error Recovery**: Automatic rollback on failures
- **Validation**: Client-side validation with server-side backup

## Error Handling

### Global Error Boundaries
- **Root-Level Boundary**: Catches unhandled errors
- **User-Friendly Messages**: Clear error explanations
- **Recovery Options**: Refresh/retry functionality
- **Error Reporting**: Console logging for debugging

### API Error Handling
- **Structured Responses**: Consistent error format
- **User Notifications**: Toast notifications for errors
- **Automatic Retries**: For recoverable errors
- **Graceful Degradation**: Fallback behavior when possible

### Network Error Handling
- **Offline Detection**: Network status awareness
- **Retry Mechanisms**: Automatic retry for transient failures
- **Caching Strategies**: Offline capability where possible
- **User Feedback**: Clear status indicators

## Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth server URL
- `BETTER_AUTH_SECRET`: JWT secret for token verification

### Available Scripts
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

### Folder Structure
```
src/
├── app/                 # Next.js App Router pages
│   ├── (auth)/         # Authentication routes
│   ├── dashboard/      # Dashboard pages
│   └── globals.css     # Global styles
├── components/         # Reusable UI components
│   ├── providers/      # Context providers
│   ├── tasks/          # Task-specific components
│   └── ui/            # Basic UI components
├── hooks/             # Custom React hooks
├── lib/               # Utility functions and clients
└── types/             # TypeScript type definitions
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ using Next.js, TypeScript, and Tailwind CSS
