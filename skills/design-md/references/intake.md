# Intake

Ask once, in one batch, and skip what you already know. Read `COPY.md` first: its `kind:` and `## facts` answer most of this. If the project has a spec (`spec.approved.md`, else `spec.md`), read its `Look inputs` and `Audience` lines too: they answer questions 1 to 3 and the audience word below, so ask only about what they leave out. `Look inputs` that says `none` means the look is open, and you propose it.

Read a `.pdf` (a brand guide, a screenshot export) with the Read tool, which extracts its text or shows its pages. Use `pdftotext` only if the Read tool cannot open it. Never install a package (pip, npm, apt or any other) to read a document: if nothing can read it, ask for the text.

1. Light, dark or both? The default is both.
2. Are there colours to use? If so, should the page use only those, or may it suggest close combos?
3. Is there anything to take direction from: screenshots, an existing site, a logo? See "Inputs" below.

From `COPY.md`, work out the `--has` list for `deal.py`: `numbers`, `images`, `portrait`, `projects`, `experience`, `skills`, `quotes`, `form`.

Only count what is real and may be shown. If there are no real projects, leave out `projects`, and the projects section will not exist.

Count `form` only if `COPY.md` records a real place to send it. Otherwise contact is a direct link.

Name the audience with one of the words the combos use: `hiring`, `technical`, `business`, `consumers`, `local`, `creative` or `community`. Pass it to `deal.py --audience`.

If the user gave colours, write them to `colors.json` at the project root as `system/color.md` describes. If they want suggestions, run `colors.py near colors.json --html previews/colors.html` and show them; a chosen combo goes in the concept as `palette`. If they want their colours only, pass `--colors colors.json` to `deal.py`.

## Inputs

- **Screenshots** of sites or apps the user likes: read palette, type style, density, corner radius and tone from them. Colours read from an image are approximations: say so, round them to clean values, and use flat regions, not photos or gradients. Do not copy layout or branding.
- **Screenshots that disagree** (one light, one dark, two unrelated palettes): name the conflict, propose which signal wins, and do not average them.
- **A logo**: take the dominant brand colours from it into `colors.json`.
- **A URL or Figma link you cannot open**: say so and ask for screenshots or exported colours. Never invent what it looks like.
- **"Make it like this" with a named product**: take tone and structure, and build an original direction. Do not reproduce their palette or branding.
- **A single brand colour or a font name only**: keep it exactly, and let `colors.py` derive the rest. Say which colours were derived.
- **A brand colour that fails contrast as a fill** under a label: never change it silently. Report the pair, offer the nearest passing step of the same hue, and keep the original for logos and decoration.
