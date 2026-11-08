# Navigation

Height `--nav-height`. Uses `--container` and `--gutter`, so that it lines up with the page.

**Desktop:** the wordmark on the left, up to five links, one action on the right. Links are `--text-sm`, weight 500, `--space-6` apart.

**Sticky or fixed:** when fixed, add a background once the page has scrolled, and set `scroll-padding-top` to `--nav-height`. Use `--z-nav`. A fixed nav must never cover content.

| Variant | Use |
|---|---|
| Plain, in the page flow | Portfolios, content sites |
| Sticky bar | Most product sites |
| Centre links | Few links, balanced wordmark and action |
| No bar: links in the hero or footer | Very short sites, up to three links |

**Phone:** wordmark and one action stay. Links open from a clearly labelled Menu button into a full-screen sheet. With three links or fewer, show them directly instead. The sheet's links are `--text-h3`, one per row, and it closes on Escape and on choosing a link. The button uses `aria-expanded`.

Mark the current page with `aria-current="page"` and a visible change.

**Avoid:** a floating pill bar covering content. A hamburger menu on desktop. Dropdowns when plain links will do.
