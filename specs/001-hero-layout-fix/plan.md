# Implementation Plan: Hero Subheadline Layout Correction (Landing Page)

**Branch**: `001-hero-layout-fix` | **Date**: 2026-01-18 | **Spec**: [specs/001-hero-layout-fix/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hero-layout-fix/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix the hero subheadline rendering issue where the sentence displays with vertical stacking instead of horizontal flow. The solution involves inspecting the hero container, typography CSS, and GSAP hooks to identify width constraints, flex direction, or transform side-effects causing forced line breaks. Apply responsive CSS layout and typography rules to ensure proper horizontal text flow while preserving the premium futuristic visual design and GSAP animations.

## Technical Context

**Language/Version**: TypeScript, JavaScript ES2022, Next.js 16+
**Primary Dependencies**: Next.js (App Router), Tailwind CSS, GSAP (GreenSock Animation Platform), Framer Motion
**Storage**: N/A (frontend-only layout fix)
**Testing**: Browser-based visual testing, responsive breakpoint validation
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application frontend (Phase-II/frontend)
**Performance Goals**: Sub-100ms layout rendering, smooth 60fps animations
**Constraints**: Must preserve existing premium futuristic design, GSAP animations, and theme consistency
**Scale/Scope**: Single page landing page hero section fix

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Phase Boundary Compliance**: This is a Phase II feature (frontend layout fix), which aligns with the constitution's Phase II requirements for web application features
- **Technology Constraint Compliance**: Using specified technology stack (Next.js 16+, Tailwind CSS, TypeScript) as required by constitution
- **Feature Level Compliance**: This is a frontend-only layout enhancement that improves the user experience of the existing Basic Level task features already implemented in the Phase II application. This enhancement does not replace or modify the core task functionality required by Phase II.
- **Architecture Compliance**: Following frontend-only changes that don't affect backend architecture or introduce stateful services prematurely
- **Spec Compliance**: Implementation directly follows the approved feature specification requirements
- **No New Dependencies**: The fix only modifies existing CSS classes without adding new dependencies, maintaining the existing technology stack
- **Design Preservation**: Changes preserve existing visual design and animations while fixing the layout issue

## Project Structure

### Documentation (this feature)

```text
specs/001-hero-layout-fix/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

Phase-II/
├── backend/                 # FastAPI backend with SQLModel and Neon PostgreSQL
│   ├── src/
│   │   ├── api/            # API routes and endpoints
│   │   ├── auth/           # Authentication modules
│   │   ├── domain/         # Domain models and entities
│   │   ├── middleware/     # Middleware components
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── use_cases/      # Business logic use cases
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # Database configuration
│   │   ├── dependencies.py # Dependency injection
│   │   └── main.py         # Main FastAPI application
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── pyproject.toml      # Python dependencies
└── frontend/               # Next.js 16+ frontend with App Router
    ├── src/
    │   ├── app/
    │   │   ├── globals.css    # Global styles including dark futuristic theme
    │   │   └── page.tsx       # Landing page with hero section (main target)
    │   ├── components/        # Reusable UI components
    │   │   └── ui/
    │   │       └── Navbar.tsx # Navigation component (also needs inspection)
    │   ├── hooks/            # Custom React hooks
    │   ├── lib/              # Utility functions and configuration
    │   │   ├── api-client.ts # API client wrapper
    │   │   └── auth.ts       # Better Auth configuration
    │   ├── styles/           # Additional style files
    │   └── types/            # TypeScript type definitions
    ├── public/              # Static assets
    ├── tests/               # Frontend tests (Playwright E2E)
    └── package.json         # Node.js dependencies

**Structure Decision**: This is a frontend-only layout fix targeting the hero section of the landing page. The changes will primarily affect Phase-II/frontend/src/app/page.tsx and potentially Phase-II/frontend/src/app/globals.css for any global style adjustments needed to fix the layout issue. This fits within the Phase II architecture which implements a full-stack web application with Next.js frontend and FastAPI backend, using Better Auth for authentication and Neon PostgreSQL for data persistence.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| CSS specificity adjustments | Required to override existing layout constraints | Direct Tailwind classes insufficient for complex layout fixes |
| GSAP animation coordination | Required to ensure animations don't interfere with text layout | Removing animations would degrade user experience |
