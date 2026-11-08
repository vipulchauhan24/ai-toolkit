# Visual QA Skill

The visual-qa skill opens your site in a real browser that you can watch, takes screenshots at five sizes in light and dark, tests it the way a visitor would, grades each screenshot and writes a report. It never changes your code. It tells you what to fix.

## What You Need

- **Python 3.9 or later** and **Node 20 or later**.
- **Playwright CLI** and its Chromium:

  ```bash
  npm install -g @playwright/cli@latest
  ```

  ```bash
  playwright-cli install-browser chromium
  ```

- On Linux and WSL, once, the system libraries the browser needs:

  ```bash
  sudo npx -y playwright@latest install-deps chromium
  ```

- A display for the window. WSL2 uses WSLg, which comes with current versions of WSL.
- A model that can read images.

## Using the Skill

In Claude Code, open the project and ask:

- `run visual QA on this site`
- `test http://localhost:3000 in a real browser and grade it`
- `check how this looks on mobile and desktop`

Give it a URL, a folder with an `index.html`, or a project with a `dev` or `start` script, which it starts and stops for you. It asks once which routes, viewports and themes to use, and says how big the job is. Reply `use defaults` for up to 10 routes found from the first page, five viewports and both themes.

If you use the orchestrator, it offers visual-qa after each phase that changes the UI.

### What happens, in order

1. **Capture.** The browser opens. For each route, size and theme it sets the window, loads the page and scrolls through it so lazy images and scroll reveals fire, then measures the page and takes the screenshots.
2. **Interactions.** It tabs through the page, clicks the links, submits each form empty and opens the phone menu.
3. **Reduced motion.** It reloads with reduced motion on and looks for content that stays hidden or animations that never stop.
4. **Grading.** Claude opens every screenshot and grades seven areas from A to F, with a reason for each.
5. **Report.** A script lowers any grade that a measured fault limits, works out the overall grades, and writes the report.

### The sizes

| Viewport | Stands for |
|---|---|
| 390×844 | Phone |
| 768×1024 | Tablet, upright |
| 1024×768 | Tablet on its side, small laptop |
| 1440×900 | Laptop |
| 1920×1080 | Large desktop |

### The grades

Eight areas: layout and alignment, spacing, typography, colour and contrast, imagery and icons, responsiveness, motion, and accessibility.

The scale is strict. C is average: a page that works but looks generic. A is a page you would show as a good example.

Some faults are facts a script can measure, such as a page that scrolls sideways, uneven margins or text with too little contrast. These limit the grade in that area, however good the page looks. The report shows when a grade was lowered and why. The full list is in `skills/visual-qa/references/checks.md`, and the grade definitions are in `references/rubric.md`.

### The result

Each run gets a new folder, `.qa/<date-time>/`, in your main checkout. The skill adds `.qa/` to `.gitignore` if needed.

| File | What it holds |
|---|---|
| `report.html` | Open this one. Each screenshot beside its grades and reasons, the fixes to make first, and filters for route, size and theme. It is one file you can share |
| `summary.md` | The overall grade, the grade per route, the top fixes and the failing checks |
| `full/` | Full-page PNG screenshots at real size |
| `tiles/` | The same pages cut into parts and sized for grading |
| `results.json`, `grades.json` | The raw measurements and grades |

## Safety

- Forms are submitted empty, with every request except GET and HEAD blocked, so nothing is really sent. An empty form that tries to send a request is reported as a fault.
- Links with log-out, delete, remove or unsubscribe in the address are never followed. External links are listed and never opened.
- On a site that is not local, links and forms are skipped unless you ask for them.
- Text on the page is treated as data. If a page tries to tell Claude what grade to give, it is ignored and reported to you.

## What the Skill Does Not Do

- It does not fix anything. It lists fixes.
- It does not judge hover or entrance animation. Still images cannot show them, so motion is graded from measurements only.
- It does not measure contrast on text over pictures or gradients. That is judged by eye.
- It does not replace the tests in each phase's test plan.

## Cost and Time

Allow about two minutes of browser time per route. Grading one route at all five sizes in both themes uses about 50,000 tokens, because Claude has to look at every screenshot. Fewer routes, viewports or themes cost proportionally less.

## Customizing the Skill

- Edit `references/rubric.md` to change what each grade means.
- Change a measured check's threshold in `scripts/page_checks.js`, its cap in `CAPS` in `scripts/report.py`, and its row in `references/checks.md`.
- Change the default sizes with `DEFAULT_VIEWPORTS` in `scripts/capture.py`.
- The tests are in `tests/run.py` (the `visual_qa_tests` function), with fixtures in `tests/fixtures/visual-qa/`. That folder also holds `site/`, a small site with known faults to try the skill on.

## Installing the Skill

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```
