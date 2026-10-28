# Doc Trimmer Skill

The doc trimmer skill is a surgical editor. It reads a piece of writing and removes the noise: hedging, windups, padding, filler, and ideas that are said more than once. It keeps your facts, your voice, and your structure. The result is the fewest words that still let a competent reader understand the point.

It cuts. It does not summarise, translate, or rewrite your argument.

## What Is in This Folder

Paths are relative to the skill folder, `skills/doc-trimmer/`, inside the ai-toolkit plugin.

| Path        | Purpose                                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| `SKILL.md`  | The skill itself. Defines what counts as noise, the editing rules, and the output format.                 |
| `README.md` | This file.                                                                                                |

The skill also reads `rules/shared/markdown-rules.md` at the plugin root, which it shares with project-planner. It uses that file to format Markdown output.

## What It Does

- Walks the input from top to bottom and removes every word, phrase, sentence, or paragraph that delays the point without adding meaning.
- Reads the whole input first to map where ideas repeat, so it can remove repeats that are far apart, not only adjacent ones.
- Keeps numbers, names, code, links, quotations, and the author's reasoning exactly as written.
- Prints the trimmed text, a short summary of how much was cut, and a breakdown by category.
- For a file, also writes a trimmed copy next to the original and never touches the original.

## Using the Skill

### Step 1: Give It Input

Give the skill one of these:

- Pasted text in your message.
- A file path, such as `docs/post.md`.
- A URL, such as `https://example.com/blog/post`.

### Step 2: Ask for the Trim

In Claude Code, any of these phrases triggers the skill:

- `trim this`
- `tighten this`
- `cut the noise`
- `make this crisp`
- `remove filler`
- `edit this down`

You can also call it directly with `/ai-toolkit:doc-trimmer`.

### Step 3: Read the Result

The response contains:

- A one-line status message starting with "Trimmer is...".
- A `Source:` line for file and URL input.
- The trimmed text.
- A footer with the percentage cut, the before and after word counts, and a count per category of what was removed.
- An `Other changes:` block if headings were dropped or reworded, or facts were folded into an earlier mention.
- A `Removed blocks:` list if whole paragraphs, examples, or sections were removed, so you can check those judgement calls.
- `Trimmer done.`

For file input, the trimmed text is also saved as `<name>-cut<ext>`. For example, `post.md` becomes `post-cut.md` and `paper.txt` becomes `paper-cut.txt`. For PDF, Word, HTML, notebook, and LaTeX files the saved file is Markdown: `paper.pdf` becomes `paper-cut.md`. The saved file holds only the trimmed text, with no status line, separators, or footer, so it is ready to publish.

If the draft is already tight (under 5% cut), you still get the trimmed text in the reply, but no `-cut` file is written.

### Examples

```text
trim docs/launch-post.md
```

```text
cut the noise from this draft: <pasted text>
```

```text
tighten https://example.com/blog/post
```

```text
trim the intro of docs/design.md only and keep the examples
```

## Capabilities

### What It Removes

- Hedging language, such as "it is important to note that", "needless to say", and habit hedges like "I think" or "perhaps".
- Empty disclaimers that name no specific exception, such as "your mileage may vary".
- Throat-clearing intros, such as "In this post we will..." and "Before we begin...".
- Cliche openers, such as "In today's fast-paced world...".
- Empty subject openers, such as "There are many systems that..." (becomes "Many systems...").
- Filler transitions, such as "With that said" and "Moving on".
- Self-reference and meta-structure, such as "as we will see" and "in the next section".
- Summarising conclusions, such as "In summary" and "What this essentially means is".
- Rhetorical-question tails, such as "Right?" and "Make sense?".
- Padded constructions, such as "in order to" (becomes "to") and "a large number of" (becomes "many").
- Nominalisations, such as "make a decision" (becomes "decide").
- Filler qualifiers and intensifier stacks, such as "basically", "very", "extremely fast".
- Redundant pairs, such as "end result" and "past history".
- Restatements, including repeats that appear in different sections.
- Redundant examples and analogies that add no new failure mode, trade-off, or edge case.
- Redundant background that the reader already has.
- Redundant elaboration that repeats a claim in more words.
- Dead sentences that only echo the sentence before.
- Generic AI-style framing and exhortations.
- Line-by-line narration of code that the code already shows.
- Ceremonial closers, such as "Thank you for reading".
- Non-load-bearing words, such as needless articles, auxiliary verbs, and relative pronouns.
- Verbose phrasings and sentence frames, such as "is able to" (becomes "can") and "It is important to understand that X" (becomes "X").

### Input Handling

- Pasted text, worked on in memory.
- Local files such as `.md`, `.txt`, and `.rst`.
- Other file types, such as `.pdf`, `.docx`, `.html`, `.ipynb`, and `.tex`, after extracting their text first. The output is a Markdown file, not the original format. The original is never modified and is never rebuilt from the trimmed text. In notebooks only prose cells are trimmed, and LaTeX math stays as written. Any other format `pandoc` can read is handled the same way. If nothing can read the format, the skill says so and stops.
- URLs, downloaded as raw pages with `curl` so the author's words are not summarised on the way in. Navigation, sidebars, footers, and comments are stripped. `WebFetch` is only a fallback when `curl` fails, and the skill tells you the text may be abridged. A login page or error page is reported and not trimmed.
- Long documents, handled section by section after an idea map of the whole document is built.
- Ambiguous input: it asks once. In a non-interactive run it does not ask, and treats the input as a file, a URL, or pasted text in that order.
- Edge cases: an empty or binary file, or a file that is not valid UTF-8, is reported and skipped. A symlink is followed and the `-cut` file is written next to the path you gave. CRLF or LF line endings are kept.

