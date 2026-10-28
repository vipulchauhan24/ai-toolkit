# AI Toolkit

A collection of Claude Code skills by Vipul Chauhan.

## Skills

| Skill                                                                                       | How to use it                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [design-system-builder](skills/design-system-builder/README.md) | Ask Claude to "create a design system" and give it a product brief, screenshots, a brand palette, or a mix. It confirms a direction with you, then writes tokens, light and dark themes, component specs, and a contrast report. |
| [project-planner](skills/project-planner/README.md)                                                 | Write a spec with `templates/spec-template.md`, then ask Claude to "plan this project" using that file. It asks about high-stakes decisions and splits the spec into phases that a coding agent builds one at a time.   |
| [doc-trimmer](skills/doc-trimmer/README.md) | Ask Claude to "trim this" or "cut the noise" and give it pasted text, a file path, or a URL. It removes hedging, throat-clearing, padding, filler and repeated ideas, and keeps your facts, voice and structure. For a file it writes a `-cut` copy next to the original (`post.md` becomes `post-cut.md`) and never touches the original. It does not summarise or rewrite, and it leaves legal text, specs and fiction alone. |
| [ui-developer](skills/ui-developer/README.md) | Ask Claude to "build this screen" or "restyle this". It builds the UI, or restyles existing UI, from a design system (Ember by default, or one you name) using only its tokens and utilities, with Base UI for behavior and accessibility. It writes no custom CSS, builds the UI layer only (no APIs, databases or auth), runs an audit for raw values and unknown classes, and hands you a look-at list for each state. |
| [doc-reviewer](skills/doc-reviewer/README.md) | Ask Claude to "poke holes in this" or "what could go wrong with this design" and give it pasted text, a file path, or a URL. It attacks the document and reports only holes: failure modes, unstated assumptions, skipped steps and unanswered questions, ranked `fatal`, `serious` or `sleeper`. Each finding quotes the text and ends with a question for the author. It gives no praise and no fixes, and it does not review code. |

## Installing

The design-system-builder, project-planner, doc-trimmer, doc-reviewer and ui-developer skills are published in the ai-toolkit Claude Code plugin. Add the marketplace and install it:

```text
claude plugin marketplace add vipulchauhan24/ai-toolkit
claude plugin install ai-toolkit@product-development
claude plugin update ai-toolkit@product-development
/reload-plugins
```

Invoke the skills with `/ai-toolkit:design-system-builder`, `/ai-toolkit:project-planner`, `/ai-toolkit:doc-trimmer`, `/ai-toolkit:doc-reviewer` and `/ai-toolkit:ui-developer`, or let Claude pick them up from a matching prompt.

## Using the skills with other providers

Each skill is a folder with a `SKILL.md` (the open Agent Skills format) plus the files it references, so it is not tied to Claude. Always copy the whole folder, not just `SKILL.md`, because the skill reads sibling files by relative path (`references/`, `scripts/`) and shared files from the repository's top-level `rules/` and `templates/` folders, which sit two levels above the skill folder. project-planner and doc-trimmer need `rules/shared/`, ui-developer needs `rules/ui-design/`, and project-planner also needs `templates/`. Copy those too and keep the relative layout. The skills live in `skills/`.

```bash
git clone https://github.com/vipulchauhan24/ai-toolkit.git
cd ai-toolkit/skills
```

### Other agents that support `SKILL.md`

Cursor, GitHub Copilot, opencode and similar tools load the same folder format from their own skills directory. Copy the skill folders there; see each tool's docs for the path.

### Chat apps and APIs without skill support

Chat apps and raw API calls have no skills loader, so supply the files yourself:

1. Paste the contents of `SKILL.md` as the system prompt, custom instructions, or the first message.
2. Attach the files the skill points to:
   - project-planner: `rules/shared/project-planner-rules.md`, `rules/shared/markdown-rules.md`, and `templates/spec-template.md`
   - doc-trimmer: `rules/shared/markdown-rules.md`
   - design-system-builder: `references/tokens.example.css`
   - doc-reviewer: none, `SKILL.md` is enough
   - ui-developer: `rules/ui-design/app-screens.md`, `copy.md` and `layout.md`, and `scripts/audit_ui.py`
3. Send your request (a spec to plan, a brief, screenshots or palette to build from, text to trim, or a document to review).

### What to expect outside Claude Code

- design-system-builder ends by running `./scripts/check-contrast.sh <theme-name>` and `python3 -I scripts/build_tokens_json.py <theme-name>`. This needs an agent with shell access and Python. In a plain chat, run the scripts yourself on the generated folder, or the contrast check is skipped and `tokens.json` is not generated.
- doc-trimmer fetches URLs with `curl` and writes the `-cut` file, so both need an agent with shell and file access. In a plain chat, paste the text and copy the result yourself.
- doc-reviewer fetches URLs with `curl` and reads files, so it needs an agent with shell and file access for those inputs. In a plain chat, paste the document text.
- Screenshot mode needs a model that accepts image input.
- ui-developer fetches the design system with `git` and runs `scripts/audit_ui.py` with Python 3, so it needs an agent with shell access. Without Python it falls back to manual searches.
- The `/ai-toolkit:...` commands are Claude Code only. Elsewhere, trigger the skills with a prompt.

## Repository Layout

The repository root is the `ai-toolkit` plugin.

| Path                | Contents                                                                                                  |
| ------------------- | --------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/`   | The marketplace manifest (`marketplace.json`) and the plugin manifest (`plugin.json`).                    |
| `skills/`           | One folder per skill, each with a `SKILL.md` and a `README.md`.                                           |
| `rules/shared/`     | Rules shared across skills: `markdown-rules.md`, plus `project-planner-rules.md` for project-planner.       |
| `rules/ui-design/`  | Guidance files for the ui-developer skill, with the license notice for the taste-skill material.           |
| `templates/`        | Templates that skills point you to, such as `spec-template.md`.                                           |

## License

MIT. See [LICENSE](LICENSE).
