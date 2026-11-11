# Signature section

One section on the page is built from scratch for this person. It is what visitors remember. Attempting it in one section only keeps a weak result small and replaceable.

## What it can be

It takes something true about this person and shows it in a form only they could have:

- real figures drawn to scale, or set side by side;
- a career or project history laid out by its real dates;
- a working piece of the thing they built, using real behaviour;
- a domain's own format, such as a score sheet, a schedule or a parts list, holding their real facts.

## Rules

1. Every value on it comes from `## facts` in `COPY.md`. A chart with invented data, or a mock dashboard, is a placeholder and is not allowed.
2. Use only tokens from `assets/kit/base/tokens.css`. Custom CSS is expected.
3. It works at 390, 768, 1024, 1440 and 1920. Rearrange it at small widths instead of shrinking it.
4. It is readable with JavaScript off.
5. Anything interactive works by keyboard, with a visible focus ring and 44px touch targets.
6. Under reduced motion it is a plain, complete version with no movement.
7. Anything tied to scrolling is the page's one scroll-linked element. Never pin the page or take over scrolling.
8. A chart or diagram has a text version: a real table, or a sentence with the same numbers.
9. No canvas or WebGL scene, and no animation running on its own for more than 5 seconds without a pause control.

Keep its files together, for example `signature.css`, and pass `audit.py` like the rest of the page.

## Recording it

`deal.py` lists it in `DESIGN.md` with `signature` and its fallback.

If two `visual-qa` rounds in a row leave a failure in this section, replace it with the fallback named in `DESIGN.md`, update `DESIGN.md` and say so in the report. A fallback of `none` means the section is removed.
