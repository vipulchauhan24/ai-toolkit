# AI Toolkit

A collection of Claude Code skills by Vipul Chauhan.

## Skills

| Skill                                                                                       | How to use it                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [design-system-builder](docs/skills/design-system-builder.md) | Ask Claude to "create a design system" and give it a product brief, screenshots, a brand palette, or a mix. It confirms a direction with you, then writes tokens, light and dark themes, component specs, and a contrast report. |
| [project-planner](docs/skills/project-planner.md)                                                 | Write a spec with `skills/project-planner/assets/spec-template.md`, then ask Claude to "plan this project" using that file. It asks about high-stakes decisions and splits the spec into phases that a coding agent builds one at a time.   |
| [doc-trimmer](docs/skills/doc-trimmer.md) | Ask Claude to "trim this" or "cut the noise" and give it pasted text, a file path, or a URL. It removes hedging, throat-clearing, padding, filler and repeated ideas, and keeps your facts, voice and structure. For a file it writes a `-cut` copy next to the original (`post.md` becomes `post-cut.md`) and never touches the original. It does not summarise or rewrite, and it leaves legal text, specs and fiction alone. |
| [ui-developer](docs/skills/ui-developer.md) | Ask Claude to "build this screen" or "restyle this". It builds the UI, or restyles existing UI, from a design system (Ember by default, or one you name) using only its tokens and utilities. It writes no custom CSS, builds the UI layer only (no APIs, databases or auth), runs an audit for raw values and unknown classes, and hands you a look-at list for each state. |
| [doc-reviewer](docs/skills/doc-reviewer.md) | Ask Claude to "poke holes in this" or "what could go wrong with this design" and give it pasted text, a file path, or a URL. It attacks the document and reports only holes: failure modes, unstated assumptions, skipped steps and unanswered questions, ranked `fatal`, `serious` or `sleeper`. Each finding quotes the text and ends with a question for the author. It gives no praise and no fixes, and it does not review code. |
| [frontend-react](docs/skills/frontend-react.md) | Ask Claude to "build this in React", "build this in Next.js" or "write this React component". It writes React and Next.js code to a fixed set of rules (components, hooks, state, effects, forms, performance, a typed data boundary, server and client components, tests), matches the project's own conventions first, and runs the typecheck, lint, tests, build and a React check script. It does not choose colors or component looks: name ui-developer too for that. It builds no APIs, databases or auth. |

## Installing

The design-system-builder, project-planner, doc-trimmer, doc-reviewer, ui-developer and frontend-react skills are published in the ai-toolkit Claude Code plugin. Add the marketplace and install it:

```text
claude plugin marketplace add vipulchauhan24/ai-toolkit
claude plugin install ai-toolkit@product-development
claude plugin update ai-toolkit@product-development
/reload-plugins
```

Invoke the skills with `/ai-toolkit:design-system-builder`, `/ai-toolkit:project-planner`, `/ai-toolkit:doc-trimmer`, `/ai-toolkit:doc-reviewer`, `/ai-toolkit:ui-developer` and `/ai-toolkit:frontend-react`, or let Claude pick them up from a matching prompt.

## Using the skills with other providers

Each skill is a self-contained folder: a `SKILL.md` (the open Agent Skills format) plus its own `references/`, `scripts/` and `assets/`. Nothing is read from outside the folder, so you can copy or zip a single skill folder on its own. The skills live in `skills/`.

```bash
git clone https://github.com/vipulchauhan24/ai-toolkit.git
cd ai-toolkit/skills
```

### Other agents that support `SKILL.md`

Cursor, GitHub Copilot, opencode and similar tools load the same folder format from their own skills directory. Copy the skill folders there; see each tool's docs for the path.

### Chat apps and APIs without skill support

Chat apps and raw API calls have no skills loader, so supply the files yourself:

1. Paste the contents of `SKILL.md` as the system prompt, custom instructions, or the first message.
2. Attach the files the skill points to, from its folder:
   - project-planner: `references/project-planner-rules.md`, `references/markdown-rules.md`, `references/architecture-patterns.md`, and `assets/spec-template.md`
   - doc-trimmer: `references/markdown-rules.md`
   - design-system-builder: `references/tokens.example.css`
   - doc-reviewer: none, `SKILL.md` is enough
   - ui-developer: `references/app-screens.md`, `copy.md` and `layout.md`, `scripts/audit_ui.py`, and `references/phase-document.md` and `references/restyle.md` when needed
   - frontend-react: `references/react-rules.md`, `references/architecture-patterns.md`, `references/nextjs-rules.md` (Next.js only), `references/react-performance-guidelines.md` (performance work only) and `scripts/check_react.py`
3. Send your request (a spec to plan, a brief, screenshots or palette to build from, text to trim, or a document to review).

### What to expect outside Claude Code

- design-system-builder ends by running `./scripts/check_contrast.sh <theme-name>` and `python3 -I scripts/build_tokens_json.py <theme-name>`. This needs an agent with shell access and Python. In a plain chat, run the scripts yourself on the generated folder, or the contrast check is skipped and `tokens.json` is not generated.
- doc-trimmer fetches URLs with `curl` and writes the `-cut` file, so both need an agent with shell and file access. In a plain chat, paste the text and copy the result yourself.
- doc-reviewer fetches URLs with `curl` and reads files, so it needs an agent with shell and file access for those inputs. In a plain chat, paste the document text.
- Screenshot mode needs a model that accepts image input.
- frontend-react runs the project's own typecheck, lint, tests and build and `scripts/check_react.py` with Python 3, so it needs an agent with shell access. Python 3 is required: without it the skill stops with an error.
- ui-developer fetches the design system with `git` and runs `scripts/audit_ui.py` with Python 3, so it needs an agent with shell access. Without Python it falls back to manual searches.
- The `/ai-toolkit:...` commands are Claude Code only. Elsewhere, trigger the skills with a prompt.

## Repository Layout

The repository root is the `ai-toolkit` plugin.

| Path              | Contents                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/` | The marketplace manifest (`marketplace.json`) and the plugin manifest (`plugin.json`).                         |
| `skills/`         | One self-contained folder per skill: `SKILL.md`, plus `references/`, `scripts/` and `assets/` where needed.   |
| `agents/`         | `skill-runner`, a generic subagent that runs named skills in its own context and writes a report file.         |
| `docs/skills/`    | One guide per skill for human readers (usage, examples, customizing). Skills do not read these.                |
| `scripts/`        | Repository tooling. `shared_files.json` lists every file copied into several skills. `check_shared_files.py` fails if a copy has drifted, and `--sync` copies the canonical file over the others.      |

Files used by more than one skill are copied into each skill folder, and `scripts/shared_files.json` lists them (for example `markdown-rules.md` and `architecture-patterns.md`). The first path in each entry is the canonical copy. Edit it, run `python3 scripts/check_shared_files.py --sync`, then run the script without `--sync` to confirm.

## License

MIT. See [LICENSE](LICENSE).
