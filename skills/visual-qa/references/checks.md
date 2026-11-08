# Measured checks

`scripts/capture.py` measures these in the real page. A measured check is a fact, so it limits the grade: no grade in that area can be better than the cap. `scripts/report.py` applies the caps. You do not apply them yourself, and you do not argue with them in `grades.json`.

## On every screenshot

| Check | Fails when | Warns when | Area | Cap on fail | Cap on warn |
|---|---|---|---|---|---|
| `overflow` | The page scrolls sideways | | Responsiveness | D | |
| `margins` | Left and right content edges differ by more than 8px or 2% of the width | | Layout | C | |
| `empty-band` | A stretch of plain background is taller than one screen | Over 60% of a screen | Spacing | C | B |
| `hidden-content` | Text is still invisible after the whole page was scrolled | | Motion | D | |
| `tap-target` | Under 24px, at widths up to 820px, measured with touch emulation on. A checkbox or radio is measured by its label | Under 44px | Responsiveness | C | none |
| `broken-image` | An image did not load | | Imagery | D | |
| `img-alt` | An image has no `alt` attribute | | Accessibility | C | |
| `img-size` | | No `width` and `height` attributes | none | | |
| `h1` | Not exactly one visible `h1` | | Accessibility | C | |
| `heading-order` | | A heading level is skipped | none | | |
| `small-text` | | Running text under 14px | Typography | | B |
| `long-lines` | | A paragraph over about 90 characters wide | Typography | | B |
| `contrast` | Text below WCAG AA: 4.5:1, or 3:1 for large text | | Colour | C | |
| `field-label` | A form field has no label | | Accessibility | C | |
| `button-name` | A link or button has no name | | Accessibility | C | |
| `placeholder-text` | "Coming soon", "lorem ipsum", "TODO" and similar | | Layout | C | |
| `transition-all` | | `transition: all` on an interactive element | Motion | | B |

Width is measured without the scrollbar, because a visible browser shows one. Contrast skips text on a picture or gradient, so judge that by eye.

## Once per route

These apply to every screenshot of the route.

| Check | Fails when | Warns when | Area | Cap on fail | Cap on warn |
|---|---|---|---|---|---|
| `reduced-hidden` | Content stays invisible under reduced motion until scrolled | | Motion | D | |
| `reduced-animating` | An endless animation keeps running under reduced motion | | Motion | C | |
| `keyboard` | Tab reaches nothing | | Accessibility | D | |
| `focus-visible` | A focused element shows no outline or ring | | Accessibility | C | |
| `broken-link` | A same-site link returns 400 or above, or nothing | | Accessibility | C | |
| `broken-anchor` | A `#link` points at a missing section | | Accessibility | C | |
| `link-click` | | A visitor cannot click the link | none | | |
| `empty-submit` | An empty form tried to send a request | | Accessibility | C | |
| `form-feedback` | | An empty submit shows no message | Accessibility | | B |
| `mobile-nav` | Links are hidden on phones with no working menu button | | Responsiveness | D | |

## What the browser does

- **Every shot:** set the viewport and theme, load the page, scroll through it slowly so lazy images and reveals fire, return to the top, measure, capture.
- **Dark theme:** uses the browser's dark preference. If the page does not change, it clicks a visible theme button. If there is none, that dark shot is dropped and the report says so.
- **Links:** requests each same-site link and clicks it. Links with log-out, delete, remove or unsubscribe in the address are never followed. External links are listed and never opened.
- **Forms:** submits each form empty, with every request other than GET and HEAD blocked, so nothing is really sent.
- **Not a local site:** links and forms are skipped unless the user asks with `--allow-remote`.
