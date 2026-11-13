# Kit ownership (maintainers)

This page is for people who edit the toolkit. No skill loads it.

`design-md` and `ui-craft` both carry part of the kit, because each skill folder must work on its own. Files they share are listed in `scripts/shared_files.json`. The first path in each entry is the canonical copy: edit that one, then run `python3 scripts/check_shared_files.py --sync`. `python3 -I tests/run.py static` fails if the copies differ, or if two skills carry a file with the same name and different content that is neither shared nor listed under `_distinct_names`.

| Files | `design-md` | `ui-craft` | Why |
|---|---|---|---|
| `assets/kit/base/`, `effects/`, `motion/`, `media/`, `vendor/`, `VERSION` | yes | yes (shared) | Previews are real first screens, so `design-md` needs the same base, motion and media the build uses |
| `assets/kit/sections/hero/` | yes | yes (shared) | The three concepts differ in their hero, so `design-md` previews only the hero |
| `assets/kit/sections/<other>/`, `components/`, `layouts/`, `examples/react/` | no | yes | Only the build composes the rest of the page |
| `assets/data/` (combos, palettes, fonts, motion, site kinds) | yes | no | Choosing the look is `design-md`'s job. `ui-craft` reads the result from `DESIGN.md`, `design.json` and `design.css` |
| `scripts/contrast.py`, `audit.py` | yes (shared) | yes (shared) | Both check pairs and pages |
| `scripts/colors.py`, `deal.py`, `preview.py`, `sameness.py` | yes | no | Palette derivation and concept previews |
| `references/signature.md` | yes (canonical) | yes (shared) | Both need the rule for the one custom element. The text names no skill-specific path, so one copy serves both |
| `references/system/color.md` | yes | no | How combos and the user's colours become a palette |
| `references/system/palette.md` | no | yes | How the build uses a palette it did not choose. Different job, so a different file name |

When a kit file changes, edit the canonical copy and sync. When `design-md` needs another kit file, add it to `shared_files.json` instead of copying it by hand.
