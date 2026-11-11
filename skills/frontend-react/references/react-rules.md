# React Rules

Rules for React code, read by the frontend-react skill. For a Next.js project the skill also reads `nextjs-rules.md` in this folder. They cover how the code is written. Appearance, tokens and the component look belong to the project's `DESIGN.md` (written by ui-craft) or the design system the spec names, not here.

**Precedence:** a rule in the phase document wins over the existing codebase's conventions, and the conventions win over these rules. Two exceptions:

- Section 11 (Security) never yields to a convention. If the codebase breaks a security rule, don't copy it, don't fix it, and list it in the report as unrelated code. A phase document that conflicts with section 11 is a Blocked report.
- Where `scripts/check_react.py` FAILs new code only because a convention requires it (for example index keys in a project that uses them), keep the convention and list the FAIL and the convention in the report. A FAIL from section 11 is always fixed.

**Assumptions:**

- React 18 or later. Rules for 19 are marked. `toSorted()`, `toReversed()` and `toSpliced()` need an ES2023 target (Node 20 or current browsers). For an older target, copy first: `[...items].sort()`.
- The numeric limits (150 lines, three and five fields, 200 rows, 200 ms and 400 ms) are starting defaults, not measured values. A limit the project already sets wins.
- Where a rule says "if installed" or "if the project has", check `package.json` first.
- Cite a rule in the report by its section number and its first three words, for example "8 Measure first".

**Pattern:** the project's pattern (`mvc`, `mvvm` or `layered`) comes from the phase document, else the codebase, as `architecture-patterns.md` describes. For `mvvm`, a component is the view, a hook is the view model, and the typed data types plus the data function are the model. Sections 1 and 5 say how that fits the rules below.

## Contents

1. Components
2. Props and TypeScript
3. State
4. Effects
5. Data boundary
6. Forms
7. Lists and keys
8. Performance
9. Errors and loading
10. Accessibility in code
11. Security
12. Tests
13. Files and naming
14. Checks

## 1. Components

- Write function components only. No class components, except an error boundary when the installed React has no other way to write one.
- One component does one job. Split at 150 lines, or when a part has its own state and a different reason to change.
- Define every component at module level. Never define a component inside another component's body: it remounts on every render and loses its state.
- Name components in PascalCase, one exported component per file. Small private helpers may share the file.
- Compose with `children` and slots before adding a prop. A boolean prop that switches the layout is two components.
- Presentational components receive data and callbacks as props. They do not fetch, read the URL or touch storage. In an `mvvm` project, the screen component (the view) calls its one view-model hook and passes the result to presentational components as props.
- Don't mutate props, state or context values. Copy, then change the copy.
- React 19 or later: pass `ref` as a normal prop. Don't add `forwardRef` to new components. Below 19, use `forwardRef`.

## 2. Props and TypeScript

- Use TypeScript with `strict` on. A JavaScript project stays JavaScript: don't convert it.
- Type every prop with an interface or type next to the component. Export it only if another file imports it.
- No `any`. Use `unknown` and narrow it. No `@ts-ignore`; use `@ts-expect-error` with a reason. No non-null `!` without a comment saying why it holds.
- Model states that exclude each other as a discriminated union (`{ status: 'loading' } | { status: 'error'; error: AppError } | { status: 'ready'; data: T }`), not several booleans.
- Type event handlers with React's event types. Type `children` as `React.ReactNode`.
- Don't use `defaultProps`. Use default parameter values.
- Give a `useState` initial value that fixes its type, or pass the type: `useState<User | null>(null)`.

## 3. State

