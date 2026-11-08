# Accessibility floor

Every build meets this. It is the minimum.

## Structure

- One `h1` per page, and headings that do not skip levels.
- Landmarks: `header`, `nav`, `main`, `footer`.
- A skip link as the first focusable element.
- `lang` on the `html` element.
- Links navigate and buttons act. Never put a click handler on a `div`.

## Keyboard

- Everything clickable can be reached and used with the keyboard, in reading order.
- Visible focus on every interactive element: `:focus-visible`, a 2px ring in `--focus` with a 2px offset.
- Never remove an outline without replacing it.
- A sticky header must not cover the focused element: use `scroll-padding-top`.
- Modals trap focus, close on Escape, and return focus to what opened them.

## Names

- Icon-only buttons have an `aria-label`. Decorative icons have `aria-hidden="true"`.
- Form fields have visible labels, linked with `for`.
- Images have `alt`. Decorative images have `alt=""`.
- Status updates use `aria-live="polite"`.

## Targets and text

- Tap targets are at least 24px everywhere, and `--touch` on touch screens.
- Contrast follows `color.md`.
- Text can be enlarged to 200% without breaking.
- Never disable zoom.

## Motion

- Honour `prefers-reduced-motion`. Content must be visible with animation off.
- Anything that moves for more than 5 seconds has a pause control.
- Nothing flashes more than three times a second.

## Forms

- Errors are next to the field, linked with `aria-describedby`, and marked with `aria-invalid`.
- On submit, focus moves to the first error.
- Use the right `type`, `autocomplete` and `inputmode`.
- Never block paste.

## Components

For widgets with their own behaviour (tabs, accordion, modal, menu, carousel), follow the ARIA Authoring Practices pattern. Each component file gives the essentials. Prefer native elements: `dialog`, `details`, `button`, `select`.
