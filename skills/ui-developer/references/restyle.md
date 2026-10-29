# Restyling an existing project

Section numbers (§) refer to SKILL.md. Read this file in full when the task is to restyle existing UI.

Use this when the project already has UI and the task is to bring it onto the design system ("restyle this", "move this to Ember", "make this match my design system"). It changes how things look. It does not change what they do.

**Scope the work.** Restyle only the screens or components the user names. If none are named, list the screens you found and ask which, in the single batch of §2. A restyle lands one screen at a time, and the app works after each. If the project is in git, suggest a branch and one commit per screen so each step can be reverted; make commits only if the user asks.

**Record the before, then change nothing until it is written down:**

1. Read the code: framework, styling method (Tailwind version, CSS modules, styled-components, plain CSS), component library, the shared components the screens use, routes, and how data reaches the screens.
2. List what must survive: routes, forms and their validation, data wiring, behavior (menus, dialogs, keyboard shortcuts), copy, and brand files such as the logo. None of these change.
3. Run the safe checks from §7 step 1 and note the result. A failure that exists before your change is not yours; say so.
4. List, per screen, what does not match the design system: literal values, legacy CSS, hand-built look-alike controls, missing states, missing focus styles. Anything the design system doesn't cover goes in as a design-system gap (§3). If the user asked only for an audit or review, stop here and report this list.

**Keep the stack.** No framework, component-library or state-management migration, and check the dependency file before adding anything. The design system's utilities are required (§2): if the project has no Tailwind v4, that is a hard blocker, because setting it up is a project change, not a side effect of a restyle. If the existing brand colors or fonts differ from the design system's, say so once and confirm that the design system replaces them. Logo and image files stay as they are.

**Order of work**, per screen, biggest effect for the least risk:

1. The foundation, once: bring in the design system (§5 step 1).
2. Color, type, radius, shadow and motion: replace literal values and legacy classes with the design system's utilities.
3. Spacing and layout: the design system's spacing and page tokens.
4. States: loading, empty, error, disabled, focus-visible, and both themes.
5. Components: replace hand-built or look-alike controls with the wrapper from §4 (on the project's component library, or semantic HTML). Behavior stays; only the look changes.

**Shared components.** Restyling a shared component (a Button used on twenty screens) changes every screen that uses it, including screens outside the scope. Before changing one, search for its usages, tell the user how many screens it touches, and check that each still works. Restyle it once, as the wrapper, instead of patching it per screen.

**Legacy CSS.** Add none (§3). When a screen no longer uses a legacy stylesheet or class, delete that CSS only if a search shows nothing else uses it. The search must also cover class names built at run time (template strings, string concatenation, CSS-module lookups such as `styles[name]`), templates in other languages, and CMS or database content. If any of those could produce the class, keep it. CSS still used by screens outside the scope stays, and goes in the report as remaining legacy. A restyled screen has no legacy styling left on it.

**Prove it**, on top of §7:

1. Build, lint and tests are no worse than the "before" result.
2. Every route, form, menu and dialog on the "must survive" list still works. Confirm what the project's tests cover, and put the rest on the look-at list for the user.
3. No CSS file gained a line. Legacy CSS only shrinks.
4. The look-at list (§7 step 4) covers each restyled screen in light and dark, and names the screens that changed through a shared component.

**Report**, on top of §8: per screen, what was replaced and what remains; legacy CSS still in use and by which screens; shared components changed, with how many screens use each; brand differences you confirmed; and the "before" build and test result next to the "after".