- Keep state as local as it can be. Lift it to the nearest common parent only when two siblings need it.
- Never store what you can compute. Derive it during render. Duplicated state goes out of sync.
- Use `useReducer` when state has more than three related fields or the next state depends on named transitions.
- View settings that must survive a reload or be shared by link (filter, sort, tab, page) go in the URL (search params or route params), not in component state. Drafts and preferences such as the theme go in the storage the project already uses.
- Context is for values that change rarely (theme, current user, locale). Don't put fast-changing state in context. Split one big context into several.
- For state shared across distant parts of the app, use the library the project already has. Don't add a state library for one screen.
- Don't copy a prop into state. If you must reset state when a prop changes, put a `key` on the component.

## 4. Effects

- An effect synchronizes with something outside React: a subscription, a timer, a browser API, a third-party widget. Nothing else.
- Don't use an effect to compute a value (derive it), respond to a click (put it in the handler), or reset state on a prop change (use `key`).
- Don't fetch in an effect when the project has a data library or router loaders. Use them. If it has none, fetch in an effect with an `AbortController` and ignore a result that arrives after cleanup.
- List every reactive value the effect reads in its dependency array. Never silence `exhaustive-deps`; restructure instead.
- Every effect that starts something returns a cleanup that stops it.
- Don't read or write the DOM with `document.querySelector`. Use a ref.
- An effect that runs only once (empty dependency array) must still be safe to run twice, because Strict Mode does that in development.

## 5. Data boundary

- A screen receives its data through typed props, or through one named hook per data source (`useOrders()`). It does not call `fetch` inline. In an `mvvm` project, the screen calls one view-model hook (`useOrderList()`). That hook calls the data-source hooks, derives the display state, and exposes the handlers.
- Each data source exposes all of its states: loading, error, empty and ready. A screen that handles only "ready" is unfinished.
- Define the data type from the API contract or phase document. Don't invent a shape. Validate data from outside your code (an API response, `localStorage`, a URL) at the boundary. Use the project's schema library if it has one. Otherwise write a type guard (`isOrder(value: unknown): value is Order`) in the data function, assign `res.json()` to `unknown` before the guard runs, and treat a failed guard as the error state. Never cast the response with `as`.
- Where the data source doesn't exist yet, type the boundary, feed it a placeholder, and mark it `PLACEHOLDER-DATA: <what the real source must supply>`. Don't write a mock server.
- Mutations call one typed function. The component handles pending, success and error, and disables the control while pending.

## 6. Forms

- Use the form library the project has. If it has none, use plain controlled inputs for fewer than five fields, or uncontrolled inputs read through `FormData` on submit.
- React 19 or later: prefer form actions with `useActionState` and `useFormStatus` over hand-written pending state.
- Validate on submit and again on blur for fields that have a format. Show an error beside its field, in words that say how to fix it.
- Disable the submit control while submitting, and never send the same submission twice.
- Keep the user's input on a failed submit.
- A `<label>` is tied to its input (`htmlFor` and `id`, or wrapping). A placeholder is not a label.

## 7. Lists and keys

- Every element rendered from an array has a `key` that is stable and unique among siblings: a database id or a slug.
- Never use the array index as a key when the list can reorder, insert or delete. An index is acceptable for a static list that never changes.
- Never generate a key at render time (`Math.random()`, `crypto.randomUUID()`). A row the user adds before the server returns an id gets a client id created once, in the handler that adds it, and stored with the row. Replace it when the server id arrives without remounting the row.
- Put the key on the outermost element returned by the `map` callback. For a fragment, use `<Fragment key=...>`.

## 8. Performance

Worked examples for each rule below are in `react-performance-guidelines.md` in this folder, along with Next.js server patterns.

Work in this order, because the earlier items cost more than the later ones: waterfalls, bundle size, re-renders, then micro-optimizations.

- Measure first before memoization, `startTransition`, `useDeferredValue` and lazy state initialization. Name the cause (a profile, a bundle report, a network trace) in a comment or in the report. Without a profiler (for example in a non-interactive run), don't add them and list them as "not measured". Every other rule in this section applies without a measurement. Don't claim an improvement without one.

**Waterfalls**

