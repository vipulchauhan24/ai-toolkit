# Form

**Layout:** one column. Labels above fields. Field gap `--space-5`. Label to field `--space-2`. Field width follows the length of what goes in it.

| Part | Value |
|---|---|
| Input height | `--control-lg` on websites, `--control-md` in apps, `--touch` minimum on touch |
| Input padding | `--space-3` to `--space-4` horizontal |
| Input text | `--text-base` so phones don't zoom |
| Border | 1px `--line-strong` |
| Radius | `--radius-md` |
| Label | `--text-sm`, weight 500 |
| Hint and error | `--text-sm`, directly under the field |
| Textarea | At least 4 rows, resizes vertically |

**Checkbox and radio:** 20px box, label beside it, whole row clickable, at least `--touch` tall on touch.

**Switch:** for an immediate on or off setting. For something that needs saving, use a checkbox.

**Select:** use the native element unless a search is needed.

**States:** focus ring, error (`--negative` border and message), disabled, read-only, submitting.

**Behaviour:** see `../system/accessibility.md`. Validate on leaving a field or on submit, never while typing the first time. Keep the user's input after an error. The submit button stays enabled until submitted. Ask only for what you use.

**Avoid:** floating labels. Placeholder as the label. Red text with no words. Asking for a phone number you won't call.
