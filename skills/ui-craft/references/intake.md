# Intake

Ask once, in one batch, and skip what you already know.

Read a `.pdf` with the Read tool, which extracts its text (use its `pages` option for a long file). Use `pdftotext` only if the Read tool cannot open it. Never install a package (pip, npm, apt or any other) to read a document: if nothing can read it, ask for the text.

1. What kind of page is this?
2. Who needs to do what after reading it? This is the one action.
3. What real material exists? Use the fact-sheet list in the kind's copy file, and also ask for images, a portrait, logos and links.
4. Does the project have a stack already, or is it new?
5. Light, dark or both? The default is both.
6. Are there colours to use? If so, should the page use only those, or may it suggest close combos?

From the answers, work out the `--has` list for `deal.py`: `numbers`, `images`, `portrait`, `projects`, `experience`, `skills`, `quotes`, `form`.

Only count what is real and may be shown. If there are no real projects, leave out `projects`, and the projects section will not exist. List what's missing in `## missing` in `COPY.md`.

Say `form` only if there's a real place to send it. Otherwise contact is a direct link.

Name the audience with one of the words the combos use: `hiring`, `technical`, `business`, `consumers`, `local`, `creative` or `community`. Pass it to `deal.py --audience`.

If the user gave colours, write them to `colors.json` at the project root as `system/color.md` describes. If they want suggestions, run `colors.py near colors.json --html previews/colors.html` and show them; a chosen combo goes in the concept as `palette`. If they want their colours only, pass `--colors colors.json` to `deal.py`.
