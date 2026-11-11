# frontend-react

## Should trigger

- "Build this in React."
- "Build the settings page in Next.js."
- "Write a React component for an order table."
- "Add a hook that loads the user's orders."
- "Fix this React code, it re-renders on every keystroke."
- "Review this component against the React rules."
- "Add a form with validation to this Next.js app."
- "Convert this class component to a function component."
- "Make this Next.js page a Server Component."
- "Build phase 3 of the plan in React." (with a phase document pinning React)

## Should NOT trigger

- "Build this in Vue." (not React)
- "Write a Svelte component."
- "Build a React Native screen."
- "Pick colors and spacing for my app." (design-system-builder)
- "Make this screen look like my design system." (ui-craft, alone)
- "Build the REST API for orders."
- "Write the SQL schema for users."
- "Write plain HTML and CSS for a landing page."
- "Explain how useEffect works."
- "Review this Python script."

## Functional

**New component**
- Given: a Next.js project with TypeScript and Vitest
- When: asked for an orders table
- Then: the typecheck, lint and tests were run once before changes. The data boundary is typed before the components. Tests exist and pass. `scripts/check_react.py --next` was run on the changed files with no FAIL. The report has a status line, stack, files, assumptions, checks and any `PLACEHOLDER-DATA`.

**Wrong stack**
- Given: a Vue project
- When: asked to build a React component
- Then: it stops with a Blocked report and writes no code.

**Missing Python**
- Given: no `python3` on the machine
- When: the skill starts
- Then: it stops with a Blocked report. It does not fall back to searching files by hand.

**Pinned pattern mismatch**
- Given: a phase document pinning `mvvm` and a codebase that uses `layered`
- When: run non-interactively
- Then: a Blocked report containing `Pattern mismatch`, and no code.
