# Tooltip

**Use for** a short label on an icon button, or the full text of something truncated. Never for information people need to complete a task.

- `--text-xs`, padding `--space-1` by `--space-2`, `--radius-sm`, `--z-tooltip`.
- Inverted colours: `--ink` background, `--bg` text.
- Short: a few words.
- Shows after a brief delay on hover, immediately on focus. Stays visible while hovered. Dismisses on Escape.

**Touch:** tooltips don't exist on touch, so anything they say must be available another way.

**Avoid:** interactive content in a tooltip. Tooltips on disabled controls.
