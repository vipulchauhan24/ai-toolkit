# React Performance Guidelines

Worked patterns for the performance rules in section 8 of `react-rules.md`, read by the frontend-react skill for React and Next.js code. Each item gives the rule and the smallest example that shows it. Items marked "Next.js" apply only when the project depends on `next`.

Adapted from the Vercel Engineering "React Best Practices" guide, version 0.1.0, January 2026, as published in `davila7/claude-code-templates` under `react-best-practices/references/`. The source is a condensed and edited selection, not a copy. Section 9 lists what was left out and why. Licence of the source was not checked.

**Precedence:** `react-rules.md` wins over this file, and the project's conventions win over both. Items marked "measure" need a measured reason first, as `react-rules.md` section 8 says. Without a profiler, skip them and list them as "not measured". All other items apply without a measurement.

## Contents

1. Waterfalls
2. Bundle size
3. Server Components (Next.js)
4. Client data fetching
5. Re-renders
6. Rendering
7. JavaScript
8. Advanced patterns

## 1. Waterfalls

Impact: critical. Each sequential `await` adds a full network round trip.

### 1.1 Await where the value is used

Move the `await` into the branch that needs it, so a path that returns early does not wait.

```ts
// Incorrect: the skip path still waits for userData
async function handle(userId: string, skip: boolean) {
  const userData = await fetchUserData(userId)
  if (skip) return { skipped: true }
  return process(userData)
}

// Correct
async function handle(userId: string, skip: boolean) {
  if (skip) return { skipped: true }
  return process(await fetchUserData(userId))
}
```

Order checks so the cheapest one that can reject runs first: fetch the resource and return "not found" before fetching permissions.

### 1.2 Run independent calls together

```ts
// Incorrect: 3 round trips
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()

// Correct: 1 round trip
const [user, posts, comments] = await Promise.all([fetchUser(), fetchPosts(), fetchComments()])
```

Use `Promise.allSettled` when partial results are acceptable.

### 1.3 Start early when calls are partly dependent

Start every promise that has no dependency before awaiting the one that gates the rest.

```ts
// Incorrect: config waits for user, though it does not need it
const [user, config] = await Promise.all([fetchUser(), fetchConfig()])
const profile = await fetchProfile(user.id)

// Correct: config and profile overlap
const userPromise = fetchUser()
const configPromise = fetchConfig()
const user = await userPromise
const [config, profile] = await Promise.all([configPromise, fetchProfile(user.id)])
```

A task-graph library such as `better-all` does this automatically. Use it only if the project already has it.

### 1.4 Put a Suspense boundary around each slow section

Next.js App Router, or a data library that supports Suspense. An `await` at the top of a page blocks the whole layout. Move it into the component that needs it and wrap that component.

```tsx
// Incorrect: sidebar, header and footer wait for the data
async function Page() {
  const data = await fetchData()
  return <Layout><DataDisplay data={data} /></Layout>
}

// Correct: the layout renders now, DataDisplay streams in
function Page() {
  return (
    <Layout>
      <Suspense fallback={<Skeleton />}>
        <DataDisplay />
      </Suspense>
    </Layout>
  )
}

async function DataDisplay() {
  const data = await fetchData()
  return <div>{data.content}</div>
}
```

The fallback matches the final size (`react-rules.md` section 9). Do not wrap a section whose content decides the layout, or the page jumps.

## 2. Bundle size

Impact: critical. A smaller first bundle improves Time to Interactive and Largest Contentful Paint.

### 2.1 Avoid barrel imports

A barrel file re-exports a folder (`export * from './module'`). Importing one name from a large barrel loads every module behind it. The source reports up to 10,000 re-exports in popular icon and component libraries, and 200 to 800 ms of import time for many packages. These are the source's measurements, not ours.

- In your own code, do not create barrels. Import from the file that defines the name.
- For a library, import from its documented per-module entry (`import Button from '@mui/material/Button'`).
- Never import from a library's internal `dist` paths.
- Next.js 13.5 or later can rewrite barrel imports at build time with `experimental.optimizePackageImports` in the Next.js config. That is a config change. Suggest it in the report. Do not edit the config unless the phase document says to.

Libraries the source names as commonly affected: `lucide-react`, `@mui/material`, `@mui/icons-material`, `@tabler/icons-react`, `react-icons`, `@headlessui/react`, `@radix-ui/react-*`, `lodash`, `ramda`, `date-fns`, `rxjs`, `react-use`.

