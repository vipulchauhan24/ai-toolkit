# Responsive behaviour

Write mobile first. Use these breakpoints, with `min-width` queries:

| Name | Width | Typical device |
|---|---|---|
| base | 0 | Phone |
| `sm` | 640px | Large phone |
| `md` | 768px | Tablet, upright |
| `lg` | 1024px | Tablet on its side, small laptop |
| `xl` | 1280px | Laptop |
| `2xl` | 1536px | Large desktop |

Every page is checked at 390, 768, 1024, 1440 and 1920.

## The phone is its own layout

- One column, unless items are small and paired, such as stats in two columns.
- Rewrite line breaks and re-crop images. Portrait crops usually work better.
- Reorder so that the main message comes first. Text comes before its image, unless the image is the message.
- Main buttons may go full width.
- Tap targets are at least `--touch`, with `--space-2` between them.
- Body text stays at 16px or above, so phones don't zoom into fields.
- No sideways scrolling on the page. A wide table or code block scrolls inside its own frame.

## Tablet

Do not simply stretch the phone layout. Two columns usually work at 768px. Cards of three across become two, with a lone last card spanning the row or the set reduced.

## Large screens

The container stops growing at `--container`. Margins grow. Wide images may run to `--container-wide`. Text never gets wider than its `--prose` or container.

## Technique

- Fluid type and spacing tokens handle most changes, so there are few media queries.
- Use container queries for components that appear at different widths.
- Use `min-width: 0` on flex and grid children that hold long text.
- Use `dvh` units for full-height sections on phones.
- Respect safe areas with `env(safe-area-inset-*)` for anything fixed to an edge.
- Detect touch with `@media (pointer: coarse)`, never by width.
- Hover effects go inside `@media (hover: hover)`.
- Set `width` and `height` on images, and use `srcset` for large ones.
