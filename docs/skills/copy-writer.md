# Copy Writer Skill

The copy-writer skill writes every word a web page needs before any design exists. It works from real facts, so nothing on the page is invented.

## What You Need

- Real material: a résumé, notes, a brief, links, or an existing site. If the project has a spec, the skill reads it first and asks only what the spec leaves out.
- **Python 3.9 or later** for the check script.

## Using the Skill

In Claude Code, ask for example `write the copy for my portfolio` and point it at your material. It asks what it still needs in one batch.

It works for eight kinds of page: portfolio, SaaS, app screens, blog or docs, service, shop, local place, and event or waitlist.

## What You Get

`COPY.md` at the project root:

- a fact sheet of what is real, and a `## missing` list of what is not;
- a voice;
- every line of text: headlines, labels, errors, the 404, the title, the description and alt text.

A script checks it for invented facts, placeholders and habits that make text sound machine-written. Figures count as facts only when the spec lists them as results with a source. Targets are never written as things that happened.

## What It Won't Do

- Invent people, quotes, customers, ratings or numbers, or leave placeholders such as "coming soon" (except on a true waitlist page).
- Choose colours, fonts or a mood (use `design-md`), or build the page (use `ui-craft`).
- Tighten an existing document (use `doc-trimmer`) or write a spec (use `spec-writer`).

## Next Step

Approve `COPY.md` (the orchestrator calls this Gate C), then run `design-md`.
