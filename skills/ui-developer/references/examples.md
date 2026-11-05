# Examples

## Example 1: A new screen on the default design system

User says: "build the billing settings screen"

Actions:
1. Preflight: the guidance files and `scripts/audit_ui.py` exist, Python 3 is available.
2. Fetch Ember at the pinned commit and write the utility map. The project has Tailwind v4 and a component library already, so ask nothing beyond the route and data source, in one batch.
3. Read `references/app-screens.md`. List every state per screen (default, loading, empty, error, success, disabled) and the 390px and desktop behavior.
4. Wire the foundation once, wrap components once, then compose the screen from the wrappers with utility classes only.
5. Run the project's checks, build the CSS, then `python3 -I <this-skill-folder>/scripts/audit_ui.py --css <built.css> <changed files>`. Fix every FAIL.

Result: the report names the design system and commit, the library version, files changed, assumptions, `PLACEHOLDER-DATA` entries, "Custom CSS: none", checks run, and a look-at list saying the result was not viewed.

## Example 2: Blocked on a token-only design system

User says: "build the dashboard with the Acme design system", and Acme has tokens and specs but no theme file.

Result: build nothing. Say the design system maps no tokens to utility classes, and ask the user to add a theme file with design-system-builder or name another design system. Non-interactive: write a Blocked report. Never write CSS as a workaround.