### 2.2 Load a module only when its feature turns on

```tsx
function AnimationPlayer({ enabled }: { enabled: boolean }) {
  const [frames, setFrames] = useState<Frame[] | null>(null)

  useEffect(() => {
    if (!enabled || frames) return
    let cancelled = false
    import('./animation-frames')
      .then((mod) => { if (!cancelled) setFrames(mod.frames) })
      .catch(() => { if (!cancelled) setFrames([]) })
    return () => { cancelled = true }
  }, [enabled, frames])

  if (!frames) return <Skeleton />
  return <Canvas frames={frames} />
}
```

Handle the failed import. A rejected `import()` with no `catch` leaves the skeleton forever.

### 2.3 Load analytics and other third-party scripts after the page is interactive

They do not block interaction. In Next.js use `next/dynamic` with `ssr: false` inside a client file. In plain React use `React.lazy` rendered after mount.

```tsx
'use client'
import dynamic from 'next/dynamic'

const Analytics = dynamic(
  () => import('@vercel/analytics/react').then((m) => m.Analytics),
  { ssr: false }
)
```

`ssr: false` is rejected outside a client file (the check script FAILs it), so keep this wrapper in its own client component and import that into the layout.

### 2.4 Lazy-load heavy components that are not on the first screen

Editors, charts, maps and modals. Use `next/dynamic` in Next.js, otherwise `React.lazy` inside a `Suspense` boundary.

```tsx
const MonacoEditor = dynamic(
  () => import('./monaco-editor').then((m) => m.MonacoEditor),
  { ssr: false }
)
```

Split by route first when the project has a router.

### 2.5 Preload on intent

Start the import when the user hovers or focuses the trigger, so the wait is over before the click.

```tsx
function EditorButton({ onClick }: { onClick: () => void }) {
  const preload = () => { void import('./monaco-editor') }
  return (
    <button onMouseEnter={preload} onFocus={preload} onClick={onClick}>
      Open editor
    </button>
  )
}
```

## 3. Server Components (Next.js)

Impact: high. Applies to the App Router only.

### 3.1 Pass the client only the fields it uses

Every property of an object passed from a Server Component to a Client Component is serialized into the page.

```tsx
// Incorrect: serializes all 50 fields to use one
async function Page() {
  const user = await fetchUser()
  return <Profile user={user} />
}

// Correct
async function Page() {
  const user = await fetchUser()
  return <Profile name={user.name} />
}
```

Never pass a field the client must not see (tokens, internal ids, other users' data). Choosing fields is also the security boundary.

### 3.2 Fetch in sibling components, not in the parent

Server Components in one tree run in order. A parent that awaits before rendering its child delays the child's fetch.

```tsx
// Incorrect: Sidebar's fetch starts after Page's fetch ends
export default async function Page() {
  const header = await fetchHeader()
  return <div><div>{header}</div><Sidebar /></div>
}

// Correct: Header and Sidebar fetch at the same time
async function Header() { return <div>{await fetchHeader()}</div> }
async function Sidebar() { return <nav>{(await fetchSidebarItems()).map(renderItem)}</nav> }

export default function Page() {
  return <div><Header /><Sidebar /></div>
}
```

When a layout must await and wrap content, take the content as `children`, so the page below it is created before the layout's await finishes.

### 3.3 Deduplicate non-`fetch` calls within a request

Wrap an authentication or database call with `React.cache()` so that several components calling it in one request run it once.

```ts
import { cache } from 'react'

export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return null
  return db.user.findUnique({ where: { id: session.user.id } })
})
```

`React.cache()` lives for one request only. Whether `fetch` calls are memoized for you depends on the installed Next.js version, so read that version's documentation before relying on it.

## 4. Client data fetching

Impact: medium to high.

### 4.1 Let the data library deduplicate

Use the project's data library (SWR, TanStack Query or the router's loaders). Two components that fetch the same key then share one request, a cache and revalidation. Without one, follow `react-rules.md` section 4: fetch in an effect with an `AbortController`. Do not add a data library for one screen.

### 4.2 Share one global listener across hook instances

A hook that calls `addEventListener` registers one listener per use. Keep a module-level registry and one listener.

