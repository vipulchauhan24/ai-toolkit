# Tabs

**Use for** switching between views of the same thing, where only one is needed at a time. Two to six tabs.

- Underline style: `--control-md` tall, `--text-sm`, weight 500, sitting on a 1px `--line` rule. The selected tab has a 2px indicator and `--ink` text.
- Segmented style: for two to four short options, in a `--surface-2` track, as wide as its options.

**Behaviour:** `tablist`, `tab` and `tabpanel` roles. Arrow keys move between tabs. Panels keep their state. If a tab changes what is shown on the page, reflect it in the URL.

**Phone:** the tab row scrolls sideways inside itself. Keep the selected tab visible.

**Avoid:** timed auto-switching. Hiding information that people need to compare. Tabs for navigating between pages.
