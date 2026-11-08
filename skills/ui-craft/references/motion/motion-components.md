# Motion for components

One rule per component. Each one stops under reduced motion unless it says otherwise.

| Component | Motion | How |
|---|---|---|
| Button | Hover: tone change. Press: scale to 0.98 | CSS, `--duration-hover`, `--duration-press` |
| Link | Underline thickens, or draws in for nav links | CSS, `--duration-hover` |
| Card, linked | Border or background change, image zooms to 1.03 inside its frame | CSS, `--duration-hover`, image over `--duration-reveal` |
| Nav | Gains its background after 8px of scroll | Class toggle, CSS `--duration-enter` |
| Nav, phone sheet | Fades in, links rise and stagger by 30ms. Closing is faster, with no stagger | Motion, `--duration-enter`, `--duration-exit` |
| Footer | None | |
| Form field | Border and ring fade on focus. Error fades in and drops 4px. Success tick draws | CSS |
| Badge | None | |
| Tabs | Indicator slides. Panel cross-fades | Motion spring with no bounce, or CSS |
| Accordion | Height opens with `interpolate-size`, where supported, and otherwise snaps. Chevron rotates | CSS, `--duration-enter` |
| Carousel | Native scroll-snap. Never autoplays | CSS |
| Modal | Backdrop fades. Panel rises 8px and fades | CSS or Motion, `--duration-enter`, `--duration-exit` |
| Tooltip | Fades in after a 300ms hover delay, immediately on focus | CSS |
| Toast | Slides in from the edge. Timer pauses on hover | Motion spring with no bounce |
| Table | Row hover: background only. A new row fades in once | CSS |
| Stat | Counts up once on entering view, ending on the exact value. Only for numbers that make sense counted | `data-count` helper |
| Logo row | Slow marquee if there are enough logos, pausing on hover | CSS |
| Testimonial | None beyond the section reveal | |
| Pricing table | Monthly and yearly: indicator slides, prices cross-fade | CSS |
| Timeline | The line draws with scroll progress | `data-timeline` helper |
| Code block | The copy icon swaps to a tick for 1.5s | CSS |
| Avatar | None | |
| Empty state | None | |
| Skeleton | Slow 1.5s shimmer. Static under reduced motion | CSS |
| Theme toggle | Icon cross-fades | CSS |
| Dropdown | Fades and scales from 0.96, from its anchor | CSS, `--duration-enter` |
| Icon | None on its own. An arrow in a button may move 2px on hover | CSS |
