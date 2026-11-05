# Skill tests

One file per skill. Each has three parts, following the Anthropic skills guide:

1. **Should trigger**: obvious and paraphrased requests. The skill must load without being named.
2. **Should NOT trigger**: unrelated requests, and near misses that belong to another skill in this plugin. The near misses are the ones that matter.
3. **Functional**: Given / When / Then checks on what the skill produces.

## Running them

Manual, in a fresh Claude Code session with the plugin installed:

- Triggering: paste each query without naming the skill. Pass if the skill loads (or, for "should NOT", does not). Ask "When would you use the X skill?" if a result is surprising and compare with the description.
- Functional: run the request in a scratch directory, then check each Then line.

Target from the guide: the skill loads on about 90% of the should-trigger queries and on none of the should-not queries. Re-run the whole file after any change to a skill's `description`.

Run output goes in `tests/runs/`, which is gitignored.
