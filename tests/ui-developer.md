# ui-developer

## Should trigger

- "Build this screen with my design system."
- "Build the pricing page."
- "Implement this UI from the mockup."
- "Style this dashboard with Ember."
- "Restyle this app onto my design system."
- "Move this UI onto the new tokens."
- "Build a landing page for my portfolio."
- "Create an admin settings view using design-system/Acme."
- "Implement the UI for phase 4." (with a phase document)
- "Make this form match our design system."

## Should NOT trigger

- "Create a design system." (design-system-builder)
- "Change the primary color in the tokens." (design-system-builder)
- "Build the REST API for this screen."
- "Add login and sessions." (auth)
- "Write the database schema."
- "Split this spec into phases." (project-planner)
- "Write a React hook for fetching orders." (frontend-react)
- "Explain flexbox."
- "Review this design doc." (doc-reviewer)
- "Make a chart of last month's revenue."

## Functional

**New screen**
- Given: a project with Tailwind v4 and the default design system
- When: asked for a billing settings screen
- Then: no `.css` file was created and the entry stylesheet gained only `@import` lines. `scripts/audit_ui.py --css <built.css>` ran with no FAIL. The report names the design system and commit, the library and version, `PLACEHOLDER-DATA`, "Custom CSS: none", and a look-at list that says the result was not viewed.

**Token-only design system**
- Given: a design system with tokens and specs but no theme file
- When: asked to build a screen
- Then: nothing is built. It asks for a theme file or another design system. It writes no CSS.

**Phase document**
- Given: a phase document with backend and UI criteria
- When: the skill reports
- Then: criteria are listed by number as pass, fail, not checked or not UI. Backend files are not built.

**Fake proof**
- Given: a landing page request
- When: the copy needs a testimonial
- Then: it uses plainly fake text such as "Customer name" and lists it in the report.
