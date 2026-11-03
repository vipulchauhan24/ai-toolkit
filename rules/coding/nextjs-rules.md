# Next.js Rules

Rules for Next.js code, read by the frontend-react skill together with `react-rules.md`, only when the project depends on `next`. They cover the Next.js parts. React rules still apply.

**Precedence:** a rule in the phase document wins over the existing codebase's conventions, and the conventions win over these rules. Two exceptions:

- The secret and server-only rules (sections 2, 4 and 7) never yield to a convention. If the codebase breaks one, don't copy it, and list it in the report.
- Where `check_react.py --next` FAILs new code only because a convention requires it, keep the convention and list the FAIL, as `react-rules.md` says.

**Version:** these rules assume Next.js 15 or later. Next.js changes between major versions. For a default this file does not settle, read the installed version's documentation if the run can reach it (the docs site or a copy in the project). If it cannot, follow the project's existing code and list the version assumption in the report.

**Pattern:** the project's pattern is `layered` unless the phase document or the codebase says otherwise (`architecture-patterns.md`). Pages, layouts, route handlers and Server Actions are handlers: a Server Component that reads data calls a service, never data access.

For performance work (parallel fetching across Server Components, `React.cache()`, serialization at the server-client boundary, `next/dynamic`), also read section 3 and the bundle-size section of `references/react-performance-guidelines.md`.

## Contents

1. Version and router
2. Server and Client Components
3. Data fetching
4. The server-client boundary
5. Mutations
6. Navigation and assets
7. Hydration and browser-only code
8. Files
9. Checks

## 1. Version and router

- Read the Next.js version from `package.json`, and note whether the project uses the App Router (`app/`), the Pages Router (`pages/`), or both. Match it. Don't migrate a project from one router to the other.
- Sections 2 to 5 describe the App Router. For the Pages Router, use its data functions (`getServerSideProps`, `getStaticProps`) as the project does, `next/head` for the title, and apply only the link, image and router-hook bullets of section 6, section 7 and section 9. The file conventions in section 8 are App Router only: follow the project's own for `pages/`.
- In a project with both routers, apply the rules of the router that owns the file you change.

## 2. Server and Client Components

- A component is a Server Component unless its file starts with `'use client'`. Keep it that way.
- Add `'use client'` only to the smallest component that needs state, effects, event handlers or browser APIs. Push it toward the leaves. Everything a client file imports becomes client code.
- Keep a layout or page a Server Component. Pass a Server Component to a Client Component as `children` or a prop instead of importing it there.
- A Client Component cannot be `async`.
- Don't import server-only code (database clients, secrets, `server-only` modules) into a Client Component.

## 3. Data fetching

- Fetch in Server Components, not in effects. Use the project's data layer if it has one. A Client Component that needs data that changes after load (polling, search as you type, a click) uses the project's client data library, otherwise `react-rules.md` section 4.
- Next.js 15 or later: `params`, `searchParams`, `cookies()` and `headers()` are async. `await` them in Server Components and `generateMetadata`. In a Client Component, read `params` with `use()`.
- Start independent fetches together (`Promise.all`), or split them into sibling components so each fetches on its own and streams behind its own `Suspense` boundary or `loading.tsx`.
- Use `React.cache` to deduplicate a non-`fetch` call (a database query, an SDK call) within one request.
- State caching explicitly. Defaults for `fetch` and route handlers differ between Next.js versions, so set `cache`, `revalidate` or tags where the behavior matters, and don't rely on the default. When neither the phase document nor the project gives a policy, don't cache data that depends on the user or the request (`cache: 'no-store'`), and list the caching of every other fetch as an assumption.
- Don't fetch in a layout what only one page needs.

## 4. The server-client boundary

- Pass a Client Component only the fields it uses, not a whole record. Everything passed is serialized into the page.
- Props across the boundary must be serializable. Functions are allowed only if they are Server Actions.
- Never pass a secret or a token across the boundary. Pass an id only when the client needs it (a list key, a link, a Server Action argument), and let the server check that the user may act on it.

## 5. Mutations

- Call the project's Server Action or route handler. Writing the server side is outside this skill. If it does not exist, take the call as a typed prop (`onSubmit: (input: T) => Promise<Result>`) so the file builds, mark `PLACEHOLDER-DATA`, and stop at the boundary.
- Show pending and error states with `useActionState` and `useFormStatus` (or `useTransition` for a non-form call).
- After a mutation, the data refreshes through the project's revalidation (`revalidatePath` or `revalidateTag` in the Server Action) or `router.refresh()` in the component, not by reloading the page. If the action does not revalidate, list that in the report.

## 6. Navigation and assets

- Use `next/link` for internal links and `next/image` for images, with `width` and `height` (or `fill` with a sized parent). Mark only the largest above-the-fold image as `priority`.
- Set the page title and description with the `metadata` export or `generateMetadata`, not with a tag in the component. A page that exports either is a Server Component: move its client hooks into a child Client Component.
- Use the router hooks (`useRouter`, `usePathname`, `useSearchParams`) only in Client Components. Wrap a component that reads `useSearchParams` in `Suspense`.

## 7. Hydration and browser-only code

- Don't read `window`, `document`, `localStorage`, `Date.now()` or `Math.random()` while rendering a Client Component. The server and the browser would render different output. Read them in an effect or with `useSyncExternalStore`.
- Use `suppressHydrationWarning` on one element with a known, harmless difference (a timestamp), never on a whole subtree.
- Use `next/dynamic` with `ssr: false` only inside a Client Component, for a widget that cannot render on the server.
- Only variables prefixed `NEXT_PUBLIC_` reach the browser. Never put a secret in one.

## 8. Files

- Follow the App Router conventions: `page`, `layout`, `loading`, `error`, `not-found`. `error` must be a Client Component.
- Keep route files thin. Put the components, hooks and types in the project's feature or component folders, or in a private `_components` folder beside the route.
- Don't add a route, a layout or a middleware the phase document does not list. A `loading`, `error` or `not-found` file for a route the phase lists is not a new route: add it where section 3 and `react-rules.md` section 9 call for it.

## 9. Checks

Run what the project provides, in this order, and fix failures before moving on:

1. Typecheck.
2. Lint, including the project's Next.js config. If the config does not extend `next/core-web-vitals`, say so in the report and don't add it unless asked.
3. Tests.
4. `next build`. It catches server and client boundary errors that typecheck misses.
5. The skill's `scripts/check_react.py` with `--next` for an App Router file, without it for a Pages Router file. With `--next` it FAILs hooks or handlers in a page or layout without `'use client'`, `error.tsx` without it, `ssr: false` outside a client file, an async Client Component, and a non-`NEXT_PUBLIC` variable in a client file. It reports `<img>`, internal `<a href="/...">` and hooks in files without `'use client'`. Every other rule is not machine-checked: say so in the report.

Test Client Components and the functions that Server Components call. The usual component test tools may not render an async Server Component. Check the project's test setup, and list the Server Components you could not test.
