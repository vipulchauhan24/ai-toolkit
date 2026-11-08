# Modal

**Use for** a short task or decision that must be finished before going on. Otherwise use a separate page or an inline section.

- Width 480px for confirmations, up to 640px for forms.
- Padding `--space-6`, or `--space-8` from 768px.
- Radius `--radius-lg`, `--shadow-3`, `--z-modal`.
- Backdrop: dark, about 50%. Clicking it closes the modal, unless there is unsaved input.
- Title `--text-h3`. Actions at the bottom right: primary last, named by what they do.
- Scrolls inside when the content is tall.

**Behaviour:** use the native `dialog`. Focus goes inside, stays inside, Escape closes it, and focus returns to what opened it. The page behind does not scroll.

**Phone:** full width, as a sheet from the bottom. Controls stay reachable.

**Avoid:** modals on page load. A modal opened from a modal. "Yes" and "No" as button labels.
