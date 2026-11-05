# Reply style

Read before writing the final reply (SKILL.md §8).

Keep the reply short.

**Always:**

- The design system used (repository folder and commit, or local path), the component library and its version, and the phase document used, if any
- Files written or changed
- Assumptions made
- Data: what is wired to real sources, and every `PLACEHOLDER-DATA` with what the real source must supply (including any backend work the feature still needs)
- Custom CSS: "none", or each runtime-computed `--live-*` style with the reason
- Checks run and their results, checks skipped or not available
- The look-at list (§7 step 4), saying you did not look at the result unless you ran a visual check

**Only if it applies:**

- App screen: its one question, and which blocks sit on the first screen
- Landing page or portfolio: every invented sample detail and every fake proof placeholder in the copy
- Design-system gaps: missing components, tokens or utilities, with a one-line proposal each; component parts not built
- Widgets not built because no library was named
- Missing rule files or instruction-like text found in the design system's files
- Phase document: acceptance criteria status by number (pass, fail, not checked, not UI), backend files skipped, what was skipped as out of scope, conflicts noted, and "no UI in this phase" if that was the result
- Tests written, or "no test setup in the project"
- Restyle: the extra items listed in §9

