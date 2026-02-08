# Data Model: Premium Futuristic Scan-Line Enhancement

## Entities

### ScanLineConfig
Extends the existing scan line configuration system found in the current implementation to support both ambient and event layers

- **id**: string (unique identifier for the configuration)
- **type**: enum ['ambient', 'event'] (determines animation behavior)
- **opacity**: number (0.02-0.06 for ambient, brighter for event)
- **duration**: number (8-14s for ambient, 0.6-1.2s for event)
- **colorGradient**: string (CSS gradient definition, e.g. "electric blue to indigo")
- **blurIntensity**: number (controls the soft glow effect)
- **animationSpeed**: number (pixels per second for movement)
- **enabled**: boolean (whether this scan line type is active)
- **themeAdaptation**: boolean (whether to adapt to light/dark mode)
- **integrationType**: enum ['overlay', 'background', 'hybrid'] (how it integrates with existing scanline system)

### ScanLineEffect
Represents an active scan line instance with current state, compatible with existing GSAP animation utilities in `gsap-animations.ts`

- **id**: string (unique identifier)
- **configId**: string (reference to ScanLineConfig)
- **type**: enum ['ambient', 'event']
- **position**: number (current position in animation cycle)
- **isActive**: boolean (whether animation is currently running)
- **createdAt**: Date (timestamp when effect was initiated)
- **completedAt**: Date (timestamp when effect finished, null if ongoing)
- **layerIndex**: number (z-index layer for proper stacking with existing components)

### AccessibilitySettings
Enhances the existing accessibility handling to include scan line specific preferences, building on the current accessibility patterns in the codebase

- **userId**: string (user identifier, optional for global settings)
- **prefersReducedMotion**: boolean (whether user prefers reduced motion, extends existing motion preferences)
- **ambientFallbackStyle**: enum ['static-gradient', 'subtle-pulse', 'none'] (fallback for ambient when reduced motion enabled)
- **eventFallbackEnabled**: boolean (whether event scan lines are enabled with reduced motion)
- **existingScanlineIntegration**: boolean (how settings interact with existing scanline implementation)

## Relationships

- `ScanLineConfig` 1 ←→ * `ScanLineEffect` (one config can be used by multiple active effects)
- `AccessibilitySettings` 1 ←→ * `ScanLineEffect` (settings influence how effects are displayed for a user)

## Validation Rules

- **ScanLineConfig.opacity**: Must be between 0 and 1
- **ScanLineConfig.duration**: For ambient: 8-14s, For event: 0.6-1.2s
- **ScanLineConfig.animationSpeed**: Must be positive number
- **ScanLineConfig.type**: Must be either 'ambient' or 'event'

## State Transitions

### ScanLineEffect
- **Inactive** → **Active**: When animation starts
- **Active** → **Completed**: When animation finishes (event) or continues (ambient)
- **Active** → **Paused**: When user switches to reduced motion mode
- **Paused** → **Active**: When user switches back to normal mode