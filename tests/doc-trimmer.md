# doc-trimmer

## Should trigger

- "Trim this blog post." (with a file)
- "Cut the noise from this draft."
- "Make this crisp."
- "Remove the filler and repetition from this."
- "Edit this down: [pasted text]"
- "Tighten this README section by removing fluff."
- "Strip the hedging from https://example.com/post"
- "This is too wordy. Cut the padding."
- "Remove redundancy from my essay without changing my argument."
- "Drive this down to the bare minimum word count."

## Should NOT trigger

- "Summarise this article." (it is not a summary)
- "Rewrite this to sound more professional."
- "Translate this to Spanish."
- "Poke holes in this design doc." (doc-reviewer)
- "Fix the grammar in this paragraph."
- "Shorten this function." (code)
- "Trim the whitespace in this CSV."
- "Make this contract shorter." (legal text)
- "Write a blog post about caching."
- "Split this spec into phases." (project-planner)

## Functional

**File input**
- Given: `post.md` with hedging, a windup opening and a repeated example
- When: the skill runs
- Then: `post-cut.md` exists next to the original, and `post.md` is unchanged. The cut file holds only trimmed text, with no flavour line, separators or footer. The chat shows the footer with real before and after word counts and a per-category breakdown, then `Trimmer done.`

**Facts survive**
- Given: text with numbers, a code block, a link and a quotation
- When: the skill runs
- Then: every number, code block, link and quotation is unchanged.

**Existing `-cut` file**
- Given: `post-cut.md` already exists
- When: the skill runs non-interactively
- Then: it writes `post-cut-2.md` and says the existing file was kept.

**Already tight**
- Given: a short, tight paragraph
- When: the skill runs
- Then: it says there was little to cut and writes no file.
