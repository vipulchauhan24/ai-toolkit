# Motion for sections

One rule per section. The kit marks these with attributes:

| Attribute | Effect |
|---|---|
| `data-enter` with `style="--_i: n"` | Hero entrance, by order `n`, starting at 0 |
| `data-reveal` | Reveals once on entering view |
| `data-reveal-group` | On a parent: its children reveal in turn |
| `data-count` | A number counts up to its value |
| `data-timeline` | The line draws with scroll |
| `data-nav` | Nav background and phone sheet |
| `data-parallax` | On an image's frame: the image drifts with scroll |

| Section | Motion |
|---|---|
| Hero | `data-enter` on the headline, supporting line, buttons and media. Nothing else on load |
| Proof and stats | `data-reveal`, and `data-count` on numbers where counting adds something |
| Logos | Static, or a slow marquee |
| Features | `data-reveal-group`. Bento may add one pointer spotlight, on technical sites only |
| How it works | `data-reveal-group`. A line connecting the steps may draw with scroll |
| Projects | `data-reveal-group`, and image zoom on hover |
| Case study | Heading group has `data-enter`. Body has none, because people are reading |
| Experience | `data-reveal` on each entry. Timeline variant uses `data-timeline` |
| Skills and stack | `data-reveal` on the section only |
| Testimonials | `data-reveal` |
| Pricing | `data-reveal`. Keep prices steady, with no counting |
| FAQ | Accordion only |
| Closing call to action | `data-reveal`. An optional slow background drift, 20 seconds or more, with a pause control |
| Contact | `data-reveal` on the section. Form states from `motion-components.md` |
| Footer | None |
| About | `data-reveal` |
| Blog index | `data-reveal-group`, first screen excluded |
| Article | None while reading. An optional thin progress bar |
| Docs | None. The contents highlight follows the section |
| Gallery | `data-reveal-group`, and image zoom on hover |
| Menu and hours | None |
| Schedule | None |
| Product detail | Image cross-fades when a variant changes |
| Waitlist | Hero entrance. The form cross-fades to its success message |

Between pages: a cross-fade with the View Transitions API on multi-page and Next.js sites, if it is available.

## Parallax

The frame gets the attribute, and holds only the image: `<div class="frame" data-parallax><img ...></div>`. See `assets/kit/effects/parallax.html`.

- Images and backgrounds only, never text.
- Only where `DESIGN.md` notes it, and only with a real image.
- At most one per page. It is the page's one scroll-linked element, so it never shares a page with `data-timeline`.
- The helper moves the image 8% of the frame's height in total, scaled up enough that no edge shows. Do not increase either number.
- It does nothing under reduced motion, and stays still below 768px.

## Optional effects

At most one per page, for technical sites and portfolios, from `assets/kit/effects/`. They are static or very slow, and never sit behind body text at a level that lowers contrast.
