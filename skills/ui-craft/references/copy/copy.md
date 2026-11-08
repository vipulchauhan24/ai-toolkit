# Copy: rules for every page

Words come before layout. No typeface rescues a four-line headline, and a pretty card does nothing for a section with no point. Write the whole page as text first, check it, and only then write markup.

Read this file for every job. Then read the file for the kind of page, then `copy-human.md`.

| The job | Also read |
|---|---|
| Personal site, portfolio, résumé site | `copy-portfolio.md` |
| Software or tech product site, SaaS landing page | `copy-saas.md` |
| Screens inside a product: dashboards, forms, settings, lists | `copy-app.md` |
| Blog, articles, documentation, newsletter | `copy-blog.md` |
| Agency, consultancy, freelancer, clinic, any hired service | `copy-service.md` |
| Shop, product page | `copy-ecommerce.md` |
| Café, restaurant, hotel, gym, any place people visit | `copy-place.md` |
| Conference, launch, webinar, waitlist | `copy-event.md` |

A landing page is a format, not a kind. Use the file for what the page is selling.

## Contents

1. How people read a page
2. The copy file
3. The fact sheet
4. Voice and tone
5. Know the reader and the context
6. The page as an argument
7. Headlines and headings
8. Supporting lines and body text
9. Buttons, links and navigation
10. Forms, errors, empty states and confirmations
11. Numbers, dates and units
12. Text typography
13. Proof
14. Page title, description and alt text
15. Check it

## 1. How people read a page

They mostly do not. In Nielsen's studies 79% of test users scanned a new page and 16% read it word by word, and a later analysis put an average visit at about 28% of the words on the page. When the same site was rewritten to be shorter, easier to scan and free of promotional language, measured usability rose by 124%.

So:

- Put the most important words first, in the headline, the paragraph and the list item.
- Give each paragraph one idea.
- Make headings say something a reader can use without reading the text under them.
- State facts. Readers have to work to filter hype out, and that work costs them attention.

## 2. The copy file

Write the copy to `COPY.md` at the project root, next to `DESIGN.md`. `scripts/check_copy.py` reads this format, so keep to it.

```text
kind: portfolio
voice: plain and exact, first person, dry only in the 404

## facts
- Reduced style recalculations from 500 to 100 per second on the Gantt view (United Airlines, résumé)
- Quote: "Fixed in a day what we had lived with for a year." Dana Ito, engineering manager

## missing
- Screenshots of the flight schedule tool (client must supply)

# page: /
title: Ada Lund, full-stack engineer
description: I build fast web apps and the data systems behind them.

## hero
h1: Ada Lund builds fast full-stack web apps
sub: Six years on React, Node and Python, most of it on data-heavy tools.
button: Email me

## experience
h2: Experience
h3: Senior engineer, Northline Rail
body: Rebuilt the timetable view so it stays smooth at 10 million rows.
```

- The first lines are `kind:` (one of the eight kinds above), `voice:`, and optionally `allow:` for words that are literal for this client, such as `allow: harness` for a climbing shop.
- `## facts` holds the fact sheet. `## missing` lists what the client must supply. Neither appears on the page.
- Each page starts with `# page: <route>`, then its `title:` and `description:`.
- Each section is `## <name>`. Each line is a role and its text.

| Roles | Used for |
|---|---|
| `h1` `h2` `h3` `eyebrow` | Headings and the small label above one |
| `sub` `body` `item` `stat` `quote` | The supporting line, paragraphs, list items, a number with its label, a quotation |
| `button` `link` | Actions and links |
| `label` `hint` `error` `success` `empty` `loading` | Form and app states |
| `alt` `meta` | Image descriptions, and small print such as the copyright line |

## 3. The fact sheet

Write this before any sentence. It is the most important step in this file, because generic copy is what a writer produces when they have no facts.

Collect, word for word where you can, from the brief, the client's files and any existing site:

- What this is, in one plain sentence with no adjectives.
- Who it is for, and who it is not for.
- What the reader does today instead.
- The real difference, and what proves it.
- Numbers, and the source of each.
- Names of people, clients and products that may be shown.
- Quotes, exactly as said, with who said them.
- Odd true details: how the work is really done, a limit, something inconvenient.
- The offer: price, terms, the one thing the reader should do.

**Nothing on the page may be invented.** That covers people, quotes, customers, logos, ratings, awards and figures. `check_copy.py` fails any number or quote that is not in the fact sheet.

If a fact is missing, ask. If you cannot ask, write a plainer line, or drop the section and add it to `## missing`. A page with four true sections beats one with seven padded ones. Never ship "Coming soon" cards, brackets or sample text.

