# Button

**Use for** actions. If it goes to another page, use a link, styled as a button if it's the main action.

| Size | Height | Padding | Text | Use |
|---|---|---|---|---|
| Small | `--control-sm` | `--space-3` | `--text-sm` | Toolbars, table rows |
| Medium | `--control-md` | `--space-4` | `--text-sm` | Default in apps and nav |
| Large | `--control-lg` | `--space-6` | `--text-base` | Heroes and main actions |

On touch screens every button is at least `--touch` tall. Icon gap is `--space-2`, and icons are 16 to 20px.

| Variant | Look | Use |
|---|---|---|
| Primary | `--accent` with `--on-accent` | The one main action per screen |
| Secondary | `--surface` or transparent, `--line-strong` border | Other actions |
| Ghost | Text only, `--surface-2` on hover | Low emphasis, toolbars |
| Danger | `--negative` | Destructive actions |

Radius is `--radius-md`, or `--radius-full` if `DESIGN.md` says so. Weight 500.

**States:** all from `../system/states.md`. A loading button keeps its width.

**Phone:** main buttons may go full width.

**Avoid:** more than one primary on a screen. Arrows on every button. Gradients, glows. Text under `--text-sm`.
