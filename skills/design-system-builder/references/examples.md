# Examples

Two typical runs. They show the shape of a run, not values to reuse.

## Example 1: Autonomous brief

User says: "create a design system for a playful fintech app for students, web only"

Actions:
1. Mode: Autonomous (text-only brief). Platform web, so the Tailwind output applies.
2. Ask once for what is missing: accessibility target, light and dark, anything fixed. The user says "just do it", so apply the defaults (WCAG 2.2 AA, both themes) and list them as assumptions.
3. Write the Direction Summary with a theme name and concrete values, and wait for the user to confirm or redirect.
4. After confirmation, build the three token layers, both themes and the component specs. Run `./scripts/check_contrast.sh <theme-name>`, fix every failing pair, then run `python3 -I scripts/build_tokens_json.py <theme-name>`.

Result: `<Theme>/` with `tokens.css`, `tokens.json`, `tailwind-theme.css`, `components.md`, `README.md`, `preview.html`, plus `contrast-reports/<theme>.txt`. The reply holds the direction summary, assumptions, checker result and file list.

## Example 2: Brand palette that fails contrast

User says: "build a design system around our brand color #F5B700 and Inter"

Actions:
1. Mode: Palette, sparse (one color and a font). Derive neutrals, accent and feedback roles and mark them as derived.
2. The brand color fails AA as a fill under a white label. Do not change it silently: report the failing pair, move the light-mode fill to the nearest passing step of the same hue, keep the original as its own pinned primitive, and use it as the dark-mode fill if it passes there.
3. Put the do/don't table for the brand color in the README.

Result: the brand value is preserved for logos and decoration, every text pair passes AA, and the summary says which fill moved and why.
