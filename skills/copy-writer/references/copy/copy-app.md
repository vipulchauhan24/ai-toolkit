# Copy for app screens

Inside a product, nobody is being persuaded. Someone is trying to get a job done. The words should help them do it and then disappear.

## Who reads it

A person in the middle of a task, often repeating it, sometimes under pressure. They already know what the product is. They use your labels as a map.

Their questions:

1. Where am I?
2. What can I do here?
3. What will this button do?
4. Did it work?
5. What went wrong, and how do I fix it?

## Fact sheet: ask for these

- The user's real terms for things. Use those, not the database's names.
- Every action on the screen and what it really does, including what cannot be undone.
- The states the screen can be in, and what causes each.
- Limits: file sizes, quotas, formats, permissions.
- What happens to data on delete, cancel or leave.

## What every screen needs written

`check_copy.py` requires at least one `empty:` and one `error:` line for this kind.

| Part | How to write it |
|---|---|
| Page title | The thing the screen is about: "Invoices". No greeting |
| Key figure labels | The noun and its time range: "Revenue, last 30 days" |
| Column headers | One or two words. Units in the header, not in every cell |
| Actions | Verb and object: "Create invoice", "Export CSV". Same verb for the same action everywhere |
| Form labels and hints | See `copy.md` section 10 |
| Empty state | Why it is empty, what will appear, and a button |
| Zero result (filter or search) | Say the filter caused it: "No invoices match 'Paid' this month." Offer "Clear filters" |
| Loading | Name what is happening when it takes more than a moment: "Importing 2,000 rows…" |
| Errors | What went wrong, why if known, what to do. Keep their input |
| Success | What happened. A short toast is enough for small actions |
| Confirmation dialog | See below |
| Permissions | Who can do this, and how to get access |

## Labels

- **Consistency beats variety.** If it is "Archive" on one screen, it is never "Hide" on another.
- **Short, and front-loaded.** Put the distinguishing word first: "Invoices: paid", "Invoices: overdue".
- **Nouns for places, verbs for actions.**
- **Use the reader's terms.** "Teammates", not "Users" if that is how they talk.
- **Plan for length.** Text may be translated or grow. Long names need truncation with the full text available.

## Destructive actions

Name exactly what will happen.

- Title: the question, with the object. "Delete the invoice for Harbor Café?"
- Body: the consequence. "This also removes 3 payments. You can't undo this."
- Buttons: the action, never "Yes" and "No". "Delete invoice" and "Keep invoice".

Offer undo where you can, and then you can skip the dialog.

## Errors in apps

| Situation | Write |
|---|---|
| Their input | Next to the field: "Enter an amount above 0" |
| Connection | "Couldn't save because the connection dropped. Your changes are still here." and "Try again" |
| Permission | "Only admins can change billing. Ask an admin on your team." |
| Our fault | "Something went wrong on our side and your work wasn't saved. Try again in a minute." Give a reference code for support after the message |
| Limit reached | Say the limit, the current use, and the way out |

Never "An error occurred". Never only a code. No jokes.

## Tone

Plain, short, neutral. Almost no voice: voice shows in empty states and the rare moment of success. Do not congratulate people for routine actions.

Write in the second person, or drop the pronoun: "Your invoices" or "Invoices". Avoid mixing "my" and "your" on one screen.

Sentence case everywhere. No full stop on labels or single-sentence hints.

## Numbers

- Right-align and use tabular numerals.
- Be consistent about decimals in a column.
- Show the unit once, and write out the time range.
- Relative dates ("3 hours ago") for recent activity, exact dates for records.
- Use the user's locale, by formatting with `Intl`.

## Checklist

- [ ] Each screen has its empty, loading and error text written.
- [ ] Each button names its action.
- [ ] Destructive dialogs name the object and the consequence.
- [ ] The same action has the same name everywhere.
- [ ] No internal names or database terms visible.
