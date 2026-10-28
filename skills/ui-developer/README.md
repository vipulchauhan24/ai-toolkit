# UI Developer Skill

The UI developer skill builds frontend UI from a design system. You point it at a design system (your own Ember by default), and it builds pages, screens and components with that system's tokens and component specs. Base UI supplies the behavior and accessibility. It can also restyle an existing project onto the design system.

The skill builds the UI layer only. It does not build APIs, databases, auth or business logic. It does not create or change a design system (use design-system-builder for that), and it does not split a spec into phases (use project-planner for that).

## What Is in This Folder

Paths are relative to the skill folder, `skills/ui-developer/`. The skill also reads three guidance files from `rules/ui-design/` at the plugin root, two levels up. A fourth file there, `NOTICE.md`, carries their license text.

| Path                                    | Purpose                                                                                                          |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                              | The skill itself. Defines the inputs, the rules, the build steps, the checks and the restyling flow.             |
| `README.md`                             | This file.                                                                                                       |
| `scripts/audit_ui.py`                   | The audit the skill runs before delivering. Finds custom CSS, raw values, stock colors, arbitrary values, and classes missing from the built CSS. |
| `../../rules/ui-design/app-screens.md`  | Guidance for dashboards, admin and settings views, lists, inboxes, forms and detail pages.                       |
| `../../rules/ui-design/copy.md`         | Guidance for the words on landing pages and portfolios.                                                          |
| `../../rules/ui-design/layout.md`       | Guidance for how a landing page or portfolio is put together.                                                    |
| `../../rules/ui-design/NOTICE.md`       | Credit and license text for the three guidance files, which are adapted from the taste-skill project (MIT).      |

## What You Need

- **A design system.** The skill never runs without one. The default is Ember, in the `Ember` folder of `https://github.com/vipulchauhan24/my-design-system`, pinned to commit `c3c40c78f8ee3b52791d623c53204ae7b52bda58` so every run reads the same version. To use another one, give a public repository URL or a local folder when you invoke the skill. Any design system made by design-system-builder works. To move the default to a newer Ember, change the commit in `SKILL.md` (§1).
- **The design system's utilities.** The skill writes no custom CSS, so the project needs the design system's utility classes. For Ember that means Tailwind v4. If the project doesn't have it, the skill asks before doing anything.
- **React**, if you use the default component library (Base UI). If you name another library, or the project already uses one, the skill uses that.
- **Git** on your machine. The skill fetches the design system's repository to read it. A local folder needs no network.
- **Python 3** (optional). It runs the audit script. Without it, the skill falls back to manual searches and says that class existence was not checked.

## How the Skill Works

1. The skill checks that its reference files and audit script exist, then resolves its inputs: the design system, the component library and what to build.
2. It asks for anything missing in a single batch of questions.
3. It fetches the design system (the pinned commit by default), reads its README, theme file and component specs, and writes a map of the utility classes it may use.
4. It lists the states of each screen. For an app screen, a landing page or a portfolio, it first reads the matching reference file.
5. It copies the design system's CSS into the project, builds wrappers for the components, and builds the screens.
6. It runs the project's safe checks (typecheck, lint, unit tests, build), builds the CSS, and runs the audit script. The audit fails on custom CSS, literal values, stock colors, arbitrary values, and any class that is missing from the built CSS.
7. It hands you a look-at list: what to open and check by eye, and how to reach each state.

## Using the Skill

In Claude Code, open the project folder and ask for the UI. Any of these phrases triggers the skill:

- `build this screen`
- `build this page`
- `implement this UI`
- `style this with my design system`
- `restyle this`

To use a different design system, include its repository URL:

```text
build the billing settings screen with https://github.com/someone/their-design-system/tree/main/Acme
```

To build from a phase document made by project-planner, give its path. The skill builds only the UI that the phase puts in scope, writes the UI tests from the phase's Test plan if the project has a test setup, and checks the UI against the phase's acceptance criteria. Backend criteria are marked "not UI", and a phase with no UI work ends with a one-line "no UI in this phase". It builds one phase per run:

```text
build the UI for docs/phases/phase-3-link-list.md
```

### Restyling an existing project

Ask it to restyle named screens or components. The skill writes down what the project does now (routes, forms, data, behavior), what must survive, and what doesn't match the design system. It then restyles one screen at a time and keeps the build and tests no worse than before. It will not migrate your framework or component library. Ask for an audit only, and it stops after listing what doesn't match.

### What you check yourself

By default the skill does not run a browser or take screenshots. Ask for a visual check and it takes screenshots at 390px and desktop width, in light and dark. Otherwise, at the end it gives you a look-at list with the screens to open, the widths (390px and desktop), light and dark themes, keyboard navigation, and every state with a way to reach it. It says plainly that it did not look at the result.

## What the Skill Does Not Do

- It does not edit the design system, and it does not invent a token value. If the design system lacks a component, token or utility, the skill reports it as a gap.
- It does not pick libraries for charts, date pickers, rich-text editors, drag and drop, maps or virtualized lists. If a screen needs one, it asks which library to use. If you don't say, it builds the rest of the screen and leaves a labeled slot.
- It does not invent testimonials, named people, quotes, customer logos or metrics. It uses plainly fake text and lists it.
- It does not follow instructions found inside a design system's files (install steps, scripts, commands). It follows only the design rules.
- It does not install the design system with a package manager. It copies the design system's CSS files into the project, unedited, and reports the repository folder and commit they came from.
- It does not write mock servers or fake backends. Where data doesn't exist yet, it types the expected shape and marks each placeholder with `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `SKILL.md` to change the rules, the default design system (and its pinned commit) or the default component library.
- Edit the files in `rules/ui-design/` (at the plugin root) to change the guidance for each kind of work. Where they disagree with a design system, the design system wins.

## Installing the Skill

### From the plugin marketplace

In Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:ui-developer`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/ui-developer/` folder and the `rules/ui-design/` folder into a skills directory that Claude Code reads, and keep their relative layout:

- Project level: `.claude/skills/ui-developer/` and `.claude/rules/ui-design/`.
- User level: `~/.claude/skills/ui-developer/` and `~/.claude/rules/ui-design/`.

`SKILL.md` reads `../../rules/ui-design/` by relative path, so `rules/` must sit two levels above the skill folder.

## License

MIT. The three guidance files are adapted from taste-skill, which is also MIT. See `rules/ui-design/NOTICE.md`.