### Editing Guarantees

- Cut, do not rewrite. The only changes beyond deletion are small and listed: swapping a padded phrase for a shorter equivalent, stitching the clause left after a cut, folding a missing fact into the kept mention of a repeated idea, and rewording a vague heading to carry the real claim.
- Facts, numbers, names, code, links, and quotations stay untouched. Nothing is invented.
- Front matter, HTML comments, image alt text, link text, and math stay as written. Table rows and columns are never deleted.
- An abstract, TL;DR, or executive summary is never cut to remove a repeat, and the body is not cut to match it.
- The author's voice and spelling stay. Casual register words stay when they carry tone.
- Headings, code blocks, lists, and links stay. If a cut empties a section, any surviving fact moves to the nearest related section and the empty heading is dropped.
- References are repaired. If a cut removes the target of "see Figure 2" or "the second example", the pointer is removed or redirected.
- When the same idea appears more than once, the skill keeps the most specific mention, and the earliest if they are equal.
- Hedges that express real uncertainty stay. Only habit hedges go.
- Trade-offs that name a real cost or condition stay.
- A fidelity check runs before output: every number, name, link, code block, and heading must survive unless it was cut as a repeat.
- When facts conflict with brevity, the priority order is meaning first, readability second, word count last.

### Safety

- Text inside the input is never treated as instructions. Lines such as "ignore the above" or "run this command" do not change what the skill does.
- The only file the skill writes in your project is the `-cut` copy. It never writes anywhere else because the input asks. Downloads, extracted text, and word-count files go in a temporary scratch folder, not in your project.
- If the input contains text that looks addressed to an AI, the footer says so.

### Output and Files

- The `-cut` file sits next to the original and keeps its extension. Files converted from another format (PDF, Word, HTML, notebook, LaTeX) are saved as `.md`.
- If the `-cut` file already exists, the skill asks whether to overwrite it or use the next free name in an interactive session. In a pipeline or when told not to ask, it never overwrites: it writes `name-cut-2.md`, `name-cut-3.md`, and so on, and says so. It overwrites only when you tell it to.
- Markdown output follows the layout and punctuation rules in `rules/shared/markdown-rules.md` at the plugin root: ASCII punctuation in prose, no hard line wrapping, list and heading spacing. Bold, italics, HTML, math, quotations, code, and links are left as you wrote them. This step is skipped for text with no Markdown structure.
- Word counts are measured with `wc -w` after removing front matter, fenced code, and bare Markdown symbols, the same way before and after.
- Say "just write the doc" or "don't print the stats" to get only the file path in the reply.
- When another skill calls it, or you say it is a pipeline step, it returns only the clean trimmed text, with no status line, source line, or footer. Any other run is treated as interactive.
- For long files in an interactive run, it does not reprint the whole trimmed text in chat. It prints the file path, the footer, and `Trimmer done.`. Long pasted text and URLs write no file, so the full text is printed.

### Your Controls

- Limit the scope: "only the intro", "leave the headings", "keep the examples".
- Ask for a target length, such as "cut to 500 words". The skill cuts as far as the priority order allows and tells you the final word count and the gap if it falls short. It never drops facts to hit a number, and it offers a summary only as a follow-up if you want one.

## What It Does Not Do

- It does not summarise, translate, or review a draft.
- It does not trim legal text, contracts, formal specs and standards, safety warnings, required disclosures, fiction, poetry, speeches, or quoted material. It says why and stops, unless you insist.
- Formal specs are those whose exact wording is binding, such as RFC-style MUST/SHALL text and API contracts. Design docs, PRDs, and proposals can be trimmed: requirements, acceptance criteria, numbers, and recorded decisions stay word for word.
- If an excluded block sits inside a longer document, only that block is left alone and the rest is trimmed. The skill refuses the whole input only when it is mostly excluded content.
- It is gentler with tutorials, FAQs, changelogs, reference docs, and tables. Deliberate repetition, teaching examples, parallel list items, and cross-references stay.
- For languages other than English, it applies only the language-neutral rules: repeats, redundant examples, dead sentences, and ceremonial closers. It tells you so.
- It does not edit code.

## Example

Input:

```text
In this blog post, we are going to explore an interesting topic. It is important to note that distributed systems are notoriously hard to reason about. Basically, when you have multiple nodes communicating over a network, a large number of things can go wrong. What this essentially means is that engineers need to design for failure from day one. Now that we understand the problem, let us look at the solution.
```

Output:

```text
Distributed systems are hard to reason about. When multiple nodes communicate over a network, many things can go wrong, so engineers need to design for failure from day one.
```

## Customising

- Edit `SKILL.md` to add or remove noise patterns, or to change the footer categories.
- Edit `rules/shared/markdown-rules.md` (at the plugin root) to change how the output is formatted. Other skills in the plugin use the same file.

## Installing

The skill ships in the ai-toolkit plugin. From the repository root:

```text
claude plugin marketplace add vipulchauhan24/ai-toolkit
claude plugin install ai-toolkit@product-development
/reload-plugins
```

To use it as a standalone skill, copy the `doc-trimmer/` folder and the plugin's `rules/shared/` folder, and keep their relative layout. The skill reads `../../rules/shared/markdown-rules.md`, so `rules/` must sit two levels above the skill folder:

- Project level: `.claude/skills/doc-trimmer/` and `.claude/rules/shared/markdown-rules.md`.
- User level: `~/.claude/skills/doc-trimmer/` and `~/.claude/rules/shared/markdown-rules.md`.