- Start independent async work together with `Promise.all`. Use `Promise.allSettled` when partial results are acceptable. Never `await` one independent call after another.
- Await where the value is used. Move an `await` into the branch that needs it, so a path that returns early does not wait.
- Chain only calls that depend on each other. Start everything else first.
- Put a `Suspense` boundary around each independent slow section, so the layout shows while it loads.

**Bundle size**

- Import from the module that defines what you need. Don't create barrel files (an `index` that re-exports a folder) in your own code. For a large library, use its documented per-module entry or the framework's package-import optimization. Never import from a library's internal `dist` paths.
- Lazy-load heavy components that are not on the first screen: editors, charts, maps, modals. Use `React.lazy` or the framework's dynamic import, and split by route when the project has a router.
- Load analytics and other third-party scripts after the page is interactive.
- Preload a lazy component when the user signals intent (hover or focus).

**Re-renders**

- Don't add `useMemo`, `useCallback` or `React.memo` by default. Add one when a profile shows a cost, and leave a comment with what was measured. If the React Compiler is enabled in the project, add none by hand.
- Don't create new objects, arrays or functions in props of a memoized child, or in a context value, on every render.
- Read state where it is used. Pass the child what it needs instead of reading it in a parent that does not use it.
- Depend on primitives in effect arrays, not on objects or arrays that are new on every render.
- Subscribe to the smallest slice of a store (a selector), not the whole store.
- Initialize costly state lazily: `useState(() => build())`.
- Wrap non-urgent updates in `startTransition`, or defer a value with `useDeferredValue`.
- A handler that an effect reads but that should not restart it: use `useEffectEvent` if the installed React provides it, otherwise a ref that holds the latest handler.

**Rendering**

- Render conditions explicitly: `count > 0 ? <List /> : null`. Never `count && <List />`, which renders `0`.
- Virtualize a list that can exceed 200 rows. Paginate or filter before that when the data source allows.
- Give images explicit width and height, and `loading="lazy"` for images below the first screen.
- Don't run expensive work in render. Move it to an event handler, a worker or the server.

**JavaScript**

- Never mutate state or props. Use `toSorted()`, `toReversed()` and `toSpliced()`, or copy first. `.sort()` on state is a bug.
- For repeated lookups inside a loop, build a `Map` or `Set` once.
- Hoist constants, regular expressions and static objects out of components.
- Return early. Combine several passes over a large array into one.
- Don't micro-optimize beyond this without a measurement.

## 9. Errors and loading

- Wrap each route, or each independent section, in an error boundary with a recovery action (retry or go back). A thrown error in one panel must not blank the page.
- An error boundary does not catch errors thrown in event handlers or async code. Catch them there and put them in error state shown beside the control that failed.
- Never swallow an error with an empty `catch`. Show it to the user, and send it to the project's logger or error reporter. If the project has neither, call `console.error`.
- Use `Suspense` with a fallback that matches the final layout's size, so the page does not jump.
- For your own pending states, show the loading indicator only after 200 ms of waiting, and once shown keep it for at least 400 ms, so it does not flash. Use one shared timer hook for both. A `Suspense` fallback shows immediately; leave that as it is. Skip this rule if the design system or phase document defines loading behavior.
- An error message says what failed and what the user can do. It never shows a stack trace, an internal id or raw server text.

## 10. Accessibility in code

`DESIGN.md` and the ui-craft skill own the visual floor. In code:

- Use the semantic element: `<button>` for actions, `<a>` for navigation, `<ul>` for lists, `<form>` for forms. Never put `onClick` on a `<div>` or `<span>`.
- A control that is not a native element needs a role, a keyboard handler and a tab stop. Prefer a native element instead.
- Move focus to the heading after a route change, unless the router already does it (read its documentation). Move focus after opening or closing a dialog, to the first control or the trigger.
- Don't remove an element's focus outline in code.
- Pair every `aria-*` attribute with a reason. No ARIA is better than wrong ARIA.

