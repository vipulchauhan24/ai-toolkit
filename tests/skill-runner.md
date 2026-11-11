# skill-runner

An agent, not a skill: Claude Code starts it with the Agent tool. These checks use the same three parts as the skills.

## Should trigger

- "Run doc-reviewer on design.md in the background and write a report."
- "Use the skill-runner agent to trim post.md."
- "Run the doc-trimmer and doc-reviewer skills on this file, one after the other, away from my main context."
- "Start a runner for the frontend-react skill on phase 3, in a worktree."
- "Run these three skills in parallel, each with its own run directory."
- "Have a subagent run project-planner on spec.md and write a report file."
- "Run frontend-react on phase 4 without asking me questions."
- "Run the design-md skill in the background."
- "Use a skill runner so the long review stays out of this chat."
- "Run the reviewer skill on both documents and give me report paths."

## Should NOT trigger

- "Review this design doc." (run doc-reviewer directly)
- "Trim this paragraph." (run doc-trimmer directly)
- "What does the skill-runner agent do?"
- "Run the test suite."
- "Explore the codebase and tell me where auth lives." (an exploration agent)
- "Write a skill for me."
- "Run this script in the background."
- "Summarise this file."
- "Create a git worktree."
- "Delegate this refactor to a subagent." (no named skill)

## Functional

**Report with evidence**
- Given: `design.md` and a run directory that does not exist
- When: the runner is asked to run `ai-toolkit:doc-reviewer` on it
- Then: the run directory holds `report.md` with a section for the skill, evidence that only the skill's steps produce, the files written and the status. The review text is saved as a separate output file, not pasted into the report. The reply is at most five lines.

**Missing input**
- Given: an input path that does not exist
- When: the runner is asked to run a skill on it
- Then: the status is blocked, the reply names the missing path, and no skill runs.

**Existing run directory**
- Given: a run directory that already exists
- When: the runner is asked to use it
- Then: the status is blocked because `mkdir` fails, the existing files are untouched, and no report is written there.
