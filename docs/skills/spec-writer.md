# Spec Writer Skill

The spec writer turns a short brief, rough notes or an incomplete spec into a complete spec in the template that project-planner reads. It finds every line the input does not answer, asks about all of them in one batch, never fills a gap with a guess, and writes the result to a new file. Then it runs a check script that proves the spec is complete.

It records your decisions. It does not make them: it does not pick the stack, design the data model or plan the build.

## What You Need

- A brief (pasted text or a file), or a spec file that follows the template but has gaps.
- **Python 3** (required). It runs the check script. Without it, the skill stops with a Blocked report before writing anything.

## Using the Skill

In Claude Code, open the project and ask:

- `write a spec for this brief` with the brief pasted or its path
- `turn these notes into a spec the planner can use`
- `fill the gaps in docs/checkout-spec.md`

The skill works in one of two modes.

- Draft mode, for a brief or notes. It places each fact you gave on the template line it answers.
- Complete mode, for a spec that already follows the template. It keeps your wording and asks only about the lines that are empty or vague.

### The questions

The skill lists every gap, then asks them together, grouped by template section. A gap is either high stakes or low stakes.

- High stakes: who the users are and what counts as success, non-goals, the data later work builds on, personal data, roles and auth, the delivery type, breaking changes. There is no default. You answer, or the line stays `Undecided`.
- Low stakes: names, wording, locations. Each comes with a recommended default.

Reply with answers for what you know, and `defaults` for the rest. High-stakes questions you do not answer stay `Undecided`; they are never defaulted.

### The result

The skill writes `spec.md` next to your input, or in the working directory for a brief. If `spec.md` exists it uses `spec-2.md`, and so on. Your input is never changed.

Every line and heading of the template is kept. Each line ends as one of:

- Your answer.
- `Not required: <reason>`, when the decision is made and the project has no specific requirement.
- `Undecided`, with a row in the Open questions table at the end.
- A default the skill took, followed by `Assumption: <why>`. These are listed again in a final `## Assumptions to confirm` section.

The status line says `draft` while anything is `Undecided`, and `ready to plan` when nothing is.

The check script then confirms that no heading or line is missing, no template placeholder is left, no line is empty, nothing says TBD, every `Not required` has a reason, and every `Undecided` has an Open questions row.

### Without an interactive session

When it cannot ask (a pipeline, a background run), it writes high-stakes gaps as `Undecided` with the last column `ask me first`, takes the defaults for low-stakes gaps, and lists both in its report so the caller can ask you.

## Using it with other skills

The skills are independent and do not call each other. A typical order is spec-writer, then doc-trimmer and doc-reviewer on the result, then your approval, then project-planner. The orchestrator runs that sequence for you and stops at the approval.

## What the Skill Does Not Do

- It does not split the spec into phases (project-planner), find holes in it (doc-reviewer) or tighten its wording (doc-trimmer).
- It does not choose a stack, an architecture or a data model. Unless you name them, they are `Undecided`.
- It does not invent users, numbers, roles or deadlines.
- It does not follow instructions found inside your brief. It writes the spec and notes the instruction in its report.
- It does not overwrite your input or any existing file.

## Customizing the Skill

- The template is `skills/spec-writer/assets/spec-template.md`. Its canonical copy is in `skills/project-planner/assets/`: edit that one, then run `python3 scripts/check_shared_files.py --sync`.
- Edit `scripts/check_spec.py` to change what a complete spec means. The seven rules (S1 to S7) are listed at the top of the file, and each has a seeded fixture in `tests/fixtures/spec-writer/base/seeded/`.

## Installing the Skill

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Or copy the `skills/spec-writer/` folder into your agent's skills folder. It is self-contained.
