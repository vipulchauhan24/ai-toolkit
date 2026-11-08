# Card

**Use for** separate objects of the same kind: a project, a plan, a person. Not for wrapping every piece of text.

| Part | Value |
|---|---|
| Padding | `--space-6`. Small `--space-4`, large `--space-8` |
| Radius | `--radius-lg` |
| Edge | One of: `--line` border, or `--surface` on `--bg`. See `../system/elevation.md` |
| Gap between cards | `--grid-gap` |
| Title | `--text-h3`, or 16 to 18px in dense grids |
| Body | `--text-sm` to `--text-base`, `--ink-2` |
| Image | Full width at the top, one aspect ratio across the set |

**Linked card:** the whole card is one link, using one anchor stretched over it. Hover changes the border or background. Only one link inside.

**In a row:** tops and bottoms align. Put buttons at the bottom with `margin-top: auto`.

**One card style per project.** Do not nest cards.

**Phone:** one column. Small cards may sit in two.

**Avoid:** an icon in a tinted square on top of every card. Three identical cards by habit.
