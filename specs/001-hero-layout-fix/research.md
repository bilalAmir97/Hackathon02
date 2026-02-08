# Research: Hero Subheadline Layout Correction

## Current State Analysis

### Issue Identification
The hero subheadline in `Phase-II/frontend/src/app/page.tsx` (line 153-158) currently has the class `break-words` which may be causing unwanted text wrapping behavior. The element is:

```jsx
<p
  ref={subheadlineRef}
  className="text-lg sm:text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed break-words"
>
  Streamline your workflow with our advanced task management platform. Built for teams who demand excellence and efficiency.
</p>
```

### Key Findings

1. **CSS Classes Analysis**:
   - `break-words`: This class uses `overflow-wrap: break-word` which can cause words to break mid-character
   - `leading-relaxed`: Sets line height to 1.625, which is relatively spacious
   - `max-w-3xl`: Constrains width but doesn't prevent line breaks within words
   - `text-center`: Applied to parent container, center-aligns text

2. **Layout Structure**:
   - The hero section uses flexbox with `flex items-center justify-center`
   - Text is centered with `mx-auto` on the subheadline
   - Container has responsive padding `px-4 sm:px-6 lg:px-8`

3. **Potential Issues**:
   - The `break-words` class is likely causing the vertical stacking effect
   - Flexbox alignment might be contributing to layout issues on narrow screens
   - GSAP animations could be affecting layout during transition

4. **Animation Impact**:
   - GSAP animations are applied to the subheadline element via `subheadlineRef`
   - Animations use `y` transforms which could affect layout
   - Delay mechanism (100ms) exists to prevent hydration issues

## Proposed Solution

### Immediate Fixes
1. **Remove `break-words` class**: This is the primary cause of unwanted word breaking
2. **Consider `whitespace-normal`**: Ensure text flows normally
3. **Review flexbox constraints**: Ensure proper container sizing
4. **Adjust GSAP animations**: Ensure they don't affect layout properties

### Implementation Strategy
1. **Replace `break-words` with `break-normal`** to allow normal word wrapping
2. **Maintain responsive typography** with existing size classes
3. **Preserve existing animations** but ensure they only affect opacity/position, not layout
4. **Test across breakpoints** to ensure consistent behavior

## Decision

**Decision**: Remove the `break-words` class from the subheadline element and replace with appropriate text wrapping behavior that allows natural line breaks based on container width without breaking individual words.

**Rationale**: The `break-words` class is causing words to break mid-character when space is constrained, creating the vertical stacking effect. Using `break-normal` or removing the class entirely will allow natural text flow while still wrapping to new lines when needed.

**Alternatives Considered**:
- Keep `break-words` with adjusted container width: Would maintain current behavior
- Use `truncate` instead: Would ellipsis text instead of wrapping
- Use `break-all`: Would break at arbitrary points, potentially worse than current