## 11. Security

- Never use `dangerouslySetInnerHTML` with content you didn't write. If it is needed, sanitize with a maintained library, and comment `SANITIZED:` with where.
- A link that opens a new tab has `rel="noopener"`. Add `noreferrer` for sites you don't control. Leave it off where the target needs the referrer, with a comment saying why.
- Don't build a URL for `href`, `src` or `window.location` from user input without parsing it (`new URL(value, window.location.origin)`) and checking the result. Allow `https:`, `mailto:`, `tel:`, and a path that starts with a single `/`. Reject `//host`, `javascript:` and `data:`.
- No secrets, tokens or private keys in client code or in variables the bundler exposes (`VITE_`, `NEXT_PUBLIC_`, `REACT_APP_`).
- Don't write tokens to `localStorage` or `sessionStorage`. Use an `httpOnly` cookie set by the server, or the storage of the project's auth library. If the project already stores tokens in `localStorage`, add no new use and list it in the report.
- Don't log personal data or tokens. Remove `console.log` before finishing. `console.error` in a `catch` is allowed when the project has no logger.

## 12. Tests

- Use the project's runner. If none exists, don't create a test setup: say so in the report. For a bug fix in such a project, write the reproduction steps in the report in place of the failing test.
- Test behavior through what the user sees and does. Query by role and accessible name (`getByRole`), then by label or text. Use `data-testid` only when nothing else works.
- Drive interactions with `userEvent`, not `fireEvent`. Await async results with `findBy*` or `waitFor`. Don't use fixed sleeps.
- Cover every state of each screen: loading, empty, error, ready, and the disabled and pending states of its controls.
- Mock at the network boundary, not by mocking your own hooks or components. Use MSW if the project has it, otherwise the project's own fetch mock, otherwise a stubbed `fetch` in the test.
- No snapshot tests of whole component trees. A small snapshot of a pure output is fine.
- Test custom hooks through a component or `renderHook`. Don't test implementation details such as state variables or internal function calls.
- Treat an `act` warning or a console error in a test as a failure.
- A bug fix starts with a failing test that reproduces it.

## 13. Files and naming

- Follow the project's layout. With none, group by feature: `features/<name>/` holding its components, hooks, types and tests. Shared pieces go in `components/` and `hooks/`.
- Name a file after the one component or hook it exports: `OrderTable.tsx`, `useOrders.ts`, `OrderTable.test.tsx` beside the component. If the project uses kebab-case file names (`use-orders.ts`), match it for every new file.
- Hooks start with `use` and call at least one hook. A function that calls none is a plain function.
- Use named exports. Use a default export only where the router or framework requires one.
- Import with the project's alias if it has one. No deep relative paths such as `../../../`.
- Don't refactor unrelated code. Leave a note in the report instead.

## 14. Checks

Run what the project provides, in this order, and fix failures before moving on:

1. Typecheck (`tsc --noEmit` or the project's script).
2. Lint, including `react-hooks/rules-of-hooks` and `react-hooks/exhaustive-deps`. If the project's lint config lacks them, say so in the report and don't add them unless asked.
3. Unit and component tests.
4. Build.
5. The skill's `scripts/check_react.py` on the changed files. It checks only: `any`, `@ts-ignore`, class components, unsanitized `dangerouslySetInnerHTML`, `onClick` on `div` or `span`, index or random keys, `target="_blank"` without `rel="noopener"`, effects with no dependency array, direct DOM queries, `console.log`, secrets in client-exposed variables, and `&&` rendering `0`. It reports `fetch` in an effect, memoization, in-place `.sort()`, `.reverse()` and `.splice()`, consecutive `await`s and `PLACEHOLDER-DATA`. Every other rule is not machine-checked: say so in the report.

Don't run end-to-end tests, migrations or anything that touches a real service unless asked. List what you skipped.
