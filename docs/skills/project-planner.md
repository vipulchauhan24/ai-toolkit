# Project Planner Skill

The project planner skill turns one product and engineering spec into an ordered set of phases. Each phase is a working, demoable slice with its own design document. You then hand the phase documents to a coding agent one at a time.

## How the Skill Works

1. You write a spec using `assets/spec-template.md` from the skill folder (`skills/project-planner/`).
2. You ask Claude to plan the project and give it the spec.
3. The planner reads your codebase (if there is one) and the phase-writing rules in `references/project-planner-rules.md`.
4. The planner asks you about high-stakes decisions, such as the tech stack, shared data model, auth, and breaking changes.
5. The planner writes an overview and one design document per phase.
6. You give each phase document to a coding agent and review the PR it produces.

## Using the Skill

### Step 1: Write the Spec

Copy `skills/project-planner/assets/spec-template.md`, replace its content with your own, and save it next to your project. A good spec states the goal, a measurable outcome, the requirements, and the non-goals.

The more the spec says about the project type, users, stack constraints, and external services, the fewer questions the planner needs to ask.

### Step 2: Start the Planner

In Claude Code, open the project folder and ask for a plan. Any of these phrases triggers the skill:

- `plan this project`
- `phase this spec`
- `split this into milestones for an agent to build`

Give the path to your spec. For example:

```text
plan this project using docs/checkout-spec.md
```

To get files on disk instead of an inline answer, say so in the request:

```text
plan this project using docs/checkout-spec.md and write the phase files
```

### Step 3: Answer the Questions

The planner stops and asks when a decision is hard to reverse. Examples are the tech stack, the shape of data that later phases build on, auth and security, and breaking API changes. Each question names the options and gives a recommendation. Small decisions it makes itself and records as assumptions at the top of the affected phase document.

### Step 4: Review the Plan

If you asked for files, the planner writes them next to your spec:

```text
docs/
  checkout-spec.md
  phases/
    README.md
    phase-1-<slug>.md
    phase-2-<slug>.md
```

Open `phases/README.md` first. It holds:

- a summary of each phase
- a dependency diagram and the reason for the order
- a parallelization note, if any phases can run side by side

Check that the order makes sense and that each phase ends in something you can demo. Ask the planner to change the plan before you start building.

### Step 5: Build Phase by Phase

Give one phase document to a coding agent in a fresh Claude Code session. Each document is self-contained, so the agent needs only that file and the code from earlier phases.

For each phase:

1. Complete the manual prerequisites listed in the document (accounts, API keys, secrets, DNS). The agent cannot do these.
2. Start a session and point it at the phase document.
3. Let the agent implement it and open one PR.
4. Review the PR against the phase's acceptance criteria and definition of done.
5. Merge before starting any phase that depends on it.

### Step 6: Run Phases in Parallel (Optional)

If the parallelization note lists lanes, you can run each lane in its own git worktree with its own Claude Code session. The plan names the shared files that more than one lane touches. It also names who changes them first and which lane merges first. Follow that merge order, and have the later lanes update from the main branch before they merge.

## What the Plan Looks Like

Phase 1 is a local walking skeleton. It connects every part of the system for one trivial flow and runs with one command.

A delivery phase follows, shaped to the project type:

- Deployed project: a deployment phase with a live URL and CI/CD.
- Library, SDK, CLI, or plugin: a packaging and release phase that installs from the published artifact.
- Internal script or local-only tool: no delivery phase.

Every later phase adds one capability on top of a working system. Each phase document covers:

- the phase goal, scope, and numbered acceptance criteria
- what already exists in the code that the phase reuses
- the data model, API contracts, and key flows
- manual prerequisites
- failure modes, test plan, rollout and rollback
- a definition of done that matches the acceptance criteria

## Customizing the Skill

- Edit `skills/project-planner/references/project-planner-rules.md` to match your own engineering conventions. Treat the current content as starter defaults.
- Edit `skills/project-planner/references/markdown-rules.md` to change how the output is formatted. doc-trimmer keeps an identical copy, and `architecture-patterns.md` has one in frontend-react: run `python3 scripts/check_shared_files.py` after editing and copy the change over.
- Edit `SKILL.md` to change how phases are cut, sized, and documented.

## Installing the Skill

### From the plugin marketplace

In Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:project-planner`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/project-planner/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.
