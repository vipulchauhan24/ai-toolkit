# ui-craft Skill

The ui-craft skill builds a web page from a finished `COPY.md` and `DESIGN.md`. It composes the page from a kit of tested HTML, CSS and JS with subtle motion, and builds one section, the signature, from scratch.

## What You Need

- `COPY.md` (from `copy-writer`) and `DESIGN.md`, `design.json`, `design.css` (from `design-md`). Without them the skill stops and says which skill writes them.
- **Python 3.9 or later**. A browser for the live review.

## Using the Skill

Ask for example `build my portfolio from COPY.md and DESIGN.md`. The output can be static HTML, React or Next.js. For a new Next.js app, a script applies the kit on top of `create-next-app`: it copies the CSS, wires the theme, motion helpers and fonts, and can write the layout.

In a planned project the orchestrator runs it as a phase build: it builds only the sections the phase names and never chooses the look again. If it finds a difference between the phase document and `DESIGN.md`, `DESIGN.md` wins and the difference is listed.

## What You Get

The built page, checked by scripts for invented facts, contrast and repeated looks, plus a live review against the guidelines and a short report.

## What It Won't Do

- Write copy, choose the look, or leave placeholders.
- Build app screens or product UI beyond the kit (use `frontend-react`), or grade a finished site in a browser (use `visual-qa`).

## Next Step

Run `visual-qa` on the result.
