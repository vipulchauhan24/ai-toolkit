# ui-craft

## Should trigger

- "Build my portfolio from COPY.md and DESIGN.md."
- "Build the site from the copy and design direction."
- "Make my personal site, the copy and the look are done."
- "Build this phase: the experience section."
- "Turn COPY.md and DESIGN.md into a page."
- "Build the portfolio as a static site."
- "Build my portfolio in Next.js from the design direction."
- "Compose the page from the kit."
- "Build the hero and the signature section."
- "Make this page pop, using DESIGN.md."

## Should NOT trigger

- "Write the copy for my site." (copy-writer)
- "Pick a palette and fonts." (design-md)
- "Build this screen." (frontend-react)
- "Build this dashboard." (ui-developer)
- "Trim this blog post." (doc-trimmer)
- "Write a spec for this brief." (spec-writer)
- "Run visual QA." (visual-qa)
- "Plan this project." (project-planner)
- "Write a press release."
- "Summarise this article."

## Functional

**Portfolio from a résumé**
- Given: `resume.md` and a run that cannot ask questions
- When: the skill runs
- Then: it reads the general and portfolio rules and the human-writing file, writes `COPY.md` with `kind: portfolio`, a fact sheet and a list of what is missing, leaves out a projects section because there are no projects, runs the check script, and leaves `resume.md` unchanged.

**Missing direction**
- Given: a project with `COPY.md` and no `DESIGN.md`
- When: the skill runs
- Then: it stops, says `design-md` writes the direction, and writes no page.

**Phase build**
- Given: `COPY.md`, `DESIGN.md`, a page with a hero and a contact section, and a phase document that adds an Experience section and asks for a magenta background
- When: the skill builds the phase
- Then: the Experience section appears between the hero and contact with the words from `COPY.md`, nothing else on the page or in `DESIGN.md` changes, no concept step runs, the magenta is not used, and the reply names the difference.
