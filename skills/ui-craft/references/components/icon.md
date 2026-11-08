# Icon

**Every project uses Tabler Icons, and only Tabler Icons.** Outline style by default. Filled only to show a selected state.

| Context | Size | Stroke |
|---|---|---|
| With `--text-xs` or `--text-sm` | 16px | 1.75 to 2 |
| With `--text-base` | 20px | 2 |
| Standalone, features | 24px | 1.75 to 2 |
| Large, rare | 32px | 1.5 |

- Colour comes from `currentColor`.
- Icon gap to its label is `--space-2`.
- Icon-only buttons have an `aria-label`. Decorative icons have `aria-hidden="true"`.
- Copy only the SVGs a page uses into the project.

**Brand and tech logos:** use Tabler's `brand-*` icons, in one colour. If the brand isn't in Tabler, write its name as text. PostgreSQL and Webpack are known to be missing. Never draw a look-alike, and never mix in another icon set.

**Avoid:** an icon on everything. Icons in coloured circles or tinted squares. Emoji as icons.
