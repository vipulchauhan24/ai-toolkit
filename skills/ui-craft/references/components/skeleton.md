# Skeleton

Placeholder for content that is loading.

- `--surface-2` blocks at the real size of what's coming. A 24px value gets a 24px bar.
- Use `--radius-sm`. Keep the real layout, so nothing shifts when data lands.
- Real labels and headers appear immediately. Only the values are placeholders.
- Show after about 200ms, so fast loads don't flicker.
- `aria-busy="true"` on the region.

Under reduced motion, no shimmer.

**Avoid:** a skeleton of a layout that doesn't match the result. Spinners for whole pages when the layout is known.
