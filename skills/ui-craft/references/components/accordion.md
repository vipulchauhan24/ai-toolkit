# Accordion

**Use for** independent items where people need only a few: FAQs, optional details. Not for content people must read in sequence or compare.

- Row: at least `--control-lg` tall, `--space-4` vertical padding, `--text-base` to `--text-lead`, weight 500.
- A 1px `--line` between items.
- Chevron or plus on the right, 20px.
- The whole header is clickable.
- Panel text `--ink-2`, with `--space-4` below.

**Behaviour:** use `details` and `summary`, or a `button` inside a heading with `aria-expanded`. Several items may be open at once. Do not auto-close others. Collapsed content is hidden from keyboard and screen readers. Open everything for printing. Write headings that say what's inside.

**Avoid:** essential information inside collapsed panels. Accordions for very short content.
