# States

A screen that only works with perfect data is half built. Take the words for each state from `COPY.md`. If one is missing, list it as missing.

## Interactive states

| State | Treatment |
|---|---|
| Rest | The default |
| Hover | A small, clear change in background or border. Only on devices that can hover |
| Focus | The ring from `accessibility.md`. Always visible on keyboard use |
| Active, pressed | Slightly darker, or scaled down a little |
| Selected | A change that is more than colour: a fill, a weight, a mark |
| Disabled | Lower contrast, no pointer, and say why if it isn't obvious. Prefer leaving controls enabled and explaining the problem on use |
| Loading | Keep the size. Replace the label with a spinner, or keep the label and add one |

## Data states

| State | How to build it |
|---|---|
| Loading | The final layout with grey bars at the real sizes. Headers and labels appear at once. The layout must not jump when data arrives |
| Empty, first use | Keep the frame. Say what will appear, and give the first action in the place where the data will be |
| Empty, no results | Say the filter or search caused it, and offer a way to clear it |
| Partial | Show what loaded, and mark what didn't |
| Error | Inside the block that failed, with what happened, and Try again. Keep what is already on screen |
| Stale | Show when it was last updated |
| Success | Short confirmation that says what changed |
| Offline | Say so, and keep what the user typed |

## Values

- A real zero prints as a zero.
- When there is no value, show a grey dash.
- Very long values are truncated, with the full text available on hover and to screen readers.
- Plan for the shortest, typical and longest real content.

Do not show an empty message while data is loading.
