# Table

**Use for** data people compare across rows.

| Part | Value |
|---|---|
| Row height | About 44px. With two lines, 64 to 72px |
| Cell padding | `--space-3` by `--space-4` |
| Header | `--text-xs` to `--text-sm`, `--ink-2`, sentence case, 1px `--line` under it |
| Row divider | 1px `--line`, or none with enough space |
| Text | `--text-sm` |
| Numbers | Right-aligned, tabular figures, fixed decimals per column |

- The first column names the row, and gets the most width.
- Only the name and the key number use `--ink`. The rest use `--ink-2`.
- Show a grey dash when there is no value.
- Long text stays on one line and ends in an ellipsis, with the full text available.
- A status appears once per row.
- Sticky header on long tables.
- Selection only if bulk actions exist.

**Use real table markup:** `table`, `th` with `scope`, `caption`.

**Phone:** below 640px, turn rows into two-line items, with fields moved to the second line. If it must stay a table, it scrolls inside its own frame with the first column fixed.

**Avoid:** stripes. Filled header bands. Uppercase headers. Left-aligned numbers. Pagination on a short list.