```tsx
const callbacks = new Map<string, Set<() => void>>()
let listening = false

function onKeyDown(e: KeyboardEvent) {
  if (e.metaKey) callbacks.get(e.key)?.forEach((cb) => cb())
}

function useKeyboardShortcut(key: string, callback: () => void) {
  useEffect(() => {
    if (!callbacks.has(key)) callbacks.set(key, new Set())
    callbacks.get(key)!.add(callback) // key is set on the line above
    if (!listening) {
      window.addEventListener('keydown', onKeyDown)
      listening = true
    }
    return () => {
      const set = callbacks.get(key)
      set?.delete(callback)
      if (set?.size === 0) callbacks.delete(key)
      if (callbacks.size === 0) {
        window.removeEventListener('keydown', onKeyDown)
        listening = false
      }
    }
  }, [key, callback])
}
```

The source does this with `useSWRSubscription`. Use that only if the project has SWR.

## 5. Re-renders

Impact: medium.

### 5.1 Read state where it is used

Do not subscribe to `useSearchParams` or storage if the value is read only inside a handler. Read it in the handler.

```tsx
function ShareButton({ chatId }: { chatId: string }) {
  const handleShare = () => {
    const ref = new URLSearchParams(window.location.search).get('ref')
    shareChat(chatId, { ref })
  }
  return <button onClick={handleShare}>Share</button>
}
```

### 5.2 Return early before expensive work (measure)

When a component computes something and then returns a skeleton, move the computation into a child that only renders after the early return. A `memo` child lets React skip it while `loading` is true.

```tsx
const UserAvatar = memo(function UserAvatar({ user }: { user: User }) {
  const id = useMemo(() => computeAvatarId(user), [user])
  return <Avatar id={id} />
})

function Profile({ user, loading }: Props) {
  if (loading) return <Skeleton />
  return <UserAvatar user={user} />
}
```

If the React Compiler is on, add no `memo` or `useMemo` by hand.

### 5.3 Depend on primitives in effects

```tsx
// Incorrect: re-runs on any user field
useEffect(() => { track(user.id) }, [user])

// Correct
useEffect(() => { track(user.id) }, [user.id])

// Incorrect: runs for width 767, 766, 765...
useEffect(() => { if (width < 768) enableMobileMode() }, [width])

// Correct: runs only when the boolean changes
const isMobile = width < 768
useEffect(() => { if (isMobile) enableMobileMode() }, [isMobile])
```

### 5.4 Subscribe to the derived boolean

A hook that returns `window.innerWidth` re-renders on every pixel. A hook that returns `matchMedia('(max-width: 767px)').matches` re-renders when the answer changes.

```tsx
const isMobile = useMediaQuery('(max-width: 767px)')
```

### 5.5 Initialize costly state lazily (measure)

`useState(expensive())` runs `expensive()` on every render and discards the result after the first. Pass a function.

```tsx
const [index] = useState(() => buildSearchIndex(items))
const [settings] = useState(() => {
  const stored = localStorage.getItem('settings')
  return stored ? JSON.parse(stored) : {}
})
```

For `useState(0)`, `useState(props.value)` or `useState({})` the function form adds nothing. A component that reads `localStorage` in `useState` fails on the server in Next.js: read it in an effect there, or see 6.3.

### 5.6 Mark non-urgent updates as transitions (measure)

Wrap the update that can wait (a filtered list that follows an input) in `startTransition`, or defer the value with `useDeferredValue`. The urgent update, such as the input's own value, stays outside.

```tsx
const [query, setQuery] = useState('')
const [filter, setFilter] = useState('')

function onChange(e: React.ChangeEvent<HTMLInputElement>) {
  setQuery(e.target.value)
  startTransition(() => setFilter(e.target.value))
}
```

## 6. Rendering

Impact: medium.

### 6.1 Defer off-screen rendering of long lists

`content-visibility: auto` with `contain-intrinsic-size` lets the browser skip layout and paint for items off screen. It is a CSS rule, so use it only where the design system allows custom CSS. Otherwise virtualize the list, as `react-rules.md` section 8 says.

```css
.message-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

The source reports about 10 times faster initial render for 1,000 items. That is its measurement for its page, not a promise.

### 6.2 Hoist static JSX

JSX that never changes can live at module level, so it is not created on every render. This matters most for large static SVG nodes.

```tsx
const loadingSkeleton = <div className="animate-pulse h-20 bg-gray-200" />

