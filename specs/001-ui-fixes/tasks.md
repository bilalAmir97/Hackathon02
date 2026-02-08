# Tasks: UI Fixes (Landing, Login, Register)

**Feature**: UI Fixes — Landing / Login / Register Card Corrections
**Branch**: `001-ui-fixes`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1: Setup & Environment

- [ ] T001 Set up development environment and verify project structure in Phase-II/frontend
- [ ] T002 [P] Install Playwright for visual regression testing as specified in requirements
- [ ] T003 [P] Verify Next.js development server runs successfully

## Phase 2: Foundation & Infrastructure

- [ ] T004 Update globals.css to fix scan-line implementation with proper z-index and transform-only animation
- [ ] T005 [P] Configure responsive breakpoints (mobile <768px, tablet 768px-1023px, desktop ≥1024px) in globals.css
- [ ] T006 [P] Set up proper container/max-width constraints for auth cards (340px-840px range)
- [ ] T007 [P] Ensure reduced-motion media query properly disables animations as per WCAG 2.1 AA
- [ ] T008 [P] Implement global CSS rules to enforce content width constraints (340px-840px) across all UI elements and prevent narrow column squeezing

## Phase 3: User Story 1 - Landing Page Hero Display (Priority: P1)

**Goal**: Stabilize landing page hero section layout to ensure proper centering and scaling across all breakpoints without content clipping or vertical stretching.

**Independent Test**: Landing page hero section displays correctly at desktop, tablet, and mobile breakpoints without any clipping or vertical stretching of content. Headline and CTA button are clearly visible and properly positioned.

- [ ] T008 [US1] Refactor landing page (page.tsx) to remove layout-affecting GSAP transforms and use only transform/opacity animations
- [ ] T009 [US1] Implement proper centering for hero section content using flexbox/grid with responsive units
- [ ] T010 [US1] Fix scan-line positioning to stay behind content with proper z-index isolation
- [ ] T011 [US1] Ensure hero section scales appropriately without clipping on mobile breakpoints
- [ ] T012 [US1] Make GSAP animations interruptible as specified in requirements
- [ ] T013 [US1] Verify no vertical stretching occurs in hero content across all breakpoints
- [ ] T014 [US1] Test landing page hero display on desktop (≥1024px), tablet (768px-1023px), and mobile (<768px) breakpoints

## Phase 4: User Story 2 - Login Card Layout Fix (Priority: P1)

**Goal**: Stabilize login card component layout to ensure proper width/height, border-radius, spacing, and horizontal centering on desktop while adapting appropriately for smaller viewports.

**Independent Test**: Login card component renders at intended width and height, maintains correct border-radius and spacing, and is horizontally centered on desktop screens while adapting appropriately for smaller viewports.

- [ ] T015 [US2] Update login page layout to ensure auth card is horizontally centered on desktop
- [ ] T016 [US2] Set proper max-width constraints for login card (340px-840px range) based on viewport
- [ ] T017 [US2] Fix card stacking behavior on small viewports (<768px)
- [ ] T018 [US2] Ensure border-radius and spacing remain consistent across all breakpoints
- [ ] T019 [US2] Remove layout shifts caused by floating particle animations
- [ ] T020 [US2] Verify glassmorphism effects don't interfere with layout calculations
- [ ] T021 [US2] Test login card rendering on desktop (≥1024px), tablet (768px-1023px), and mobile (<768px) breakpoints

## Phase 5: User Story 3 - Register Card Layout Fix (Priority: P1)

**Goal**: Stabilize register card component layout to ensure proper width/height, border-radius, spacing, and horizontal centering on desktop while adapting appropriately for smaller viewports.

**Independent Test**: Register card component renders at intended width and height, maintains correct border-radius and spacing, and is horizontally centered on desktop screens while adapting appropriately for smaller viewports.

- [ ] T022 [US3] Update register page layout to ensure auth card is horizontally centered on desktop
- [ ] T023 [US3] Set proper max-width constraints for register card (340px-840px range) based on viewport
- [ ] T024 [US3] Fix card stacking behavior on small viewports (<768px)
- [ ] T025 [US3] Ensure border-radius and spacing remain consistent across all breakpoints
- [ ] T026 [US3] Remove layout shifts caused by floating particle animations
- [ ] T027 [US3] Verify glassmorphism effects don't interfere with layout calculations
- [ ] T028 [US3] Test register card rendering on desktop (≥1024px), tablet (768px-1023px), and mobile (<768px) breakpoints

## Phase 6: User Story 4 - Animation and Layout Stability (Priority: P2)

**Goal**: Ensure GSAP animations don't cause layout shifts or permanent transforms, maintaining stable and predictable UI during and after animations.

**Independent Test**: GSAP animations execute without causing initial layout distortion or leaving permanent transforms that affect the layout flow of UI elements.

- [ ] T029 [US4] Refactor GSAP animations to use only transform and opacity properties (no layout-affecting transforms)
- [ ] T030 [US4] Ensure GSAP animations are interruptible during user interactions as specified
- [ ] T031 [US4] Remove any permanent transforms that persist after animation completion
- [ ] T032 [US4] Optimize animation performance to maintain 60fps as per requirements
- [ ] T033 [US4] Verify no layout flow disruption occurs during GSAP animations
- [ ] T034 [US4] Test animation interruptibility on user interactions (click, scroll, etc.)

## Phase 7: Testing & Validation

- [ ] T035 [P] Create Playwright visual regression tests for desktop, tablet, and mobile breakpoints
- [ ] T036 [P] Run visual regression tests to verify landing page hero display across all breakpoints
- [ ] T037 [P] Run visual regression tests to verify login card layout across all breakpoints
- [ ] T038 [P] Run visual regression tests to verify register card layout across all breakpoints
- [ ] T039 [P] Verify all accessibility requirements (reduced-motion, keyboard navigation, form labels)
- [ ] T040 [P] Test page load times to ensure under 2-second performance target and animations maintain 60fps performance as specified in requirements
- [ ] T041 [P] Validate WCAG 2.1 AA compliance for all UI components
- [ ] T042 [P] Verify scan-line animation uses transform-only with no reflow impact

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T044 [P] Conduct user satisfaction evaluation of design aesthetic preservation and ensure 4.0/5.0 rating threshold is met
- [ ] T045 Review all pages to ensure premium futuristic design aesthetic is preserved
- [ ] T046 Verify no visual regressions were introduced to other parts of the application
- [ ] T047 Optimize any performance bottlenecks identified during testing
- [ ] T048 Document any changes made to the UI components for future reference
- [ ] T049 Final verification that all success criteria from spec are met

## Dependencies

- User Story 2 (Login) and User Story 3 (Register) can be developed in parallel
- User Story 1 (Landing) can be developed independently
- User Story 4 (Animation) depends on completion of other stories for testing
- Phase 7 (Testing) depends on completion of all user stories

## Parallel Execution Opportunities

- T015-T021 (Login card fixes) and T022-T028 (Register card fixes) can run in parallel
- T035-T042 (Testing tasks) can run in parallel after all user stories are complete
- T002 and T003 (Setup tasks) can run in parallel

## Implementation Strategy

1. **MVP Scope**: Complete User Story 1 (Landing Page) as the minimum viable product
2. **Incremental Delivery**: Add User Stories 2 and 3 (Login/Register) as enhancements
3. **Quality Assurance**: Complete User Story 4 (Animation) and testing phase for full feature completion