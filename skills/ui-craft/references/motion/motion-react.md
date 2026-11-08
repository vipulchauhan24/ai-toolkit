# Motion in React and Next.js

Use the `motion` npm package, free features only. See `assets/kit/examples/react/`.

- Wrap the app in `MotionConfig reducedMotion="user"`. It turns off transform and layout animation for people who ask.
- Use `LazyMotion` with `domAnimation` and the `m` components, to keep the bundle small.
- In the Next.js App Router, components that animate are client components. Keep them small and pass server-rendered content in as children.
- Hide elements only after hydration, so that content is visible before JavaScript runs.

| Vanilla kit | React |
|---|---|
| `data-reveal` | `whileInView` with `viewport={{ once: true }}` |
| `data-reveal-group` | Parent and child `variants` with `staggerChildren` |
| Phone sheet, modal | `AnimatePresence` with an `exit` |
| Tab indicator | `layoutId` |
| `data-timeline` | `useScroll` and `useTransform` on `scaleY` |

Hover and press stay in CSS. They do not need JavaScript. The hero entrance stays in CSS too, so it runs before hydration.
