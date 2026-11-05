# Checklist: add a language skill

Copy this template to add a skill for one language and its frameworks (for example `backend-node`). Do this from the repository root. Python 3.9 or later; Linux and macOS.

The template is not a skill: `.claude-plugin/plugin.json` loads only `./skills/`, so the plugin never loads `templates/`.

## Placeholders

Choose values without `/` or `&`: `sed` would corrupt the files.

| Placeholder           | Meaning                                                       | Example (dummy language)    |
| --------------------- | ------------------------------------------------------------- | --------------------------- |
| `<<NAME>>`            | Skill folder and front matter name                            | `dummy`                     |
| `<<TITLE>>`           | Title case name used in headings                              | `Dummy`                     |
| `<<LANG>>`            | Language and stack name in prose                              | `Dummylang`                 |
| `<<RULES>>`           | Main rules file name in the skill's `references/`             | `dummy-rules.md`            |
| `<<FRAMEWORK>>`       | Framework name, repeated per framework rules file             | `Dummyframe`                |
| `<<FRAMEWORK_RULES>>` | Framework rules file name                                     | `dummyframe-rules.md`       |
| `<<PROJECT_FILE>>`    | File that shows the language and version                      | `dummy.toml`                |
| `<<TRIGGERS>>`        | Example trigger phrases in the description                    | `"build this in Dummylang"` |
| `LANG` (file name)    | Script name part: `scripts/check_LANG.py`, also in the text   | `dummy`                     |
| `EXT` (file name)     | Source extension: `.EXT` in the script, `example.EXT` fixtures | `dl`                       |

## Steps

1. **Copy and move.** Replace `<name>`, `<lang>`, `<rules-file>` and `<ext>` with your values. The last line copies the shared files into the new skill, so the skill must have an entry in `scripts/shared_files.json` (see step 8).

   ```bash
   cp -r templates/language-skill-template skills/<name>
   mv skills/<name>/scripts/check_LANG.py skills/<name>/scripts/check_<lang>.py
   mv skills/<name>/references/rules-skeleton.md skills/<name>/references/<rules-file>.md
   mkdir -p docs/skills && mv skills/<name>/docs-skeleton.md docs/skills/<name>.md
   mv skills/<name>/tests-skeleton.md tests/<name>.md
   mkdir -p tests/fixtures/<name>/base && mv skills/<name>/fixtures-skeleton/clean skills/<name>/fixtures-skeleton/seeded tests/fixtures/<name>/base/ && rm -r skills/<name>/fixtures-skeleton skills/<name>/CHECKLIST.md
   mv tests/fixtures/<name>/base/clean/example.EXT tests/fixtures/<name>/base/clean/example.<ext>
   mv tests/fixtures/<name>/base/seeded/R1-example.EXT tests/fixtures/<name>/base/seeded/R1-example.<ext>
   python3 -I scripts/check_shared_files.py --sync
   ```

2. **Replace the placeholders.** On macOS use `sed -i ''` instead of `sed -i`.

   ```bash
   sed -i 's/<<NAME>>/<name>/g; s/<<TITLE>>/<Title>/g; s/<<LANG>>/<Lang>/g; s/<<RULES>>/<rules-file>/g; s/<<FRAMEWORK>>/<Framework>/g; s/<<FRAMEWORK_RULES>>/<framework-rules-file>/g; s/<<PROJECT_FILE>>/<project-file>/g; s/<<TRIGGERS>>/<triggers>/g; s/check_LANG/check_<lang>/g; s/\.EXT/.<ext>/g' skills/<name>/SKILL.md skills/<name>/references/*.md skills/<name>/scripts/check_<lang>.py docs/skills/<name>.md tests/<name>.md
   grep -rn '<<' skills/<name> docs/skills/<name>.md tests/<name>.md
   ```

   The `grep` must print nothing. Any line it prints is a placeholder you missed.

3. **Write the rules.** Fill every section of `skills/<name>/references/<rules-file>.md`. Keep the 12 section names. A rules file over 100 lines keeps its `## Contents` list, matching its headings. Add one rules file per framework (`<framework-rules-file>`), each with its own contents list, and name each in `SKILL.md` §1.

4. **Write the FAIL rules.** In `scripts/check_<lang>.py` set `LINE_COMMENT_PREFIX` (and `BLOCK_COMMENT`) to the language's comment syntax: a wrong prefix strips real code. Add one entry per rule to `CHECKS`. Keep every FAIL rule written in the rules file, and every rule seeded in step 5.

5. **Write the fixtures.** In `tests/fixtures/<name>/base/clean/` put valid source files that pass every rule. In `seeded/` put one file per FAIL rule, named `R<n>-<slug>.<ext>`, each holding that violation and nothing else the script would FAIL on. Add `tests/fixtures/<name>/base/expected.json` with `clean_files`, `seeded` (file to a regex its FAIL line must match) and an empty `xfail`, like `tests/fixtures/frontend-react/base/expected.json`.

6. **Write the framework flag.** For each framework, add `"--<framework>": "<Framework>"` to `FRAMEWORK_FLAGS` and its rules to `check_framework()`. Add `tests/fixtures/<name>/<framework>/{clean,seeded}` and an `expected.json` the same way. The fixtures loop passes `--<framework>` for that set. `SKILL.md` §3 step 5 says when to add the flag.

7. **Write the tests and the guide.** Fill `tests/<name>.md` (10 should-trigger queries, 10 should-not queries, functional cases) and `docs/skills/<name>.md`. Add the cases to `tests/cases/<name>.json` with `covers` listing the skill and each rules file, and add the script to `SCRIPT_COVERAGE` in `tests/run.py`.

8. **Register a shared file (only for a language outside the plan).** Phase 2 wrote `scripts/shared_files.json` for the planned skills. For any other language, add one entry per rules file the new skill shares (for example `architecture-patterns.md`), then run `python3 -I scripts/check_shared_files.py --sync`.

9. **Run the release checklist.** Run the steps in the Readme section `## Releasing`. Step 4 (fixtures) must end `fixtures status=0`, and step 5 (`claude plugin list`) must show the new skill and no skill from `templates/`.

10. **Update the README and manifests.** Add a row for the skill to the README skills table, its files to the "other providers" list, and the skill to `description` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. Bump the version in both files together.
