# Copy that sounds like a person wrote it

Read this before you draft and again when you check. The goal is a page a good human copywriter would sign. Fooling a detector is not the goal, and rewriting to beat one makes the writing worse.

## Why model writing sounds like model writing

A language model is trained to predict likely text, so with little to go on it writes the most probable sentence for a page of this type. That sentence is pleasant, balanced and could appear on a thousand other sites. A person who knows the business reaches for what happened last Tuesday.

What changes the result is **knowing more and choosing**. Trading "seamless" for "smooth" gets you nowhere. Writing "setup takes two commands" tells the reader something.

Copy written by someone who knows the subject tends to have four things:

1. **Knowledge you could only get from being there:** how the work is really done, what went wrong.
2. **A speaker.** You could tell it apart from a competitor's page with the logos removed.
3. **A choice that costs something:** a customer it turns away, a feature it admits it lacks.
4. **Unequal attention.** It spends words where the writer has most to say, and skips the rest.

## The tells, and what to do instead

A single instance means nothing. Readers notice patterns. The script column shows what `check_copy.py` counts.

### Words that stand in for facts

| Tell | Examples | Instead | Script |
|---|---|---|---|
| Hype adjectives and verbs | seamless, robust, powerful, cutting-edge, unlock, elevate, empower, streamline | Write the fact it replaces. "Seamless" becomes the setup steps. "Robust" becomes what happens when it fails | `ai-word` |
| Model vocabulary | delve, tapestry, pivotal, testament, showcase, underscore, foster, crucial | The plain word, or nothing | `ai-word` |
| Grand verbs for "is" | serves as, stands as, boasts, plays a key role | "is", "has" | `puffery` |
| Stock lines | "In today's fast-paced world", "Look no further", "Say goodbye to", "Whether you're a…" | Delete it. The next sentence is usually where the page starts | `stock-phrase` |
| Résumé clichés | passionate, results-driven, detail-oriented, team player, proven track record | The project that shows it | `ai-word`, `stock-phrase` |
| Dead metaphors | landscape, ecosystem, journey, "in the heart of", "where X meets Y" | The street, the tool, the thing | partly |
| Virtue claims | honest, genuine, truly, simply, actually, thoughtful | Show it. A page that calls itself honest is not convincing anyone | `virtue` |

Keep a word when it is the literal name for something: a climbing harness, bespoke tailoring. Add it to `allow:`.

### Sentence shapes

| Tell | Example | Instead | Script |
|---|---|---|---|
| The contrast frame | "More than a calendar, it's a way of working." "Useful rather than flashy." "Without the hassle." | Say the positive fact alone | `contrast` |
| The trailing "-ing" | "We rebuilt the API, ensuring a smooth experience." | Stop at the fact: "We rebuilt the API." | `ing-rider` |
| Automatic threes | "Fast, reliable, and secure." | List as many as there are | `triple` |
| Three fragments | "Bold. Clear. Yours." | One phrase that names the thing | `tricolon` |
| Two-fragment headings | "Small team. Big ideas." | Fine once a page. Otherwise name the thing | `two-fragment` |
| The reveal | "The outcome? Happier staff." "We tried one thing: listening." | Say it straight | no |
| Announcing the point | "It's important to note that…" "Here's the thing." | Make the point | partly |
| Filler openers | "Additionally," "Furthermore," "Moreover," | Start with the point | `transition` |
| Summing up | "In summary", "Overall", a closing line that repeats the section | End on information | `stock-phrase` |
| The page describing itself | "This section shows", "Below you'll find" | Delete it | `process-talk` |
| Even rhythm | Every sentence about 14 words, every card the same length | Let length follow meaning | `even-rhythm` |
| Rotating synonyms | "the platform… the tool… the solution" | One word, repeated | no |
| Vague authority | "Experts agree", "Industry leaders say" | Name them, or cut it | no |

### Invented detail

These look like good writing, which is why they get through.

| Tell | Instead | Script |
|---|---|---|
| Made-up specifics: a serial number, an exact hour of the morning, "41% less rework" | Only details from the fact sheet. Without one, write a plainer line | `unsourced-number` |
| Polished testimonials, always three, each with a number and a punchline | Real quotes, word for word. None is fine | `unsourced-quote` |
| The same names every time: Priya, Sarah Chen, Acme | Names from the fact sheet | `stock-name` |
| The invented founding story | The real story, or no story section | no |
| "Trusted by thousands", "10,000+ teams" | The real number and who counted it, or nothing | `unsourced-number` |

### Page habits

