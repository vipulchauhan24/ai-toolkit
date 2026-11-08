# Toast

**Use for** brief confirmation that something happened. Errors that need action belong next to the problem, not in a toast.

- Bottom right on desktop, bottom centre on phones. Above the phone's safe area.
- `--surface`, `--shadow-2`, `--radius-md`, padding `--space-3` by `--space-4`, `--text-sm`, `--z-toast`.
- Up to 360px wide.
- Stays at least 5 seconds. The timer pauses on hover and focus. A close button is available.
- Offers Undo where it can.
- At most three stacked.

**Behaviour:** an `aria-live="polite"` region, which exists before the message arrives.

**Avoid:** toasts for every action. Critical information that disappears.
