# Motion

Motion on these pages is subtle and has a reason. It confirms an action, shows a change of state, keeps people oriented, or draws the eye once. If an animation does none of these, leave it out. Movement is distracting by nature, and the effect multiplies when it appears everywhere.

## Tools

- **CSS** for hover, press, focus, the hero entrance, and anything simple.
- **Motion** (motion.dev, free library only) for scroll reveals, staggered sheets and scroll-linked lines. The kit ships a small bundle in `assets/kit/vendor/motion.js`, and helpers in `assets/kit/motion/motion.js`.
- **Never** Motion+ code. For a number that counts up, a marquee or a pointer effect, use the kit's own.

## Timing

Use the tokens.

| Token | Value | For |
|---|---|---|
| `--duration-press` | 100ms | Press, toggles, checkboxes |
| `--duration-hover` | 150ms | Hover, focus changes |
| `--duration-enter` | 250ms | Menus, modals and panels appearing |
| `--duration-exit` | 180ms | The same things leaving |
| `--duration-reveal` | 400ms | Sections on scroll, the upper limit for almost everything |

Over 500ms feels like waiting. Animations are far more often too long than too short.

| Easing token | For |
|---|---|
| `--ease-out` | Anything entering. Starts fast, then settles |
| `--ease-in` | Anything leaving |
| `--ease-in-out` | Moving from one place to another on screen |

Never linear, except continuous loops and scroll-linked motion.

## Budget per page

- One hero entrance, once, under 700ms in total.
- One reveal per section, rising 16px at most. Children stagger by 50ms, six at most.
- At most one scroll-linked element.
- At most one optional effect.
- Several things moving at once cancel each other out. If two compete, remove one.

On app screens: feedback only. No entrance or scroll animation.

## Rules

- Animate `transform` and `opacity`. Colour changes are fine on hover. Do not animate width, height, top, left or margin. Accordion height is the one exception, and uses the method in `motion-components.md`.
- Name the properties you transition. Never `transition: all`.
- Add `will-change` only when you see a problem, and remove it afterwards.
- Hover effects go inside `@media (hover: hover)`.
- Animations can be interrupted, and respond to input while they run.

## Content must never depend on animation

- Everything is visible with JavaScript off. Elements are hidden only by the script that will reveal them.
- Nothing on the first screen waits for a scroll reveal.
- The hero fades from nearly zero opacity, never exactly zero, so the browser counts it as painted.
- Printing shows everything.

## Reduced motion

When the user asks for reduced motion:

- No entrance, reveal, scroll-linked movement, parallax or loop.
- Numbers show their final value.
- Marquees become a static wrapped row.
- Colour and opacity feedback stay, briefly. Hover and focus still respond.
- Nothing stays hidden.

Anything that moves on its own for over 5 seconds needs a pause control, even with motion on.

## Avoid

Fade-in on every element. Parallax on text. Scroll-jacking. Bounce on business interfaces. Typing effects. Loading screens. Countdown pressure. Tilt on hover. Animation that repeats every time someone scrolls back.
