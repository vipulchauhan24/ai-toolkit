# Colour

## Structure

Each palette defines the colour tokens in `system.md`, once for light and once for dark. Write values in OKLCH, with a hex fallback where the project needs one.

Build neutrals with a slight tint of the accent's hue, so that the greys belong to the palette.

## The palette

The palette is chosen by `design-md` and written to `DESIGN.md` and `design.css`, with every token's light and dark value and its use. Build only from it. Never write a colour value in a component, and never change a palette value. If a pair fails contrast, report it.

### A second button colour

Use `--accent-2` only when the page has two distinct actions of similar weight, such as "Hire me" and "Read the case study", or "Start a trial" and "Book a demo". The concept sets `two_actions`. At most two filled button colours on a page, never for links or focus, and not on app screens, where a second filled colour means status. Otherwise the second button is an outline.

## Using colour

- One action colour. It marks the main action and a few points of emphasis. If everything is accented, nothing is. A second button colour follows the rule above.
- Neutrals do most of the work.
- Status colours mean status only: never use green or red as decoration.
- Never use colour alone to carry meaning. Add a word or icon.
- On app screens, keep colour for data, status and the main action.

## Contrast minimums

| Thing | Minimum |
|---|---|
| Normal text | 4.5:1 |
| Large text: 24px and up, or 18.5px bold and up | 3:1 |
| Control boundaries and meaningful icons | 3:1 |
| Focus ring against its surroundings | 3:1 |
| Placeholder text | 4.5:1 |

Disabled controls are exempt, but should still be readable. Text over photographs needs a scrim or a solid panel, measured against the brightest area behind it.

Check every text and background pair with the contrast script. Check both themes.

## Building a palette

1. Choose the accent's hue and how vivid it is.
2. Build a neutral ramp by changing lightness in even steps and keeping chroma very low.
3. Lower chroma as the lightness approaches white or black, so colours stay in range.
4. Assign roles: `--bg`, `--surface`, `--surface-2`, then the three inks, then lines.
5. Pick status colours that sit comfortably with the accent. If the accent is green, use it as `--positive`.
6. Test every pair.

## Dark theme

A dark theme is designed. Do not invert the light one.

- Backgrounds are very dark neutrals, tinted slightly. Use pure black only if the design is built around it.
- Raise a surface by making it lighter, since shadows barely show on dark.
- Reduce accent chroma slightly, so it does not vibrate against the background.
- Soft status backgrounds become dark tints.
- Body text is off-white, to lower glare.
- Set `color-scheme: dark`, and match `theme-color` to the page background.

## Avoid

- Purple-to-blue gradients on white or on black, the common default of generated pages.
- Gradient text as a habit.
- Glowing borders and neon on dark.
- Two action colours with no second action to justify them.
- A heavy coloured sidebar beside a light canvas.
