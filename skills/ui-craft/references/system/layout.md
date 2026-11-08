# Layout

## The frame

Every page is built on one frame:

- A centred container, with `margin-inline: auto` and `max-width: var(--container)`.
- `padding-inline: var(--gutter)` on the same element or its wrapper.
- Left and right margins are equal at every width. The check in visual-qa fails a page when they differ by more than 8px or 2% of the width.
- Navigation and footer use the same container and the same margins as the content.

A background colour or image may run the full width. The content inside it stays in the container.

Do not leave a max-width on an element without centring it: that is the most common cause of a page that sits to the left.

## Alignment

- One left edge runs from the nav to the footer. Every block starts on it or on a column line.
- Pick one text alignment per section. Left-aligned is the default, and centred is for a short heading group with nothing else beside it.
- Never centre paragraphs over three lines.
- In a row of cards, tops and bottoms line up. Balance the content, or align buttons to the bottom.

## Hierarchy on a screen

Each screen has one thing to look at first. Make it clearly bigger, heavier or more contrasting than everything else. If you squint and can't find it, there isn't one.

## Section rhythm

A page reads as a sequence, so neighbours should differ:

- No two neighbouring sections use the same shape.
- If the same shape appears three times, the page looks like a template. The exception is real archives such as a project list or a menu.
- Alternate dense and open, image and text.
- Changing the background between sections is optional. Use at most two section backgrounds.
- Use cards only when items are separate objects. Text does not need a box to be a section.

## Empty space

Space is good when something closes it, and it is a hole when nothing does.

| Good | Hole |
|---|---|
| Wide margins around a focused block | Text in one half and nothing in the other |
| A large image with text docked at its edge | A gap of more than half a screen between sections |
| One statement alone on a screen, once per page | A short block stretched to fill the screen |

- If text takes one side of a section, something belongs on the other: an image, a list, a figure, or the text moves to the centre.
- Size a section to its content. Use `min-height: 100vh` only for a section that really fills it.
- When a section looks empty, make the main element bigger or remove the section. Adding decoration does not help.
- visual-qa warns on a band of plain background over 60% of a screen, and fails over one screen.

## Heights of a screen

The hero's main message and main button are visible without scrolling at 1440x900 and at 390x844. Nothing important is cut by the fold.

## Expressive layouts

Off-centre anchors, overlapping elements, oversized type running to the edges, and deliberate asymmetry all need something large to balance them, such as a strong image, object or word.

Use them only when `DESIGN.md` sets `layout: expressive` and the page has that material. Equal outer margins still hold. A résumé-style page with no images always uses the default layout.
