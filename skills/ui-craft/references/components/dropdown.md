# Dropdown

A menu of actions, or a popover of options, opened from a button.

- Min width 180px, padding `--space-1`, `--radius-md`, `--shadow-2`, `--z-dropdown`.
- Items `--control-sm` to `--control-md` tall, `--text-sm`, `--surface-2` on hover. On touch, `--touch` tall.
- Group with a 1px `--line` divider. Destructive item last, in `--negative`.
- Stays in the window: flips if there's no room.

**Behaviour:** the trigger has `aria-expanded`. Arrow keys move through items. Escape closes and returns focus. Clicking outside closes.

For choosing a form value, use a native select first.

**Avoid:** hover-only menus. Nested menus on a website.
