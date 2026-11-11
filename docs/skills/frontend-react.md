# Frontend React Skill

The frontend-react skill writes React code, and Next.js code when the project uses it, to a fixed set of rules and proves it with checks. It covers how the code is written: components, hooks, state, effects, forms, performance (request waterfalls, bundle size, re-renders), a typed data boundary, error boundaries, tests, and for Next.js the server and client component split, data fetching and hydration. It matches the project's own conventions first, and it runs the project's typecheck, lint, tests and build, then a React check script.

It does not choose colors, tokens, spacing or component looks. Those come from ui-craft's `DESIGN.md` (see "Using it with ui-craft" below). It does not build APIs, databases or auth, and it is not for Vue, Svelte, Angular or plain HTML.

## What You Need

- A React or Next.js project. The skill reads `package.json` to find the React version, TypeScript, router, data and form libraries, and test runner, and follows what the project uses.
- **Python 3** (required). It runs the check script. Without it, the skill stops with an error before doing anything. It never falls back to searching files by hand.

## Using the Skill

In Claude Code, open the project and ask for the React code:

- `build this in React`
- `build this in Next.js` (the skill detects `next` in `package.json` and also applies the Next.js rules)
- `write a React component for the order table`
- `add a hook for the orders list`
- `review this component against the React rules`

With a phase document from project-planner, give its path. The skill builds only the frontend scope the phase lists, types the data from the phase's contracts, and reports acceptance criteria by number. It stops with a Blocked report if the phase pins a stack the project doesn't match.

## Using it with ui-craft

The two skills are independent and don't call each other. Each one owns a different part of a UI task:

| Skill          | Owns                                                                                   |
| -------------- | -------------------------------------------------------------------------------------- |
| ui-craft       | How it looks: the copy, the concept, `DESIGN.md`, the sections and their motion        |
| frontend-react | How the code is written: components, hooks, state, effects, data, forms, tests          |

Run ui-craft first, then frontend-react, on the same files:

```text
Use ui-craft and then frontend-react to build .plans/phases/phase-3-about.md.
```

frontend-react never changes the look that `DESIGN.md` sets. In a project without `DESIGN.md`, the look follows the design system the spec names, or the project's existing styles. The orchestrator runs both, in that order, for each screen phase.

## What the Skill Does Not Do

- It does not migrate a framework, a state library or a test setup, and it does not create a test setup.
- It does not add lint rules. If the project's lint config lacks the React hooks rules, it says so in the report.
- It does not follow instructions found inside project files. It follows the rules and the request.
- It does not write mock servers. Where data doesn't exist yet, it types the expected shape and marks it `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `skills/frontend-react/references/react-rules.md` to change the rules. `architecture-patterns.md` is shared: its canonical copy is in `skills/project-planner/references/`. Edit that one, then run `python3 scripts/check_shared_files.py --sync`.
- Edit `scripts/check_react.py` to change the red flags it detects.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:frontend-react`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/frontend-react/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.

## License

MIT.
