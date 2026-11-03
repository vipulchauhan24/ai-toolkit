# Frontend React Skill

The frontend-react skill writes React code, and Next.js code when the project uses it, to a fixed set of rules and proves it with checks. It covers how the code is written: components, hooks, state, effects, forms, performance (request waterfalls, bundle size, re-renders), a typed data boundary, error boundaries, tests, and for Next.js the server and client component split, data fetching and hydration. It matches the project's own conventions first, and it runs the project's typecheck, lint, tests and build, then a React check script.

It does not choose colors, tokens, spacing or component looks. Use ui-developer for that (see "Using it with ui-developer" below). It does not build APIs, databases or auth, and it is not for Vue, Svelte, Angular or plain HTML.

## What Is in This Folder

Paths are relative to the skill folder, `skills/frontend-react/`. The skill also reads rules files from `rules/coding/` at the plugin root, two levels up.

| Path                              | Purpose                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                        | The skill itself. Defines the inputs, the build steps, the blockers, the checks and the report.                   |
| `README.md`                       | This file.                                                                                                        |
| `scripts/check_react.py`          | The check the skill runs before delivering. Finds `any`, class components, index keys, effects with no dependency array and other red flags. |
| `../../rules/coding/react-rules.md` | The React rules: components, props and TypeScript, state, effects, data, forms, keys, performance, errors, tests, files. |
| `../../rules/coding/nextjs-rules.md` | The Next.js rules, read only when the project depends on `next`: server and client components, data fetching, the server-client boundary, mutations, hydration, files. |
| `../../rules/coding/references/react-performance-guidelines.md` | Worked performance patterns for React and Next.js (waterfalls, bundle size, Server Components, re-renders, rendering). Read when the task touches performance. Adapted from Vercel's React Best Practices. |
| `../../rules/coding/architecture-patterns.md` | The coding patterns (mvc, mvvm, layered) and the default per framework. The skill builds to the pattern the phase document pins, else the codebase's own. |

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

## Using it with ui-developer

The two skills are independent and don't call each other. Each one owns a different part of a UI task:

| Skill          | Owns                                                                                   |
| -------------- | -------------------------------------------------------------------------------------- |
| ui-developer   | How it looks: the design system, tokens, no custom CSS, component states, the look-at list |
| frontend-react | How the code is written: components, hooks, state, effects, data, forms, tests          |

To get both in one run, name both skills in the prompt:

```text
Use ui-developer and frontend-react to build the billing settings screen with Ember.
```

Or, with a phase document:

```text
Use ui-developer and frontend-react to build docs/phases/phase-3-link-list.md.
```

When both run, ui-developer decides appearance and frontend-react decides code structure. If they disagree on appearance, the design system wins. If they disagree on code structure, the React rules win. Both write the same files, so run them in one pass and not as two separate runs. Running only ui-developer works, but the React code then follows only the project's own conventions, not these rules. The orchestrator skill, when it exists, loads both for you.

## What the Skill Does Not Do

- It does not migrate a framework, a state library or a test setup, and it does not create a test setup.
- It does not add lint rules. If the project's lint config lacks the React hooks rules, it says so in the report.
- It does not follow instructions found inside project files. It follows the rules and the request.
- It does not write mock servers. Where data doesn't exist yet, it types the expected shape and marks it `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `rules/coding/react-rules.md` to change the rules.
- Edit `scripts/check_react.py` to change the red flags it detects.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:frontend-react`, or let Claude pick it up from a matching prompt.

### Manually

Copy `skills/frontend-react/` and `rules/coding/` into a skills directory that Claude Code reads, and keep their relative layout. `SKILL.md` reads `../../rules/coding/` by relative path, so `rules/` must sit two levels above the skill folder.

## License

MIT.