**Sample details are the one exception**, and only when the brief gives the shape but not every value: eight apartments at "about €90", a short list of treatments. Write realistic details so the design can be judged at its real density. Put them in the fact sheet marked `(sample)` and list them in the report for the client to confirm.

## 4. Voice and tone

**Voice stays the same. Tone changes with the moment.** A person sounds like themselves whether they are telling a joke or giving bad news, but they say those things differently.

Write the voice on the `voice:` line as a few concrete choices: who is speaking (I, we, or the product), how technical it is, how formal, and where humour is allowed. Take it from the client's own writing if there is any. Each project gets its own. The default model voice (warm, wry, modest) is not a voice.

Tone follows the reader's state of mind:

| The reader is | Tone |
|---|---|
| Deciding if this is for them (hero, about) | The most voice on the page |
| Comparing or checking details (features, specs) | Plain and exact |
| Worried about money or commitment (pricing, checkout, FAQ) | Flat facts, no jokes |
| Blocked by something (errors) | Calm, specific, no humour, no blame |
| Done (success, confirmation) | Short and warm |
| Waiting or lost (empty states, 404) | Helpful. A light touch is welcome here if the voice allows it |

Priority, always: **clear, then short, then characterful.** Character never comes at the cost of the first two.

## 5. Know the reader and the context

Answer these before drafting:

- **What do they already know?** Someone who has never heard of this needs the category named. Someone comparing options needs the difference. Someone who already knows it needs the price and the button.
- **Where did they come from?** A search result, a job application, a friend's link. Match what they expected to find.
- **What words do they use?** Use the terms of the audience, even technical ones: specialists expect the vocabulary of their field. Do not use your company's internal names for things.
- **What device are they on?** Phones need shorter text still.

Reading level: about grade 8 to 9 for the general public, about grade 12 for specialists. Grade level is about sentence and word length, and the tone stays adult. `check_copy.py` estimates it.

## 6. The page as an argument

Before writing lines, list what the page must establish, one claim to a section, and note the evidence for it:

```text
1. We repair bikes at your door in south Leeds.    -> the van outside a house
2. Most repairs are finished in one visit.         -> what the van carries
3. Prices are fixed before we start.               -> the price list
4. Pick a slot online, usually within two days.    -> booking button
```

If you can't state what a section claims, cut it. Claims come in the order a reader needs them, and that order sets the page. The kind file lists likely sections, but your facts decide which ones you keep.

## 7. Headlines and headings

**The h1 says what this is.** A stranger should be able to say what the page is about within five seconds. Exactly one per page.

**Two lines at most at every width.** Average letter width decides how much fits, so estimate it before settling on a headline. For a typical sans or serif at display size, a letter is about half as wide as the font size. Narrow fonts fit about a fifth more, and wide fonts or capitals about a sixth less.

| Where | Line width | Font size | Fits on two lines |
|---|---|---|---|
| Phone | 358px | 40px | about 36 characters |
| Phone | 358px | 32px | about 44 characters |
| Tablet | 704px | 56px | about 50 characters |
| Desktop | 1200px | 88px | about 54 characters |

The phone is the limit, so aim for about 36 to 44 characters. Over 60, the detail belongs in the supporting line. A headline that only fits at a small size is too long.

Shapes that work, plainest first:

- **What it is and who for:** "Scheduling software for dental clinics"
- **Name and what it does:** "Mira Holt designs type for small presses"
- **A specific claim:** "Payroll that closes in one afternoon"
- **The place or the moment:** "Ramen in Kreuzberg, open late"

Section headings name the thing or make a short claim. "Pricing" is a good heading. Two to six words, sentence case, and no full stop unless every heading on the site has one.

Avoid:

- A line any company could use: "Smarter tools for growing businesses".
- Three clipped words in a row: "Bold. Clear. Yours."
- Denying something nobody said: "More than a calendar, it's a way of working".
- Empty openers: "Welcome to our site", or a new name followed by "reimagined".
- A question the reader never had.
- A heading that only makes sense once you have read the section.

## 8. Supporting lines and body text

- **Supporting line:** one sentence, up to about 25 words, that says concretely what it is and how it works. It adds to the headline and never repeats it.
- **Body:** short paragraphs of plain statements. Each sentence earns its place by telling the reader something.
- **Specific beats general:** "delivered by Friday" over "fast delivery", "a 12-seat counter" over "intimate".
- **Active voice** nearly always. "We reply within a day", and not "Replies are sent within a day".
- **Say "you"** for the reader. Use "I" or "we" for whoever is speaking, the same one throughout.
- **One word for one thing.** If it is an "invoice", it stays an invoice. Do not rotate through synonyms for variety.
- **Lengths follow the material.** One card can have more to say than its neighbours. A list has as many items as there are things, and four real features are four, not three.

