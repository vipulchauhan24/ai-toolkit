# Intake

Ask once, in one batch, and skip what you already know.

Read the project's spec first (`spec.approved.md`, else `spec.md`) if there is one. Its Interfaces section answers questions 1, 2 and 4 below (`Page kind`, `The one action each page leads to`, and the stack under Technology and constraints), and `Audience` tells you who reads the page. Its `Content that does not exist yet` line goes straight into `## missing`. Ask only what the spec leaves out.

A figure from the spec is a fact only when it is listed under `Figures that are results, not targets`, with its source. Success criteria and quality-bar numbers are targets: never copy one into `## facts`, and never write it on the page as something that happened.

Read a `.pdf` with the Read tool, which extracts its text (use its `pages` option for a long file). Use `pdftotext` only if the Read tool cannot open it. Never install a package (pip, npm, apt or any other) to read a document: if nothing can read it, ask for the text.

1. What kind of page is this?
2. Who needs to do what after reading it? This is the one action.
3. What real material exists? Use the fact-sheet list in the kind's copy file, and also ask for images, a portrait, logos and links.
4. Does the project have a stack already, or is it new?

Only count what is real and may be shown. List what's missing in `## missing` in `COPY.md`.

Say a contact form exists only if there's a real place to send it. Otherwise contact is a direct link.

Design questions (light or dark, colours, mood) belong to the `design-md` skill. If the user raises them, note them under `## missing` and move on.
