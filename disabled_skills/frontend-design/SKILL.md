---
name: frontend-design
description: Design and implement web components, pages, and applications, or refine an existing web UI. Use for frontend layout, typography, color, motion, and interaction work while respecting the project's brand, accessibility, and technical constraints.
license: Complete terms in LICENSE.txt
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---

# Frontend Design

Implement working frontend code with a deliberate visual direction. Preserve the user's requirements and an existing project's design system, framework, and conventions.

## Design thinking

Establish the interface's purpose, audience, constraints, and defining visual idea from the brief.
Ask only about missing choices that materially change the result.
A focused edit can retain the current direction; a new design can explore a stronger one.

Choose a coherent tone: restrained minimalism, editorial, playful, industrial, organic, luxury, brutalist, geometric, or another direction grounded in the content. The goal is intentional execution; every interface need not choose an extreme style.

## Five design priorities

1. **Accessibility:** use semantic HTML, meaningful labels, visible focus, and keyboard navigation. Target at least 4.5:1 contrast for ordinary text. Preserve readable glyph coverage and honor reduced-motion preferences.
2. **Interaction:** provide clear states and usable controls. The existing Pro Max guidance targets 44×44 pt touch areas and under 100 ms interaction delay; treat them as design targets and measure before claiming they are met.
3. **Layout stability:** reserve space for loading media and components. Target CLS below 0.1; a source review alone does not establish a measured score.
4. **Consistency:** apply a coherent palette, hierarchy, spacing, and component language. Fit new work into the existing brand unless a redesign is requested.
5. **Responsive layout:** use systematic breakpoints and test narrow and wide views. Avoid unintended horizontal overflow; intentional horizontal regions need usable navigation.

## Aesthetic techniques

- **Typography:** choose readable fonts with character when the brief allows.
  A distinctive display face can pair with a restrained body face.
  Existing brand fonts, Inter, Arial, system fonts, or accessible fallbacks are valid when they serve the project; do not replace them merely to avoid a common choice.
- **Color and theme:** use consistent tokens or CSS variables. Choose a dominant palette and purposeful accents; balance contrast and content rather than repeating a default gradient.
- **Motion:** use CSS transitions for simple interfaces and an existing motion library when it fits the stack.
  A coordinated reveal or a useful state transition can be enough.
  The Pro Max reference suggests 150–300 ms transitions; make motion optional where it does not aid interaction and respect reduced motion.
- **Composition:** choose intentional spacing, asymmetry, visual density, or negative space. Keep overlaps and grid-breaking effects clear of required text, focus indicators, and controls.
- **Depth and detail:** contextual textures, borders, shadows, gradients, and layered transparency can support the visual idea. Use them selectively; a plain background is valid when it gives the content clarity.

Bento grids can organize asymmetrical content.
Glassmorphism can use backdrop blur above 10 px with a subtle border, provided contrast remains legible.
Modern Minimalist work can use generous space, line height 1.6–1.75, and restrained shadows.
These are available styles, not requirements for every interface.

## Implementation and completion

Use the project's stack.
For a new React or Next.js project, Tailwind, Lucide, Radix UI, and shadcn/ui are available choices; avoid introducing them into an existing project without a concrete need.
Co-locate components, styles, and relevant tests according to repository conventions.

Match implementation complexity to the brief: dense visual work may need more structure, while a restrained interface benefits from precise spacing and typography. Deliver a functioning page or component, not only a mockup.

Run the project's required build or checks, render the changed view, inspect narrow and wide layouts, and exercise the primary interaction and keyboard path.
Fix observed failures and rerun affected checks.
A low-risk visual edit needs focused verification, not a new test suite that mirrors the change.
Report unavailable checks and unmeasured performance targets accurately.

Keep edits within the authorized project, preserve unrelated user changes, and retain a recoverable copy before replacing user files. External publication requires user authorization. Report in Traditional Chinese unless the user requests another language.
