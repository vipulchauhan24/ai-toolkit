# Recorded run: frontend-react pattern mismatch (phase 1, criterion 9)

Date: 2026-11-03. Run headless with `claude -p`, the plugin loaded from this repo with `--plugin-dir`, tools limited to Read, Glob, Grep, Skill and `python3 --version`.

Setup: a copy of a small React 19 project in an MVVM layout (`OrderList.tsx` view, `useOrderList.ts` hook, `orderApi.ts` and `order.types.ts` model), plus `phases/phase-2-order-count.md` containing `Pattern: mvc`. The throwaway project lives outside the repository.

Prompt: `Use the ai-toolkit:frontend-react skill to build phases/phase-2-order-count.md. This is a non-interactive run: never ask questions, write a Blocked report if blocked.`

Output, copied from the run:

```text
**Blocked: nothing was built.**

Pattern mismatch: phase document pins mvc, codebase uses mvvm.

- Phase document: phases/phase-2-order-count.md:6 pins Pattern: mvc, with the reason "the team prefers controllers for request handling".
- Codebase: it follows the mvvm layout in architecture-patterns.md section 3.
  - src/features/orders/OrderList.tsx:4 is the view. It only calls its hook and renders.
  - src/features/orders/useOrderList.ts:5-11 is the view model. It holds the state and calls fetchOrders.
  - orderApi.ts and order.types.ts are the model.
  - There are no controllers, and imports run view -> hook -> model.

What the caller must supply, either one:
1. Change the phase document to Pattern: mvvm.
2. Confirm that this codebase should move to mvc, and give a migration scope. That is a separate phase.

Checks: none run. Preflight passed (Python 3 and scripts/check_react.py present).
```

Check:

```text
$ grep 'Pattern mismatch' output -> Pattern mismatch: phase document pins mvc, codebase uses mvvm.
```

Result: pass. The Blocked report names both patterns.
