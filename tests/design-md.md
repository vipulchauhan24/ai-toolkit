# design-md

## Should trigger

- "Design the look for my portfolio from COPY.md."
- "Create a DESIGN.md for this site."
- "Pick a palette and fonts for my personal site."
- "Propose three design directions for my portfolio."
- "Use my brand colours as the direction for this site."
- "Write a Stitch-style DESIGN.md for this project."
- "Choose a look before we build the page."
- "Give me design tokens and light and dark colours for my site."
- "Use these screenshots as the design direction."
- "Decide the visual direction for this portfolio."

## Should NOT trigger

- "Write the copy for my site." (copy-writer)
- "Build my portfolio from COPY.md and DESIGN.md." (ui-craft)
- "Build this screen." (ui-developer)
- "Run visual QA." (visual-qa)
- "Trim this blog post." (doc-trimmer)
- "Write a spec for this brief." (spec-writer)
- "Plan this project." (project-planner)
- "Write unit tests for the form."
- "Translate this page into Spanish."
- "Summarise this article."

## Functional

**Direction from COPY.md**
- Given: `COPY.md` for a portfolio and a run that cannot ask questions or open a browser
- When: the skill runs
- Then: it writes `CONCEPTS.md` with three ideas and a recorded choice, three previews and `concept.json`, deals with that concept and a seed, writes a `DESIGN.md` that starts with YAML front matter and has the `## Colors` section before `## Sections`, runs the contrast and sameness checks, and says the lint was not run if npm is missing.

**No COPY.md**
- Given: a project with no `COPY.md`
- When: the skill runs
- Then: it stops, says `copy-writer` writes it, and writes no `DESIGN.md`.
