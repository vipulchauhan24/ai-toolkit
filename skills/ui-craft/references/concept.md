# Concepts

Before any layout exists, propose three ideas for this page. An idea comes from the person's own material, so it can't be reused on someone else's site.

## Finding the material

Read `## facts` in `COPY.md`. Note what only this person has: the domain they work in, the things they measured, the shape of their career, an odd detail, the way they write. Those notes are the raw material. Their job title is not.

## What an idea is

An idea names a thing the page does or shows. It is never an adjective. "Clean and minimal", "bold and modern" and "dark, for developers" are moods, and any site can have them.

| Weak | Why | Stronger, for a person who built airline crew schedules |
|---|---|---|
| A terminal window for a developer | Fits every developer | The page reads as a departures board: each project is a flight, with its real figures in the columns |
| Big type and lots of white space | A mood, with no subject | One measured result fills the first screen, and the page explains how it was reached |

Each idea must pass this test: **swap in someone else from the same field. If the idea still works, it is too generic. Replace it.**

A page still has a job. The idea shapes the layout and the first impression, and a stranger must still see in seconds who this is and what to do next. Navigation labels stay plain. Nobody has to learn a metaphor to find the contact link. `COPY.md` does not change to suit an idea unless the user agrees.

## Three that differ

The three must differ in **first-screen layout, page structure and tone**. Three colour schemes on one layout count as one idea.

## CONCEPTS.md

Write this at the project root, one block per idea:

```
## A: <short name>

idea: <one sentence, naming the thing the page does>
facts: <the lines from ## facts that it draws on, word for word>
first screen: <what fills it, and what the eye lands on first>
structure: <section order, and what is left out>
mood: <palette, fonts and type contrast, and why they suit the facts>
signature: <the one section built from scratch, from signature.md>
fails on someone else because: <the fact it depends on>
```

## Concept files

For each idea, write `previews/a.json`, `b.json` or `c.json`. Every key except `name` is optional, and any key left out is picked at random. Read `assets/data/site-kinds.json`, `palettes.json` and `fonts.json` for the allowed values.

```json
{
  "name": "Departures board",
  "hero": "custom",
  "palette": "ochre",
  "fonts": "space-grotesk-ibm",
  "radius": "sharp",
  "motion": "standard",
  "type_contrast": "even",
  "backgrounds": "ruled",
  "headings": "side",
  "images": "natural",
  "parallax": null,
  "order": ["experience", "skills-stack", "about", "contact", "footer"],
  "sections": { "experience": "rows" },
  "signature": { "id": "flight-board", "after": "hero", "fallback": "projects/list-rows" }
}
```

- `hero` is a kit hero, or `custom` when the preview's hero is built for this idea.
- `order` leaves out the hero and the signature. It ends with `footer`, and `contact` comes after the middle sections. A section left out is dropped.
- `images` is `none` when the project has no images or portrait.
- `parallax` is `null`, `hero`, or a section with real images. It needs real images, motion above `quiet`, and no timeline on the page.
- `signature.fallback` is the kit variant used if the signature fails. It must not already be in `order`. Use `none` only when the signature's facts also appear elsewhere on the page.

The script fails with a reason if an idea asks for something the project has no material for. Fix the idea and do not invent the material.

## Previews

A preview shows one idea's first screen, as a real page: `previews/a.html`, `b.html` and `c.html`.

1. Copy the kit's base styles, once: `cp -r <this-skill-folder>/assets/kit/base previews/base`.
2. Deal each idea into its own folder, so that its colours are real. Add `--force` when redoing one:

   ```bash
   python3 -I <this-skill-folder>/scripts/deal.py --kind portfolio --has <material> --concept previews/a.json --out previews/a --no-history
   ```

3. Write the HTML. Link `base/tokens.css`, `a/design.css`, `base/reset.css`, `base/base.css`, `base/direction.css` and `base/utilities.css`, in that order. Add your own `<style>` using only tokens. Set the attributes from `a/DESIGN.md` on `html`.

Each preview:

- is the navigation and the hero, and nothing below it;
- uses real words from `COPY.md` and real images only;
- reads kit samples for technique, and is composed for the idea;
- has no animation, so that its screenshot is honest;
- works at 390px wide, has one `h1`, and passes `audit.py`.

If the project has npm, install the fonts into `previews/` and link them. Otherwise say that the previews show fallback fonts.

Then take the screenshots:

```bash
python3 -I <this-skill-folder>/scripts/preview.py --dir previews --names a,b,c
```

If the script can't open a browser, carry on, and give the paths of the HTML files for the user to open.

## Choosing

Show the user the three ideas in a few lines each, with the screenshot paths. They can choose one, mix them or ask for changes. Redo only what they changed, for at most two rounds.

In a non-interactive run, choose the idea that depends most on the person's own facts, and say why in the report.

Add `## chosen` to `CONCEPTS.md` with the letter and any changes, and write the final concept to `concept.json` at the project root. The chosen preview's markup becomes the page's hero. `previews/` can be deleted after the build.
