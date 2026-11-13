# Using the kit in React or Next.js

For a new create-next-app project, `scripts/next_overlay.py` does steps 1, 2, 4, 5 (the helpers), 6 and 7 for you. The steps below are for any other React setup.

1. Copy `base/*.css`, `motion/motion.css` and the project's `design.css` into the app, and import them in the root layout, in that order.
2. Copy each `component.css` and `section.css` you use. The class names do not change.
3. Turn each sample into a component. Take the markup between the `sample:start` and `sample:end` comments, change `class` to `className`, and replace all text from `COPY.md`.
4. For Tailwind, import `theme.css`. New layout work may use utilities. Kit components keep their own CSS.
5. Do not import `motion/motion.js`. Use `Reveal.tsx` and the table in `references/motion/motion-react.md`. The hero entrance stays in CSS.
6. Add `theme.js` as an inline script in the document head, so the theme applies before first paint.
7. Load fonts with Fontsource, using the packages in `DESIGN.md`.