| Tell | Instead |
|---|---|
| Every section is label, claim heading, short intro, three cards | Choose the shape from what the section has to say: a list, a table, one paragraph, one line |
| A strip of three stats under the hero, on every page | Move each number next to the claim it supports. Keep a strip only for real figures that matter together |
| A small label above every heading | One or two a page, when the heading needs it |
| A dry one-liner closing every paragraph | End on information. Spend humour in the small text: the 404, the empty state, the sent message |
| A witty sign-off in the footer | Facts: name, year, legal links |
| The brand name's metaphor in every section | Once or never |
| Emoji as bullets, bold labels at the start of every list item | Plain lists |
| Every paragraph hedged | Commit. If you are unsure of a fact, check it or cut it |

## What to do when drafting

**Start from a fact, not a frame.** Pick the most interesting true thing in the fact sheet for each section and write the sentence around it.

**Say it the way the client would say it to a friend.** Then tidy that sentence, and resist the urge to make it impressive.

**Use names.** The tool, the street, the customer, the file format. Proper nouns are hard to fake and hard to move to another company.

**Explain how.** "Drop in the CSV. It flags duplicate customers and asks you which to keep." A description of the mechanism persuades better than a superlative.

**Admit one limit**, if the fact sheet has one. "English and Spanish only for now." It costs little and buys belief.

**Use plain "is" and "has".** They are the most human words on the page.

**Let sentences differ.** A short one lands a point. A longer one carries an explanation and is allowed to take its time. Do not manufacture variety; let it come from what each sentence is doing.

**Write the microcopy in the same voice.** Labels, errors, the sent message, the 404. This is where a person's hand shows most.

### Before and after

These clients are made up.

| Model draft | Rewritten from facts |
|---|---|
| "Passionate full-stack developer delivering robust, scalable solutions that drive results." | "I build the parts of web apps that have to stay fast: 10 million rows in a timetable, six states at once." |
| "Elevate your team's workflow with our seamless, AI-powered scheduling platform." | "Rosters for care homes. It checks each shift against staffing ratios before you publish." |
| "Nestled in the heart of the city, our cozy café offers a vibrant atmosphere and artisanal coffee." | "Filter coffee and cinnamon toast opposite the tram depot. Open from eight." |
| "We don't just build websites. We craft digital experiences that inspire." | "We build sites for museums. Our last four opened on time." |
| "Something went wrong. Please try again later." | "We couldn't save your changes because the connection dropped. Your text is still here. Try again." |
| "No data available." | "No invoices yet. They appear here once you send your first one." |

## When the rules backfire

Each rule breeds its own habit. After editing, look for the replacement tic.

| The edit | The new problem | Better |
|---|---|---|
| Dropped every em dash | Sentences glued with commas | Split the sentence, or use a colon |
| Banned the contrast frame | The same idea, reworded with "rather than" or "instead of" | Say only what is true of this client. The script counts every form together |
| Removed hype | A new soft vocabulary: quietly, steady, practical | Put a measurement where the adjective was |
| Stopped listing three things | Pairs everywhere | Count the real items |
| Made vague lines specific | Numbers nobody measured | Go back to the fact sheet |
| Shortened everything | Choppy, breathless fragments | Keep one sentence per section that takes its time |
| Tried to add personality | A quip in each section | Keep humour for the small text |

If following a rule makes a sentence worse, break the rule. These are habits to watch. Good writing comes first.

## What is not a tell

Leave these alone. Each one is a normal part of good writing.

- Correct spelling and grammar. People who write for a living have those too.
- Wordy phrases and small qualifiers. Wikipedia counts "the fact that", "very" and "perhaps" as more common in human text.
- A single "however" or "also". Transition words only mean something in bulk.
- Three items, when the client really has three.
- Asking for the sale. A landing page is meant to persuade, as long as the claims are real.
- Anything the client wrote themselves. Keep it, and use `allow:`.
- Curly quotes. Wikipedia lists them as a sign of AI text, but that is about its own plain-text articles. On a web page they are correct.

## Checks before you finish

1. **Run the script.** `check_copy.py COPY.md`.
2. **The swap test.** Replace the client's name with a competitor's, and read the headline and section headings again. Any line that stays true is empty, so rewrite it with real facts.
3. **Read it out loud.** Imagine the client saying it to a customer across a table. Anything that would embarrass them goes.
4. **The stranger test.** Read only the first screen. Can you tell what is on offer, whom it serves and the next step?
5. **The trace test.** Point to where each claim came from. If you can't, it goes.
6. **The replacement test.** Look for the tic that replaced the one you removed.
7. **Sameness.** If you have written other pages in this project or session, read their headlines side by side. A shared rhythm or joke is a tic.
