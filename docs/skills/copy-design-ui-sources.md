# ui-craft, copy-writer and design-md: sources and decisions

For whoever maintains these three skills. `ui-craft` was split in November 2026: `copy-writer` owns `COPY.md` and the copy rules, `design-md` owns the direction and `DESIGN.md`, and `ui-craft` builds the page. The tables below keep their old headings, and each source belongs to the skill named in its row's section. The skill never reads this file, and agents do not need these links while working.

**How each source was read**

- **Direct:** the full text was read.
- **Fetched:** the page was opened through a tool that summarises it, so check exact wording before quoting.
- **Snippet:** only a search result excerpt was seen. Open the page before relying on it.

**Strength**

- **Primary:** research, or the owner's own documentation.
- **Practitioner:** experienced opinion, usually consistent across sources, but not tested.

## Copy files

| Source | Used for | Read | Strength |
|---|---|---|---|
| [NN/g: How users read on the web](https://www.nngroup.com/articles/how-users-read-on-the-web/) | 79% scan, 16% read word by word, 124% better usability, promotional language as a burden. Study from 1997 | Fetched, figures confirmed | Primary, old |
| [NN/g: Legibility, readability and comprehension](https://www.nngroup.com/articles/legibility-readability-comprehension/) | About 28% of words read, reading levels, active voice, front-loading | Fetched | Primary |
| [NN/g: The 3 Cs of microcopy](https://www.nngroup.com/articles/3-cs-microcopy/) | Clarity, then concision, then character | Fetched | Primary |
| [NN/g: Error-message guidelines](https://www.nngroup.com/articles/error-message-guidelines/) | Error placement, wording, tone, keeping input | Fetched | Primary |
| [NN/g: Designing empty states](https://www.nngroup.com/articles/empty-state-interface-design/) | Empty-state content | Fetched | Primary |
| [NN/g: 5 steps to a UX-design portfolio](https://www.nngroup.com/articles/ux-design-portfolios/) | Survey of 204 hiring professionals, case-study contents. About UX portfolios; applying it to engineers is an inference | Fetched | Primary |
| [NN/g: Formatting long-form content](https://www.nngroup.com/articles/formatting-long-form-content/) | Descriptive headings and scannable long text. It does not state "one idea per paragraph" | Fetched | Primary |
| [Mailchimp: Voice and tone](https://styleguide.mailchimp.com/voice-and-tone/) | Voice versus tone | Fetched | Primary |
| [Vercel web interface guidelines](https://github.com/vercel-labs/web-interface-guidelines) | Typography marks, button labels, loading text, tabular numbers, `Intl` | Fetched | Primary |
| [Diátaxis](https://diataxis.fr/how-to-guides/) | The four documentation kinds, writing a how-to | Fetched | Primary |
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | Writing tells, title case, what is not a tell. About encyclopedia text. The last 44,700 characters were not read | Fetched | Primary, dates quickly |
| [taste-skill](https://github.com/Leonxlnx/taste-skill) | Fact sheet, counting habits, over-correction | Direct | Practitioner |
| Copy rules of an earlier skill in this repository, since removed | Argument-first method, headline budget idea. Adapted from taste-skill | Direct | Practitioner |
| [linear.app](https://linear.app/), [stripe.com](https://stripe.com/) | Real headlines, sentence case, proof, November 2026 | Fetched | Observation |
| [brittanychiang.com](https://brittanychiang.com/) | Portfolio structure, and a test for false alarms in `check_copy.py` | Fetched | Observation |
| [NN/g: Writing, snippets on one idea per paragraph](https://www.nngroup.com/articles/applying-writing-guidelines-web-pages/) | One idea per paragraph, as reported in a search result | Snippet | Check |
| [Scrimba](https://scrimba.com/articles/how-to-build-a-web-developer-portfolio-that-gets-you-hired) | Developer portfolios | Snippet | Practitioner |
| [Leadfeeder](https://www.leadfeeder.com/blog/saas-landing-pages-that-convert/), [Userpilot](https://userpilot.com/blog/saas-landing-pages/) | SaaS sections as visitor questions. No controlled study of section order was found | Snippet | Practitioner |
| [Baymard product page research](https://baymard.com/research/product-page) | Product pages commonly fail on usability. Detailed guidelines are paywalled and were not checked | Snippet | Primary, partial |
| [Webtonic](https://www.webtonic.io/blog/best-copywriting-agencies-birmingham) | Agency process and the debate over publishing prices | Snippet | Practitioner |
| [BentoBox](https://getbento.com/blog/restaurant-website-most-important-pages), [Web Designer Depot](https://www.webdesignerdepot.com/2012/06/essential-advice-for-restaurant-websites/) | What restaurant visitors look for, menus as HTML | Snippet | Practitioner |
| [Clutch](https://clutch.co/visualobjects/web-design/blog/event-landing-pages) | Event page essentials | Snippet | Practitioner |
| [GetResponse](https://www.getresponse.com/blog/waitlist-landing-page), [Moosend](https://moosend.com/?p=67875) | Waitlist page content | Snippet | Practitioner |

## System, components and sections

| Source | Used for | Read | Strength |
|---|---|---|---|
| [WCAG 2.2: Target size (minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | 24px minimum target (AA) | Fetched | Primary |
| [WCAG 2.2: Contrast (minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | 4.5:1 and 3:1, what counts as large text | Fetched | Primary |
| [WCAG 2.2: Non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) | 3:1 for controls and meaningful graphics | Fetched | Primary |
| [WCAG 2.2: Focus appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html) | 2px, 3:1 focus ring. This is AAA, adopted here as the target | Fetched | Primary |
| [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/) | Which widget patterns exist. Individual pattern pages were not read | Fetched index only | Primary |
| [NN/g: Designing effective carousels](https://www.nngroup.com/articles/designing-effective-carousels/) | Carousel limits, no autoplay on mobile | Fetched | Primary |
| [NN/g: Accordions on desktop](https://www.nngroup.com/articles/accordions-on-desktop/) | When accordions help and hurt | Fetched | Primary |
| [NN/g: Mobile navigation patterns](https://www.nngroup.com/articles/mobile-navigation-patterns/) | Visible navigation for few links, hidden menus are least discoverable | Fetched | Primary |
| [Practical Typography: Line length](https://practicaltypography.com/line-length.html) | 45 to 90 characters | Fetched | Practitioner, respected |
| [Vercel web interface guidelines](https://github.com/vercel-labs/web-interface-guidelines) | Focus, scroll margin, touch, safe areas, hover, images | Fetched | Primary |
| App-screen rules of an earlier skill in this repository, since removed | Ranges for sidebars, rows, type and colour on app screens, from its study of 23 real product screens. Adapted from taste-skill. Rewritten here | Direct | Practitioner, measured |

The 44px touch target is a common platform convention. Apple's guideline page and Material's window-size page could not be loaded, so it is not confirmed from them. WCAG's own minimum is 24px.

### Measurements of real sites

Measured in a browser in November 2026, at 1440 and 390 wide, on 12 product sites: Linear, Stripe, Vercel, Raycast, Notion, Figma, Framer, Resend, Supabase, React, Tailwind and Apple. Each cell is the median, then the range. The script takes the most common or median value on one page, so treat these as approximate. Portfolios were measured too (Brittany Chiang, Lee Robinson, Rauno, Paco): their headings run much smaller, from 16 to 48px, and pages are shorter.

| Measure | At 1440 | At 390 |
|---|---|---|
| h1 size | 60.0 (34 to 96) | 36.0 (34 to 64) |
| h2 size | 44.0 (20 to 56) | 32 (22 to 48) |
| paragraph size | 15 (13 to 21) | 15 (14 to 18) |
| paragraph line height | 1.4 (1.2 to 2) | 1.5 (1.2 to 2) |
| nav height | 64.0 (44 to 78.4) | 64.5 (64 to 72) |
| button height | 40.0 (34 to 48) | 39.0 (28 to 47.4) |
| button radius | 8.0 (4 to 16) | 8 (4 to 16) |
| button text | 16.0 (12 to 17) | 15.5 (12 to 17) |
| card radius | 12.0 (6 to 18) | 16 (6 to 21.3) |
| grid gap | 16.0 (8 to 48) | 16.0 (8 to 48) |
| gap above h2 | 227.8 (16 to 446) | 125.5 (16 to 400) |
| main left margin | 104 (40 to 104) | 24.0 (16 to 192) |

How these became tokens: `--text-h1` (36 to 64px), `--text-h2` (28 to 44px), `--nav-height` (64px), `--control-md` (40px), soft radius (12px on cards), `--section` (64 to 120px each side, so about 128 to 240px between sections) and `--gutter` (24px on phones).

Real sites often use buttons under 44px on phones. This skill sets 44px on touch anyway, for usability.

## Motion

| Source | Used for | Read | Strength |
|---|---|---|---|
| [NN/g: Animation duration](https://www.nngroup.com/articles/animation-duration/) | 100ms feedback, 200 to 300ms for screen changes, 400ms upper limit, exits shorter than entrances, ease-out to enter | Fetched | Primary |
| [NN/g: Animation purpose](https://www.nngroup.com/articles/animation-purpose-ux/) | When motion helps, and warnings about overuse | Fetched | Primary |
| [WCAG 2.2: Pause, stop, hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | Controls for motion over 5 seconds (A) | Fetched | Primary |
| [WCAG 2.2: Animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | Reduced motion (AAA, adopted here) | Fetched | Primary |
| [web.dev: Animations guide](https://web.dev/articles/animations-guide) | Animate transform and opacity, `will-change` sparingly | Fetched | Primary |
| [Motion docs: animate](https://motion.dev/docs/animate), [inView](https://motion.dev/docs/inview), [scroll](https://motion.dev/docs/scroll), [React accessibility](https://motion.dev/docs/react-accessibility) | The APIs and sizes used | Fetched | Primary |

Material 3's motion pages could not be loaded, so their tokens are not used. Stagger amounts (50ms, 60ms) and reveal distance (16px) are working defaults.

`assets/kit/vendor/motion.js` is built from `motion` 14.10.1 with esbuild, exporting `animate` from `motion/mini` and `inView`, `scroll` and `stagger` from `motion` (about 8KB gzipped). Tabler icons are pinned at v3.50.0.

## Colour combos

`assets/data/combos.json` holds 24 combos, written for this skill, tagged by site kind and audience. They follow conventions common to editorial, product and local-business sites: a near-black text colour with a slightly warm or cool off-white, one saturated action colour, and in larger combos a pale band colour and a highlight. Every combo is generated into `palettes.json` by `scripts/colors.py`, which fails the build if any pair misses WCAG 2.2 AA in light or dark.

Rules the derivation follows, and where they come from:

- Contrast minimums: WCAG 2.2, 1.4.3 (text, 4.5:1, or 3:1 at 18.66px bold and 24px), and 1.4.11 (controls, 3:1).
- Shades are mixed in OKLab and kept in sRGB by lowering chroma, as CSS Color 4 does when it maps a colour into the gamut.
- Label colour by hue: yellows, ambers and limes carry dark labels. This is a design convention, not a standard.
- Links that fail as text become ink with an underline in the action colour, so the colour still shows without failing 1.4.3.

Found in the first portfolio test (2026-11-11): white on `#D9541E` is 4.01:1, so a brand orange with white labels fails AA. The skill now offers the nearest passing shade, large bold labels, the other label, or keeping it, and never swaps silently.

## Working defaults

These are judgement calls, with no research behind them. Change them freely:

- Length budgets, such as a supporting line of about 25 words and two lines for a headline.
- The section tables in each kind file.
- The word lists and per-page allowances in `scripts/check_copy.py`. They date quickly as models change, so review them.
- Dialog and label patterns in `copy-app.md`.
- What follows a sign-up, and who should attend, in `copy-event.md`.
- `copy-ecommerce.md`, beyond the general points above.
- The spacing relationships, component padding and sizes that are not in the measurement table.
- The variant lists in `sections/`, and which variant suits what.
- The radius families.
- The 24 combos, their audience tags, and the 0.68 lightness line for light or dark labels.

## Decisions

- **Sentence case, against Vercel.** Vercel's guidelines ask for Title Case on headings and buttons. This skill uses sentence case, because Linear and Stripe do, and Wikipedia lists title case among signs of AI writing. The live Vercel review step must skip that one rule.
- **Curly quotes, despite Wikipedia.** Wikipedia lists them as a sign of AI writing in its plain-text articles. On a web page they are correct.
- **Sources stay out of the skill.** Working files hold rules only, because they load on every run and links invite agents to fetch outside content.

## DESIGN.md format (design-md)

| Source | Used for | Read | Strength |
|---|---|---|---|
| [google-labs-code/design.md, docs/spec.md](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) | The format `deal.py` writes: YAML front matter tokens (`colors`, `typography`, `rounded`, `spacing`, `components`), section order, reference syntax, consumer behaviour for unknown content. Version `alpha`, Apache-2.0 | Direct, full text | Primary, alpha: expect changes |
| [Stitch DESIGN.md overview](https://stitch.google.com/docs/design-md/overview/) | The page the owner pointed to. It renders only a script shell, so nothing was read from it | Not read | n/a |
| Search results on the `@google/design.md` CLI (lint, diff, export to Tailwind and DTCG) | The optional lint step. The CLI was not run during the split, because running a downloaded package was refused | Snippet | Check before relying on it |

Decisions:

- Dark values are `colors` entries ending in `-dark`, because the format has no mode concept. Our extra sections (Sections, Motion, Responsive) follow Do's and Don'ts, because the format keeps unknown sections.
- The kit's base, motion, vendor, media, effects and hero files exist in both `ui-craft` and `design-md` (previews need them). `scripts/shared_files.json` keeps the copies identical. `check_copy.py`, `contrast.py` and `audit.py` are shared the same way.
- Ideas taken from the earlier `design-system-builder` skill, since removed: screenshots, logos and unopenable links as inputs, never changing a brand colour silently, and deriving missing neutrals and status colours and saying so. Its three-layer CSS tokens, Tailwind preset and `tokens.json` export were not carried over: the format's own CLI exports to Tailwind and DTCG.

