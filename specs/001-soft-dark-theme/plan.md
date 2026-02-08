# Implementation Plan: Dashboard UI Rebuild (Modern Soft Dark SaaS)

**Branch**: `001-soft-dark-theme` | **Date**: 2026-01-24 | **Spec**: [specs/001-soft-dark-theme/spec.md](./spec.md)
**Input**: Feature specification from `/specs/[001-soft-dark-theme]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Complete rebuild of the dashboard UI from scratch using a modern, professional, soft dark SaaS design with clean layout, minimal motion, and high usability. This involves removing the existing dashboard UI (layout, styles, components, animations) and recreating it with a soft dark theme following professional SaaS standards: left sidebar navigation, top navigation bar, and central content workspace. The implementation preserves all existing backend API integrations and authentication logic while delivering a premium user experience with glassmorphism effects, subtle animations, and responsive design.

## Technical Context

**Language/Version**: TypeScript/JavaScript, React 19.2.1, Next.js 16.0.10
**Primary Dependencies**: Tailwind CSS, GSAP, Framer Motion (frontend only)
**Storage**: Neon Serverless PostgreSQL (existing backend - no changes)
**Testing**: Jest, React Testing Library (existing)
**Target Platform**: Web application with responsive design for mobile, tablet, desktop, and ultra-wide screens
**Project Type**: Frontend UI enhancement (no backend changes)
**Performance Goals**: 60fps animations across mid-range and high-end devices, with 30fps acceptable on lower-end devices
**Constraints**: Maintain existing backend API integrations and authentication logic, zero layout shift during animations, support reduced-motion accessibility preferences
**Scale/Scope**: Single dashboard page UI overhaul with task management functionality preservation

**Design Tokens**:
- Background gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) (soft deep dark to midnight blue)
- Primary accent: linear-gradient(to right, #38bdf8 0%, #6366f1 100%) (soft blue to indigo)
- Secondary accent: #22d3ee (soft neon cyan) for glow effects
- Glassmorphism: rgba(30, 41, 59, 0.4) with backdrop-filter: blur(12px)
- Borders/dividers: soft muted contrast rgba(148, 163, 184, 0.1)
- Responsive breakpoints: mobile: <640px, tablet: 640px-1024px, desktop: >1024px, ultra-wide: >1920px
**Constraints**: Maintain existing backend API integrations and authentication logic, zero layout shift during animations, support reduced-motion accessibility preferences

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Phase II compliance: Feature is UI enhancement, not advanced/intermediate feature addition
- ✅ Technology constraints: Using specified stack (Next.js 16+, Tailwind, TypeScript)
- ✅ Security compliance: Maintaining existing JWT-based authentication via Better Auth (no changes)
- ✅ Feature level: Basic Level (task management) with premium UI enhancements
- ✅ Clean architecture: Frontend UI layer only, preserving existing backend architecture
- ✅ Contract-first: Maintaining existing API contracts (no backend changes)

## Project Structure

### Documentation (this feature)

```text
specs/001-soft-dark-theme/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (Frontend Only - No Backend Changes)

```text
Phase-II/frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── page.tsx          # COMPLETELY REPLACED with new soft dark UI
│   │   │   └── layout.tsx        # Updated for new navigation structure
│   │   └── (auth)/               # Authentication routes (UNCHANGED - uses existing Better Auth)
│   ├── components/
│   │   ├── ui/                   # Updated reusable UI components
│   │   ├── tasks/                # Updated task-specific components with soft dark styling
│   │   ├── navigation/           # NEW sidebar/top navigation components
│   │   └── dashboard/            # NEW dashboard-specific components
│   ├── hooks/
│   │   └── useTaskManager.ts     # Updated for new UI interactions (no backend changes)
│   ├── styles/
│   │   └── globals.css           # Updated with soft dark design tokens
│   └── lib/
│       └── api-client.ts         # Existing API client (UNCHANGED - connects to existing backend)
└── public/
    └── [assets for new UI]       # New graphics/animations if needed
```

**Structure Decision**: Frontend-only UI overhaul. No changes to backend infrastructure (Better Auth, Neon PostgreSQL, API endpoints). The new dashboard UI will be implemented in the existing Next.js app router structure while maintaining all existing backend API integrations and authentication flows.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| | | |
