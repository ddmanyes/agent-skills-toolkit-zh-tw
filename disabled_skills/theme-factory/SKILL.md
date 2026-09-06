---
name: theme-factory
description: Apply a named bundled color/font theme or create a requested custom theme for slides, documents, or HTML artifacts. Use when the user asks to select or apply a theme; preserve an existing brand or specified theme.
license: Complete terms in LICENSE.txt
---


# Theme Factory Skill

This skill provides a curated collection of professional font and color themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any artifact.

## Purpose

To apply consistent, professional styling to presentation slide decks, use this skill. Each theme includes:
- A cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- A distinct visual identity suitable for different contexts and audiences

## Usage Instructions

To apply styling to a slide deck or other artifact:

1. **Use the existing choice**: If the user already specified a bundled theme, custom palette, or brand, apply it without asking for confirmation again.
2. **Support selection**: If the user asks to choose among themes, show [theme-showcase.pdf](theme-showcase.pdf) unchanged and ask for their choice. If they delegate the choice, select a fitting theme and state it.
3. **Read one theme**: Load the corresponding file from the theme list below, then apply its colors and fonts to the artifact.
4. **Check the result**: Inspect contrast, glyph coverage, readable fallback fonts, and consistent use across the artifact.

## Themes Available

The following 10 themes are available, each showcased in `theme-showcase.pdf`:

1. [Ocean Depths](themes/ocean-depths.md) - Professional and calming maritime theme
2. [Sunset Boulevard](themes/sunset-boulevard.md) - Warm and vibrant sunset colors
3. [Forest Canopy](themes/forest-canopy.md) - Natural and grounded earth tones
4. [Modern Minimalist](themes/modern-minimalist.md) - Clean and contemporary grayscale
5. [Golden Hour](themes/golden-hour.md) - Rich and warm autumnal palette
6. [Arctic Frost](themes/arctic-frost.md) - Cool and crisp winter-inspired theme
7. [Desert Rose](themes/desert-rose.md) - Soft and sophisticated dusty tones
8. [Tech Innovation](themes/tech-innovation.md) - Bold and modern tech aesthetic
9. [Botanical Garden](themes/botanical-garden.md) - Fresh and organic garden colors
10. [Midnight Galaxy](themes/midnight-galaxy.md) - Dramatic and cosmic deep tones

## Theme Details

Each theme is defined in the `themes/` directory with complete specifications including:
- Cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- Distinct visual identity suitable for different contexts and audiences

## Application Process

After a preferred theme is selected:
1. Read the corresponding theme file from the `themes/` directory
2. Apply the specified colors and fonts consistently throughout the deck
3. Ensure proper contrast and readability
4. Maintain the theme's visual identity across all slides

## Create your Own Theme
To handle cases where none of the existing themes work for an artifact, create a custom theme.
Based on provided inputs, generate a new theme similar to the ones above.
Give the theme a similar name describing what the font/color combinations represent.
Use any basic description provided to choose appropriate colors/fonts.
If the user authorized you to choose or create and apply the theme, show the resulting palette as part of the deliverable and apply it.
If they asked to select a custom theme before application, present the concrete palette and font choices for that selection first.

## Completion

Deliver the styled artifact after checking the rendered result against the selected theme and required content.
Correct mismatches and repeat the affected check.
If a font or renderer is unavailable, report the actual fallback or unverified layout.
Preserve a recoverable copy before replacing an existing artifact; keep the bundled showcase unchanged.
