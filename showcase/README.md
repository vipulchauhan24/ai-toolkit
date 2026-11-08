# ui-craft showcase

A maintainer's tool that shows every kit component and section in a real browser. It is not part of the skill and does not ship with it.

Serve the repository root, then open the app:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/showcase/>. The left and right arrow keys move between items.

The sidebar lists every item. The toolbar sets theme, light or dark, width, density, reduced motion, long content, and the `DESIGN.md` options. The address holds the view, so it can be shared. "Open alone" opens the render page by itself.

## After changing the kit

| Command | What it does |
|---|---|
| `python3 -I showcase/build_showcase.py --write` | Rewrites `manifest.json` from the kit, after adding or removing an item |
| `python3 -I showcase/build_showcase.py --sheets` | Rewrites the kit's contact sheets |
| `python3 -I showcase/build_showcase.py` | Checks the manifest, themes, fonts and sheets |
| `python3 -I showcase/build_showcase.py --verify` | Loads every item in a browser and reports errors |
| `python3 -I showcase/build_showcase.py --verify --full` | Does that in every theme, mode and width (about 15 minutes) |

The items under "Signature examples" show what a from-scratch section can look like. They are kept out of the skill so that builds do not copy them.

The fonts in `fonts/` are latin subsets from Fontsource, under the SIL Open Font License.
