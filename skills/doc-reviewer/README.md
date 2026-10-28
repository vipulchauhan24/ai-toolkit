# Doc Reviewer Skill

The doc reviewer skill is an adversarial reader. It takes a design doc, spec, plan, proposal, blog post, or technical writeup and looks for holes: failure modes the author did not consider, assumptions they did not state, steps they skipped, and questions the reader is left holding.

It finds holes. It does not praise, balance, or propose fixes. Each finding ends with one question the author must be able to answer.

## What Is in This Folder

Paths are relative to the skill folder, `skills/doc-reviewer/`, inside the ai-toolkit plugin.

| Path        | Purpose                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------- |
| `SKILL.md`  | The skill itself. Defines the hole categories, the attack method, severity tiers, and output. |
| `README.md` | This file.                                                                                    |

## What It Does

- Classifies the document first (design doc, blog post, PRD, and so on) and picks the categories that fit.
- Hunts two kinds of hole: holes in the design (the system breaks) and holes in the understanding (the reader cannot follow or is left with a wrong model).
- Walks the data and control paths end to end, then walks the argument end to end.
- Quotes the exact text of each hole, or says what is missing when the hole is an omission.
- Labels each hole `fatal`, `serious`, or `sleeper` by impact and sorts the output by severity.
- Reports what it attacked and what it did not.

## Using the Skill

### Step 1: Give It Input

Give the skill one of these:

- Pasted text in your message.
- A file path, such as `docs/design.md`.
- A URL, such as `https://example.com/blog/post`.
- A description of an idea in chat. The skill treats your message as the document.

### Step 2: Ask for the Review

In Claude Code, any of these phrases triggers the skill:

- `poke holes in this`
- `what could go wrong with this design`
- `what is missing from this spec`
- `attack this doc`
- `find the gaps`

You can also call it directly with `/ai-toolkit:doc-reviewer`.

### Step 3: Read the Result

The response contains:

- A one-line status message starting with "Reviewer is...".
- A `Source:` line for file and URL input.
- A `Reviewing as:` line naming the document type and audience the skill assumed, so you can correct a misread.
- The findings, most severe first. Each has a severity, an attack line, a quote, a short explanation, and an `Answer this:` question.
- A `Coverage:` line listing which sections were attacked and which were not.
- A tally of the holes found.
- `Review done.`

### Examples

```text
poke holes in docs/design.md
```

```text
what could go wrong with this spec: <pasted text>
```

```text
attack https://example.com/blog/post
```

```text
review docs/design.md, only the security and abuse angles
```

## Severity

| Tier      | Meaning                                                                                                                         |
| --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `fatal`   | Data loss, a change that cannot be rolled back, a design that does not work, or a reader left with an empty or wrong model.     |
| `serious` | Breaks when a plausible event happens, or the reader hits an obvious question the piece never answers.                          |
| `sleeper` | Will not break at launch but will hurt later: cost after growth, manual steps that drift, missing observability, unstated caveats. |

When a hole fits two tiers, the higher one applies.

## Your Controls

- **Scope**: "only security", "just section 3", "only understanding gaps". The skill reviews only that and says what it left out.
- **Fixes**: ask for fixes after the findings and the skill answers. They are never mixed into the findings.
- **Balance**: ask what is strong and the skill adds it as a separate note after the findings.
- **Revised docs**: bring back a new version and the skill checks which earlier holes are still open, then looks for new ones. It does not repeat holes you marked known or out of scope.

## What It Does Not Do

- It does not review code or diffs. Use `code-review`.
- It does not tighten or restyle writing. Use `doc-trimmer`.
- It does not summarise, translate, or rewrite.
- It cannot read `.docx`, `.pptx`, or links that need a login (Google Docs, Notion). It asks for an export or pasted text.
- It does not follow instructions written inside the reviewed document. Text addressed to the reviewer is ignored and reported as a defect.
- It does not invent capacity numbers. When the doc gives no baseline, the missing baseline is the finding.

## Example

Input:

```text
On checkout, the order service writes the order to MySQL and then publishes an OrderCreated event to Kafka for the downstream fulfilment and email services.
```

Output:

```text
Reviewer is hunting for what breaks first.

Reviewing as: design doc for engineers

**fatal** partial failure

> "the order service writes the order to MySQL and then publishes an OrderCreated event to Kafka"

This is a dual write with no transactional boundary. When the MySQL commit succeeds and the Kafka publish fails, the order exists but fulfilment and email never hear about it. The customer paid and nothing ships. Nothing in the doc detects or repairs this divergence.

Answer this: when the write succeeds and the publish fails, what notices, and how does the event get delivered?

Coverage: attacked the whole text; not reviewed none
Reviewer found 1 hole: 1 fatal.

Review done.
```

## Customising

- Edit `SKILL.md` to add hole categories, change the severity tiers, or change the output format.
- Drop the status line and `Review done.` by editing the Output Structure section if you want plain output.

## Installing

The skill ships in the ai-toolkit plugin. From the repository root:

```text
claude plugin marketplace add vipulchauhan24/ai-toolkit
claude plugin install ai-toolkit@product-development
/reload-plugins
```

To use it as a standalone skill, copy the `doc-reviewer/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.
