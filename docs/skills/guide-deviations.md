# Deliberate deviations from the skills guide (maintainers)

This page is for people who edit the toolkit. No skill loads it.

| Deviation | Where | Why |
|---|---|---|
| `model:` in front matter | Every `SKILL.md` | It is outside the guide's list of fields. We keep it so the orchestrator can read which model a skill needs (`sonnet` or `opus`) when it routes a phase |
| Descriptions name skills that are not in this plugin | backend-node, backend-python, julia (`api-builder`, database skills), doc-reviewer and visual-qa (`code-review`) | `api-builder` and the database skills are planned. `code-review` is built into Claude Code. `tests/run.py` lists them in `NOT_INSTALLED_OK` |
| Several skills carry the same file | `scripts/shared_files.json` | Each skill folder must work on its own, so shared files are copied and a test keeps the copies equal |
| `doc-trimmer` `SKILL.md` close to the word limit | 4,993 of 5,000 words | Cut before adding to it, or move a section to `references/` |
