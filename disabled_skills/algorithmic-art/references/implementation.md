# p5.js implementation and viewer

Read this before creating or extending a p5.js sketch or interactive viewer. Follow the user's brief; a full philosophy document is optional.

## Reuse existing resources

- Read [generator_template.js](../templates/generator_template.js) for parameter organization, seeded randomness, classes, and render lifecycle. Reuse its structure without copying an unrelated example algorithm.
- When an interactive viewer is requested and its layout fits, read [viewer.html](../templates/viewer.html) and adapt it. Its existing seed controls, reset, regeneration, and export code are reusable. Its embedded comments describe the supplied template, not mandatory rules for every artwork.
- The supplied template uses Anthropic styling. Retain that styling only for an Anthropic brief or an explicitly requested unchanged template. Otherwise adapt UI colors, fonts, layout, and theme to the user's project, including accessible system fonts.
- For an existing application or a focused sketch, use its current layout and framework. Add only the controls needed for that task.

### TECHNICAL REQUIREMENTS

**Seeded Randomness (Art Blocks Pattern)**:
```javascript
// ALWAYS use a seed for reproducibility
let seed = 12345; // or hash from user input
randomSeed(seed);
noiseSeed(seed);
```

**Parameter Structure - FOLLOW THE PHILOSOPHY**:

To establish parameters that emerge naturally from the algorithmic philosophy, consider: "What qualities of this system can be adjusted?"

```javascript
let params = {
  seed: 12345,  // Always include seed for reproducibility
  // colors
  // Add parameters that control YOUR algorithm:
  // - Quantities (how many?)
  // - Scales (how big? how fast?)
  // - Probabilities (how likely?)
  // - Ratios (what proportions?)
  // - Angles (what direction?)
  // - Thresholds (when does behavior change?)
};
```

**To design effective parameters, focus on the properties the system needs to be tunable rather than thinking in terms of "pattern types".**

**Core Algorithm - EXPRESS THE PHILOSOPHY**:

**CRITICAL**: The algorithmic philosophy should dictate what to build.

To express the philosophy through code, avoid thinking "which pattern should I use?" and instead think "how to express this philosophy through code?"

If the philosophy is about **organic emergence**, consider using:
- Elements that accumulate or grow over time
- Random processes constrained by natural rules
- Feedback loops and interactions

If the philosophy is about **mathematical beauty**, consider using:
- Geometric relationships and ratios
- Trigonometric functions and harmonics
- Precise calculations creating unexpected patterns

If the philosophy is about **controlled chaos**, consider using:
- Random variation within strict boundaries
- Bifurcation and phase transitions
- Order emerging from disorder

**The algorithm flows from the philosophy, not from a menu of options.**

To guide the implementation, let the conceptual essence inform creative and original choices. Build something that expresses the vision for this particular request.

**Canvas Setup**: Standard p5.js structure:
```javascript
function setup() {
  createCanvas(1200, 1200);
  // Initialize your system
}

function draw() {
  // Your generative algorithm
  // Can be static (noLoop) or animated
}
```


## Interactive controls

For a full parameter-exploration viewer, expose tunable numeric parameters with labels and ranges, show current values, update the result, and provide Reset. Add color pickers only when palette editing is useful. Preserve a way to record or enter the current seed.

The supplied viewer offers Previous, Next, Random, and Jump-to-seed controls plus Regenerate, Reset, and Download PNG. Keep and verify these controls when using that viewer. A simpler sketch may expose only the requested controls while retaining a seed in code.

Match each control to the algorithm. A numeric control can use this structure:

```html
<div class="control-group">
  <label for="particle-count">Particle count</label>
  <input type="range" id="particle-count" min="100" max="2000" step="100" value="500">
  <span id="particle-count-value">500</span>
</div>
```

Connect input events to parameter updates and regenerate from the same seed. Reset simulation state, randomSeed, and noiseSeed together; for animated output also specify the time or frame needed to reproduce an exported image.

## Packaging

For a portable single HTML artifact, inline the algorithm, controls, styles, and event handlers. The supplied template loads p5.js from a CDN: that requires network access and is not an offline guarantee. Verify the dependency loads in the target browser. If offline use is requested, bundle a permitted local library copy. A requested separate JS source may also be delivered; existing apps retain their own build structure.

## Variations

Seed navigation lets users explore without generating separate files. If the user requests highlighted variations, add seed presets or a thumbnail gallery. Generate 100 variations (seeds 1–100) only when requested. Check representative seeds for empty frames, broken bounds, color imbalance, and excessive density.

## Verification and recovery

Render the delivered format, check browser errors, and exercise each visible control. Confirm the same seed, parameters, and simulation time reproduce the same composition. Confirm a different seed changes the intended randomized elements. Check export, reset, and responsive layout when present.

Fix observed problems within the authorized task and repeat the affected check. If rendering, library loading, or export is unavailable, preserve the source and state the exact unverified behavior. Describe offline or browser compatibility only to the extent tested.