## 9. Buttons, links and navigation

- **A button says what happens:** a verb and the thing. "Book a table", "Download for Mac", "Email me". One to five words.
- **Never** "Click here" or "Submit". Avoid "Learn more", "Get started" and "Discover" when you can name the thing. Real sites do use "Get started" when the next step really is starting, so it warns rather than fails.
- **Say what the button leads to.** If there is a price, a card requirement or a form behind it, the reader should not be surprised.
- **Use the same wording for the main action** on every page.
- **At most two actions in a hero,** one clearly primary.
- **A link makes sense on its own.** Its words say where it goes. "Read the case study", and not "here".
- **Navigation:** up to five plain nouns. Use the words a visitor would look for.

## 10. Forms, errors, empty states and confirmations

These are copy too. A hand-tuned headline above a stock error message gives the game away.

**Forms**
- A label says what goes in. It stays visible and is never replaced by placeholder text.
- A hint explains only what is not obvious: why you need it, or the format.
- The submit button repeats the action: "Send message", "Create account".
- Ask only for what you use.

**Errors**
- Put the message next to the problem. Never rely on colour alone.
- Say what went wrong and how to fix it, in plain words: "Enter a date after today".
- Do not blame the reader. Avoid "invalid", "illegal", "incorrect". No humour: it wears thin when someone sees it twice.
- Keep what they typed so they can correct it.
- Do not show an error before they have finished trying.
- Show error codes only for technical diagnosis, and after the plain message.

**Empty states**
- Say why it is empty: "No invoices match this date range".
- Say what will appear and how: "Star a project to pin it here".
- Give a direct way forward, usually a button.
- Never show "nothing here" while data is still loading. Show a loading state.

**Loading and success**
- Loading text names what is happening and ends with an ellipsis: "Saving…".
- A success message says what happened and what comes next: "Message sent. I reply within two days."
- Only promise a time the fact sheet gives.

**404:** say the page is not here, and offer the two most useful links.

## 11. Numbers, dates and units

- Use digits for counts: "8 developers", "3 projects".
- Keep each number beside the claim it supports, with its unit. A bare number means little.
- A number from real records is rarely tidy. If every figure on the page ends in zero, check where they came from.
- A figure means something only next to what it was before or what it is compared with: "from 500 to 100 per second".
- Write dates in full where space allows: "12 March 2026". Choose one format per site.
- Join a number to its unit with a non-breaking space, so "10 km" does not split across lines.
- Line up figures in columns with tabular numerals.
- One fact has one value and one wording everywhere it appears.

## 12. Text typography

- **Sentence case** for headings, buttons and navigation. Keep proper nouns capitalised.
- **Curly quotes and apostrophes** (“ ” ’), never straight ones, on a finished page.
- **A real ellipsis** (…), never three dots.
- **En dash for ranges** (9–5, 2020–2024). Em dashes sparingly.
- **Non-breaking space** to stop one short word being left alone on the last line of a headline.
- **All caps** only for labels of one to three words.
- **Centre** only text of up to three lines, and never justify.
- **Line length:** about 45 to 75 characters for reading. Past 90 is hard work.
- **Body text at 16px or more** on the web, and never below 14px for running text.
- **Bold** picks out a few words a scanner should catch. A page where everything is bold has nothing bold.
- **One exclamation mark at most**, and usually none.
- **No emoji** in headings or list items unless they are the client's own voice.
- **Headings balance** (`text-wrap: balance`) and paragraphs avoid orphans (`text-wrap: pretty`).

## 13. Proof

- The product on screen, at a good size, is the strongest proof. A demonstration beats a testimonial.
- Say how it works, specifically. A mechanism convinces more than an adjective.
- Use a real number, a real name or a real customer, placed beside the claim it supports.
- Quote people word for word, with their name and role.
- Superlatives are more believable from someone else, so leave them to your customers.
- **No proof is a normal state.** No testimonials section is better than a fake one.

## 14. Page title, description and alt text

- **Title:** the page, then the site. About 60 characters at most before search results cut it.
- **Description:** one sentence on what the reader finds here. About 160 characters at most.
- **Alt text:** what the image shows and why it is there. Skip "image of". Use empty alt for decoration.

## 15. Check it

1. Run `python3 -I <skill>/scripts/check_copy.py COPY.md`. Every FAIL must be fixed. A WARN may stay if you have a reason, and you state it.
2. Do the checks at the end of `copy-human.md`.
3. Read the kind file's checklist.
