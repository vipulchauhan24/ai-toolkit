# design-system-builder

## Should trigger

- "Create a design system for a meal-planning app."
- "I need a color palette and type scale for a new fintech product."
- "Set up design tokens with light and dark themes."
- "Here are three screenshots I like. Build a style guide from them."
- "Our brand color is #0A7C66. Make a full token set around it."
- "Define a spacing and typography scale for a new product."
- "Generate a style guide and tokens for a kids' education startup."
- "Can you design the theming and dark mode for our new app from scratch?"
- "Make a design system from this logo."
- "Build me tokens that export to Figma."

## Should NOT trigger

- "Build a landing page for my bakery." (ui-developer)
- "Style this button with my design system." (ui-developer)
- "Change the primary color in our existing tokens.css." (edits an existing system)
- "Write a React component for a modal." (frontend-react)
- "Poke holes in this design system doc." (doc-reviewer)
- "Trim this style guide." (doc-trimmer)
- "Plan the rollout of our design system." (project-planner)
- "What's the weather in Paris?"
- "Write a Python script to resize images."
- "Make a bar chart of monthly sales."

## Functional

**Autonomous brief**
- Given: "create a design system for a playful fintech app for students, web only"
- When: the skill runs to completion
- Then: it asks its missing questions in one batch, or applies defaults and lists them. It shows a Direction Summary with a theme name and waits for confirmation. After confirmation the output folder has `tokens.css`, `tokens.json`, `tailwind-theme.css`, `components.md`, `README.md` and `preview.html`, and `contrast-reports/<name>.txt` exists next to it. The checker reports no failing pair.

**Brand color that fails contrast**
- Given: a palette with one yellow brand color
- When: the skill checks label contrast
- Then: the brand value is not silently changed. The report names the failing pair, the passing alternative, and the original value is kept as its own primitive.

**Unreadable link**
- Given: a Figma URL it cannot open
- When: the skill reads the input
- Then: it says so and asks for screenshots or exported colors. It invents nothing.
