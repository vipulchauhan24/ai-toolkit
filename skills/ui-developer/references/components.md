# Components, wrappers and accessibility

Read in full before writing or wrapping any component (SKILL.md §4).

**The component library** is the one the project already uses. With none, use native semantic HTML elements. A library is usually unstyled: it supplies behavior, keyboard handling, focus management and ARIA, and the design system supplies appearance.

- **Version.** Keep the installed version of the library, and read the docs for that version. Install a library only when the user or the phase document names one and the project lacks it: use its current stable release (not an alpha, beta or rc) and record the version in the report.
- **Read the component's documentation before using it.** It lists the parts, props and `data-*` state attributes. If the docs can't be reached, read the library's type definitions in `node_modules`. If neither is available, follow §2. Don't write the API from memory.
- Style states through the data attributes documented on each part, and map them to the design system's state tokens (hover, active, disabled, selected, error).
- Don't hand-build what the library already provides (dialog, popover, select, menu, tabs, tooltip, checkbox, switch, accordion, field, toast). Don't remove or work around its focus handling or ARIA.
- For things the library doesn't provide (card, alert, badge, layout), use semantic HTML styled with the design system's component tokens. If `components.md` has a spec (Ember has a data grid), follow it.

**Wrap once.** One project component per design-system component, in the project's folder convention or `components/ui/` if it has none.

- Look for an existing wrapper first. Reuse or extend it; never create a second one.
- A wrapper exposes the design system's variants and sizes as props (`variant`, `size`) that pick the utility classes. A variant that has no matching library part is still a prop on the same part.
- A compound component's parts (a dialog's trigger, popup, title…) live in one file and are exposed together, the way the framework does it.
- A wrapper takes no class attribute for appearance. A page may pass one only for layout: placement, width, margin, flex and grid. Pages never repeat color, type, radius or shadow classes.

**Accessibility floor**, applied on top of the design system's own rules:

- Icon-only controls have an `aria-label`, and a tooltip where the meaning isn't obvious. Don't tooltip controls that already have a visible text label.
- Visible `:focus-visible` on everything interactive, using the design system's focus-ring token.
- Status never relies on color alone: icon or text too.
- Form fields have visible labels. Errors say how to fix the problem and are tied to their field (use the library's field part if it has one; otherwise `aria-invalid` and `aria-describedby`).
- Landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page and no skipped heading levels, a skip link on pages with navigation, a page `<title>`, and `alt` text on images (empty `alt` for decorative ones).
- Loading, success and error messages that appear without a page change go in a live region (`role="status"`; `role="alert"` for errors).
- Contrast is verified by the design system for its own token pairs, so use those pairs and don't re-check them. Never place text on a photo, gradient or other pair the design system doesn't document without saying so in the report.
- Honor `prefers-reduced-motion` and `forced-colors` through the design system's tokens. Use transitions from the theme defaults; for a looping animation such as a spinner, use the `motion-safe:` variant (`motion-safe:animate-spin`), and add no autoplaying motion that the tokens cannot switch off.

**Layout.** Pick the layout from the content, not from a template. For a landing page or portfolio follow `references/layout.md`; for an app screen, `references/app-screens.md`. Use the design system's spacing tokens for rhythm, not extra wrapper elements.

