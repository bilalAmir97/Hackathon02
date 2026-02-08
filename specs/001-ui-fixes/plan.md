# Implementation Plan: UI Fixes (Landing, Login, Register)

**Branch**: `001-ui-fixes` | **Date**: 2026-01-16 | **Spec**: [link to spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ui-fixes/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan addresses UI layout, sizing, and animation issues causing distorted landing, login, and register UIs in the Phase II frontend application. The implementation will stabilize layouts, fix card sizing issues, and resolve GSAP animation conflicts while preserving the premium futuristic design aesthetic. The solution will ensure proper responsive behavior across desktop, tablet, and mobile breakpoints with accessibility compliance (WCAG 2.1 AA) and performance targets (pages load < 2s, animations at 60fps).

## Technical Context

**Language/Version**: TypeScript 5.x, JavaScript ES2022
**Primary Dependencies**: Next.js 16+ (App Router), Tailwind CSS, GSAP (GreenSock Animation Platform), Better Auth
**Storage**: [N/A - frontend only changes]
**Testing**: Playwright for visual regression testing, Jest for unit tests
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend only)
**Performance Goals**: Pages load in under 2 seconds, animations run at 60fps with 100% success rate
**Constraints**: Work limited to Phase-II/frontend (no backend changes), use existing design system tokens and GSAP, follow App Router conventions and server/client component boundaries, respect reduced-motion preferences
**Scale/Scope**: Single-page application with landing, login, and register views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Phase Boundary Compliance**: This is a Phase II feature (Full-Stack Web Application) with Basic Level features only
- ✅ **Technology Constraint Compliance**: Uses Next.js 16+, TypeScript, Tailwind CSS, GSAP - all compliant with constitution
- ✅ **Feature Level Compliance**: Addresses Basic Level features (UI layout/styling fixes)
- ✅ **Architecture Compliance**: Frontend-only changes, no backend modifications
- ✅ **Security Compliance**: No security implications as this is a UI layout fix
- ✅ **Performance Compliance**: Meets performance goals (pages load < 2s, animations at 60fps)
- ✅ **Accessibility Compliance**: Follows WCAG 2.1 AA standards as specified

## Project Structure

### Documentation (this feature)

```text
specs/001-ui-fixes/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Phase-II/frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/          # Authentication-related pages
│   │   │   ├── callback/    # Auth callback handler
│   │   │   ├── login/page.tsx # Login page
│   │   │   └── register/page.tsx # Register page
│   │   ├── api/             # API routes
│   │   │   └── auth/[...all]/ # Better Auth API route
│   │   ├── dashboard/       # Dashboard page
│   │   ├── globals.css      # Global styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Landing page
│   ├── components/          # Reusable UI components
│   │   ├── providers/       # Provider components
│   │   ├── tasks/           # Task-related components
│   │   ├── ui/              # Base UI components (Input, Button, etc.)
│   │   └── ProtectedRoute.tsx # Route protection component
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   │   └── api-client.ts    # API client utilities
│   ├── styles/              # Style sheets
│   │   └── globals.css      # Global styles and animations
│   └── types/               # TypeScript type definitions
├── public/                  # Static assets
├── next.config.ts           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Project dependencies
```

**Structure Decision**: Web application structure selected as this is a frontend-only UI fix for the Phase II web application. The changes will be contained within the Phase-II/frontend directory with existing component organization. UI fixes will primarily affect the auth pages (login, register) and the landing page (page.tsx), with potential minor updates to globals.css for styling fixes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [No violations found] | [No violations found] |