function Container({ loading }: { loading: boolean }) {
  return <div>{loading ? loadingSkeleton : null}</div>
}
```

### 6.3 Render client-only values without a flash or a mismatch

A value that exists only in the browser (the theme in `localStorage`) breaks server rendering if read during render, and flashes the default if read in an effect. The source's fix is a small inline script that sets the value before React hydrates.

```tsx
function ThemeWrapper({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div id="theme-wrapper" suppressHydrationWarning>{children}</div>
      <script
        // SANITIZED: constant string written in this file, no user input
        dangerouslySetInnerHTML={{
          __html: `(function(){try{var t=localStorage.getItem('theme')||'light';var e=document.getElementById('theme-wrapper');if(e)e.className=t}catch(e){}})()`,
        }}
      />
    </>
  )
}
```

- The script must be a constant you wrote. The `SANITIZED:` comment is required by `react-rules.md` section 11 and by the check script.
- `suppressHydrationWarning` on the changed element is not in the source. The script changes the class before hydration, so the server and client markup differ. Confirm the installed React version accepts it for this case.
- If the design system or the framework already provides theme handling, use it and skip this pattern.

### 6.4 Keep state when a component hides and shows

React's `<Activity mode={isOpen ? 'visible' : 'hidden'}>` keeps the state and DOM of a hidden subtree. It needs a React version that ships `Activity`. Check the installed version before using it, and otherwise leave the component mounted and hidden by the design system's own visibility mechanism.

## 7. JavaScript

Impact: low to medium. Apply in hot paths and in loops over large arrays.

### 7.1 Build a Map for repeated lookups

```ts
// Incorrect: O(n) per order
orders.map((o) => ({ ...o, user: users.find((u) => u.id === o.userId) }))

// Correct: build once, then O(1) per order
const userById = new Map(users.map((u) => [u.id, u]))
orders.map((o) => ({ ...o, user: userById.get(o.userId) }))
```

### 7.2 Use a Set for repeated membership checks

```ts
const allowedIds = new Set(['a', 'b', 'c'])
items.filter((item) => allowedIds.has(item.id))
```

### 7.3 Combine passes over a large array

Three `.filter()` calls walk the array three times. One `for...of` loop fills three arrays in one pass.

### 7.4 Find the min or max with a loop

Sorting to find one element is O(n log n) and, on state, mutates. One pass with a running best value is O(n) and needs an empty-array guard.

```ts
function latestProject(projects: Project[]) {
  let latest: Project | null = null
  for (const p of projects) {
    if (!latest || p.updatedAt > latest.updatedAt) latest = p
  }
  return latest
}
```

### 7.5 Compare lengths before an expensive array comparison

If the lengths differ, the arrays differ. Check that before sorting, joining or deep-comparing, and use `toSorted()` on the rest.

### 7.6 Hoist static regular expressions

A literal such as `/^\d{3}$/` belongs at module level. A regular expression built from user input (a search highlight) is built inside the component, with the input escaped. A regular expression with the `g` flag keeps `lastIndex` between calls, so reset it or avoid `g`.

### 7.7 Cache repeated storage reads (measure)

`localStorage`, `sessionStorage` and `document.cookie` reads are synchronous. When the same key is read many times, keep a module-level `Map` and invalidate it.

```ts
const storageCache = new Map<string, string | null>()

export function readStorage(key: string) {
  if (!storageCache.has(key)) storageCache.set(key, localStorage.getItem(key))
  return storageCache.get(key)
}

export function writeStorage(key: string, value: string) {
  localStorage.setItem(key, value)
  storageCache.set(key, value)
}

window.addEventListener('storage', (e) => { if (e.key) storageCache.delete(e.key) })
```

Do not cache tokens or personal data in a module-level object.

### 7.8 Cache a pure function called many times with the same input (measure)

When a profile shows `slugify(project.name)` or a similar pure function called hundreds of times with the same arguments, memoize it in a module-level `Map`. A `Map` works in utilities and event handlers, which a hook does not.

## 8. Advanced patterns

Impact: low.

### 8.1 Keep a handler out of an effect's dependencies

When an effect subscribes to an event and the handler changes on every render, put the latest handler in a ref so the subscription stays. If the installed React provides `useEffectEvent`, use that instead.

```tsx
function useWindowEvent(event: string, handler: () => void) {
  const handlerRef = useRef(handler)
  useEffect(() => { handlerRef.current = handler }, [handler])

  useEffect(() => {
    const listener = () => handlerRef.current()
    window.addEventListener(event, listener)
    return () => window.removeEventListener(event, listener)
  }, [event])
}
```