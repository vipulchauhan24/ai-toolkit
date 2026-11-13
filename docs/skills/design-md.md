# DESIGN.md Skill

The design-md skill fixes the look of a web page before anything is built. It reads `COPY.md`, proposes three ideas drawn from your own material, shows each as a real first screen, and records the one you choose.

## What You Need

- `COPY.md` (written by `copy-writer`).
- **Python 3.9 or later**. A browser (Playwright CLI) for the previews. npm for fonts and for linting `DESIGN.md`.
- Optional: brand colours, a logo, screenshots of sites you like. If the project has a spec, its `Look inputs` and `Audience` lines are read first.

## Using the Skill

Ask for example `design the look for my portfolio`. It asks about light or dark, your colours and any references in one batch. Only portfolios and personal sites have a full direction so far.

## What You Get

- `CONCEPTS.md` and three previews to choose from.
- `DESIGN.md` in the Google Stitch format: YAML tokens for light and dark, plus prose.
- `design.json` and `design.css`, checked for contrast and for repeating the same look.

It picks a colour combo that suits your audience, or uses your own colours and shows nearby combos when you want options. A colour that fails contrast is never changed silently: you get the options.

## What It Won't Do

- Write copy (use `copy-writer`) or build the page (use `ui-craft`).
- Invent anything on a preview. Previews use words from `COPY.md` and real images only.

## Next Step

Run `ui-craft` to build the page from `COPY.md` and `DESIGN.md`.
