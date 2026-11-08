# App screens

For screens people work in: dashboards, tables, settings, inboxes, detail pages. Marketing rules do not apply here. There is no hero and no scroll animation.

## Start with the data and the job

Before layout, write down:

1. The objects on the screen, their fields and realistic amounts, including a new account with very little.
2. Who uses it, and how often.
3. The one question the screen answers first, such as "Which deploy failed?"
4. The most frequent next action.

Give the answer to that question the most visual weight. The most frequent action is one click away. Any block that answers no question goes.

Use believable sample data from one file, and compute totals from the rows so that numbers on the screen agree.

## The shell

| Part | Size |
|---|---|
| Sidebar, labelled | 224 to 240px |
| Sidebar, icon rail | 56px, with tooltips and names on each icon |
| Sidebar row | `--control-sm` to `--control-md` tall, icon 16px, `--text-sm` |
| Top bar, if there is one | 48 to 64px. It must hold something real: search, a switcher, the object's name |
| Content padding | `--space-6` to `--space-10` |
| Content width | Fluid up to about 1200 to 1300px. Forms and settings narrower |

- The sidebar matches the page background or sits one step away from it.
- The active item is a neutral fill or a change in text colour.
- Show the product's name and the current workspace.
- Use a sidebar when there are many destinations. With few, use a top bar over a centred column.

## Page title row

The title is a noun at `--text-h3`, weight 600. Greetings are for personal home screens only. An optional line under it gives the period or the finding. Actions sit on the right, with at most one filled primary.

## Key figures

- Prefer one container split by 1px dividers, or put each figure in the card that explains it.
- Value about 24 to 32px, label `--text-sm` in `--ink-2`, label above value.
- No icon in a coloured circle.
- A change shows its period in words: "vs last 30 days".
- Colour means good or bad, which is not the same as up or down. A rise in errors is bad.
- A zero change is grey. From a base of zero, say "new".

## Tables and lists

See `../components/table.md`. Rows are about 44px, or 64 to 72px with two lines. Numbers are right-aligned in tabular figures. No stripes and no header band.

## Forms and settings

- One column, labels above fields.
- Group settings by area, with each area on its own view.
- A section is a title and description on the left, with controls on the right. On phones they stack.
- One way of saving per view: everything saves itself, or one Save per group.
- Destructive actions go last, on their own, and name the consequence.

## Grid

- One gap value both ways.
- Cards in a row share the same top and bottom edges. Balance their content. A stretched card must not contain a blank band.
- A narrow table does not span the full width. Pair it with something.
- Choose columns from the number of items, so there are no orphan cells.

## Type and colour

- One font family is usually enough. A second has a single job, such as mono for IDs.
- Sizes: title 20 to 24, card title 16, body and cells 14, meta 12.
- Colour on data, status and the main action only. Around 95% of the screen is neutral.
- Borders or tone steps separate surfaces. Shadows are for what floats.

## Motion

Feedback only: press, hover, focus, menus and dialogs opening, a new row arriving. No entrance animation on load.

## Phone

- The sidebar becomes a top bar with a menu, or, for four or five destinations, a bar along the bottom.
- Tables become two-line rows below 640px, moving fields to the second line. Nothing is dropped.
- Key figures become two columns or a list.
- Filters fold into a sheet, or a single line of chips. The first row of data stays high on the screen.
- A list and its detail become two views, with back returning to the same scroll position.

## Avoid

"Welcome back" with a wave. Four identical stat cards with green percentages. Gradient charts by default. Zebra rows under uppercase headers. Buttons with gradients or glow. Pagination under a five-row list.
