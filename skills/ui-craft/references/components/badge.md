# Badge

**Use for** a short status or category, beside the thing it describes.

- Height 20 to 24px, padding `--space-2`, `--text-xs`, weight 500.
- Radius `--radius-sm` or `--radius-full`.
- A soft colour token as background with dark matching text, such as `--positive-soft` with `--positive`, at 4.5:1. Neutral uses `--surface-2` and `--ink-2`.
- Does not shrink or wrap: `flex: none; white-space: nowrap`.

**Avoid:** a badge above every heading. Solid bright fills in lists. Two badges that say the same thing. "New" that never goes away.

A combo's highlight colour is `.badge--highlight` (`--highlight` with `--on-highlight`), for tags and markers.
