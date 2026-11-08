# Radius, borders, shadows and layers

## Radius families

`DESIGN.md` picks one family for the whole project.

| Family | `--radius-sm` | `--radius-md` | `--radius-lg` | Suits |
|---|---|---|---|---|
| Sharp | 0 | 2px | 4px | Editorial, finance, serious brands |
| Tight | 4px | 6px | 8px | Developer tools, dense apps |
| Soft | 6px | 8px | 12px | The default for most sites |
| Round | 8px | 12px | 20px | Consumer products, friendly brands |

| Use | Token |
|---|---|
| Badges, checkboxes, small inner parts | `--radius-sm` |
| Buttons, inputs, tooltips | `--radius-md` |
| Cards, modals, images | `--radius-lg` |

A project may set all buttons to `--radius-full` as a choice in `DESIGN.md`, and then uses that everywhere.

A shape inside another shape needs a smaller radius: inner radius equals outer radius minus the padding.

## Separating surfaces

Choose one method per surface:

1. Space alone. Try this first.
2. A change of background.
3. A 1px `--line` border.
4. A shadow.

Never a border and a shadow together on a resting card.

## Shadows

Resting cards rarely need shadows. Shadows are for things that float above the page.

| Token | Used for |
|---|---|
| `--shadow-1` | A raised card, when the design calls for it |
| `--shadow-2` | Dropdowns, popovers |
| `--shadow-3` | Modals |

Shadows are soft and low in opacity, and usually two layers: one tight and one wide. On a dark theme, use a lighter surface or a faint border instead.

## Layers

Use only the `--z-*` tokens. Never type a number.

Order, low to high: nav, dropdown, modal, toast, tooltip.
