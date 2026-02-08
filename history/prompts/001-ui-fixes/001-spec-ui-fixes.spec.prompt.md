---
id: 001
title: spec-ui-fixes
stage: spec
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: ui-fixes
branch: 001-ui-fixes
user: bilal-amir
command: "/sp.specify Spec-3 UI Fixes — Landing / Login / Register Card Corrections (Phase-II/frontend)"
labels: [spec, ui, frontend, layout, accessibility]
links:
  spec: ../specs/001-ui-fixes/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ui-fixes/spec.md
  - specs/001-ui-fixes/checklists/requirements.md
tests:
  - specs/001-ui-fixes/checklists/requirements.md
---

## Prompt

Spec-3 UI Fixes — Landing / Login / Register Card Corrections (Phase-II/frontend)

Target audience:
Claude Code acting as a frontend engineer/designer tasked with diagnosing and fixing major visual/layout regressions on the landing, login, and register pages of the Phase-II frontend.

Focus:
Identify and resolve root causes that produce the narrow, vertically distorted auth cards and misplaced hero content. Deliver robust, responsive, pixel-consistent fixes that preserve the premium futuristic design, GSAP motion, and ambient scan-line while removing layout shift and distortion.

Success criteria (must all be met)
- Landing hero displays centered, correctly-scaled headline and CTA at desktop/tablet/mobile breakpoints (no clipped or vertically-stretched content).
- Login and Register card components render at intended width/height, maintain correct border-radius, spacing, and are horizontally centered on desktop and stacked on small viewports.
- No UI elements are squeezed into a single narrow column; layout uses expected content widths (e.g., card max-width between 340–840px depending on breakpoint).
- GSAP animations no longer cause initial layout distortion or permanent transforms that affect layout flow.
- Ambient scan-line remains behind content, with opacity and transform-only animation (no reflow).
- Accessibility: reduced-motion respected, keyboard tab order intact, form labels visible.
- Visual regression tests (desktop/tablet/mobile) pass vs. expected screenshots.

Constraints
- Work limited to Phase-II/frontend (no backend changes).
- Use existing design system tokens and GSAP; prefer CSS layout fixes before large refactors.
- Follow App Router conventions and server/client component boundaries.
- No addition of heavy external visual libraries beyond GSAP and chosen CSS system (Tailwind/CSS Modules).

## Response snapshot

Created comprehensive specification for UI fixes focusing on landing page hero display, login card layout, register card layout, and animation stability. The specification includes:

- Four prioritized user stories covering the core issues
- Twelve functional requirements addressing all success criteria
- Key entities defining the main UI components
- Nine measurable success outcomes
- Edge cases for accessibility and various viewport sizes
- A completed quality checklist validating the specification

## Outcome

- ✅ Impact: Created complete specification for UI layout fixes addressing landing page, login, and register page visual regressions
- 🧪 Tests: Quality checklist validates all requirements are testable and measurable
- 📁 Files: Created spec.md and requirements checklist in specs/001-ui-fixes/
- 🔁 Next prompts: Ready for planning phase with /sp.plan
- 🧠 Reflection: Specification covers all required success criteria while maintaining focus on user experience

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All validation criteria met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase