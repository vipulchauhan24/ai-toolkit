# ui-craft: sources and decisions

For whoever maintains `ui-craft`. The skill never reads this file, and agents do not need these links while working.

**How each source was read**

- **Direct:** the full text was read.
- **Fetched:** the page was opened through a tool that summarises it, so check exact wording before quoting.
- **Snippet:** only a search result excerpt was seen. Open the page before relying on it.

**Strength**

- **Primary:** research, or the owner's own documentation.
- **Practitioner:** experienced opinion, usually consistent across sources, but not tested.

## Copy files

| Source | Used for | Read | Strength |
|---|---|---|---|
| [NN/g: How users read on the web](https://www.nngroup.com/articles/how-users-read-on-the-web/) | 79% scan, 16% read word by word, 124% better usability, promotional language as a burden. Study from 1997 | Fetched, figures confirmed | Primary, old |
| [NN/g: Legibility, readability and comprehension](https://www.nngroup.com/articles/legibility-readability-comprehension/) | About 28% of words read, reading levels, active voice, front-loading | Fetched | Primary |
| [NN/g: The 3 Cs of microcopy](https://www.nngroup.com/articles/3-cs-microcopy/) | Clarity, then concision, then character | Fetched | Primary |
| [NN/g: Error-message guidelines](https://www.nngroup.com/articles/error-message-guidelines/) | Error placement, wording, tone, keeping input | Fetched | Primary |
| [NN/g: Designing empty states](https://www.nngroup.com/articles/empty-state-interface-design/) | Empty-state content | Fetched | Primary |
| [NN/g: 5 steps to a UX-design portfolio](https://www.nngroup.com/articles/ux-design-portfolios/) | Survey of 204 hiring professionals, case-study contents. About UX portfolios; applying it to engineers is an inference | Fetched | Primary |
| [NN/g: Formatting long-form content](https://www.nngroup.com/articles/formatting-long-form-content/) | Descriptive headings and scannable long text. It does not state "one idea per paragraph" | Fetched | Primary |
| [Mailchimp: Voice and tone](https://styleguide.mailchimp.com/voice-and-tone/) | Voice versus tone | Fetched | Primary |
| [Vercel web interface guidelines](https://github.com/vercel-labs/web-interface-guidelines) | Typography marks, button labels, loading text, tabular numbers, `Intl` | Fetched | Primary |
| [Diátaxis](https://diataxis.fr/how-to-guides/) | The four documentation kinds, writing a how-to | Fetched | Primary |
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | Writing tells, title case, what is not a tell. About encyclopedia text. The last 44,700 characters were not read | Fetched | Primary, dates quickly |
| [taste-skill](https://github.com/Leonxlnx/taste-skill) | Fact sheet, counting habits, over-correction | Direct | Practitioner |
| `ui-developer` copy rules in this repository | Argument-first method, headline budget idea. Adapted from taste-skill | Direct | Practitioner |
| [linear.app](https://linear.app/), [stripe.com](https://stripe.com/) | Real headlines, sentence case, proof, November 2026 | Fetched | Observation |
| [brittanychiang.com](https://brittanychiang.com/) | Portfolio structure, and a test for false alarms in `check_copy.py` | Fetched | Observation |
| [NN/g: Writing, snippets on one idea per paragraph](https://www.nngroup.com/articles/applying-writing-guidelines-web-pages/) | One idea per paragraph, as reported in a search result | Snippet | Check |
| [Scrimba](https://scrimba.com/articles/how-to-build-a-web-developer-portfolio-that-gets-you-hired) | Developer portfolios | Snippet | Practitioner |
| [Leadfeeder](https://www.leadfeeder.com/blog/saas-landing-pages-that-convert/), [Userpilot](https://userpilot.com/blog/saas-landing-pages/) | SaaS sections as visitor questions. No controlled study of section order was found | Snippet | Practitioner |
| [Baymard product page research](https://baymard.com/research/product-page) | Product pages commonly fail on usability. Detailed guidelines are paywalled and were not checked | Snippet | Primary, partial |
| [Webtonic](https://www.webtonic.io/blog/best-copywriting-agencies-birmingham) | Agency process and the debate over publishing prices | Snippet | Practitioner |
| [BentoBox](https://getbento.com/blog/restaurant-website-most-important-pages), [Web Designer Depot](https://www.webdesignerdepot.com/2012/06/essential-advice-for-restaurant-websites/) | What restaurant visitors look for, menus as HTML | Snippet | Practitioner |
| [Clutch](https://clutch.co/visualobjects/web-design/blog/event-landing-pages) | Event page essentials | Snippet | Practitioner |
| [GetResponse](https://www.getresponse.com/blog/waitlist-landing-page), [Moosend](https://moosend.com/?p=67875) | Waitlist page content | Snippet | Practitioner |

## Working defaults

These are judgement calls, with no research behind them. Change them freely:

- Length budgets, such as a supporting line of about 25 words and two lines for a headline.
- The section tables in each kind file.
- The word lists and per-page allowances in `scripts/check_copy.py`. They date quickly as models change, so review them.
- Dialog and label patterns in `copy-app.md`.
- What follows a sign-up, and who should attend, in `copy-event.md`.
- `copy-ecommerce.md`, beyond the general points above.

## Decisions

- **Sentence case, against Vercel.** Vercel's guidelines ask for Title Case on headings and buttons. This skill uses sentence case, because Linear and Stripe do, and Wikipedia lists title case among signs of AI writing. The live Vercel review step must skip that one rule.
- **Curly quotes, despite Wikipedia.** Wikipedia lists them as a sign of AI writing in its plain-text articles. On a web page they are correct.
- **Sources stay out of the skill.** Working files hold rules only, because they load on every run and links invite agents to fetch outside content.
