# Phase 2: Short codes and redirect

## Decisions and assumptions

- Stack and pattern are inherited from phase 1.
- Branch: `phase-2-redirect`.

## Product

### Phase goal

Saving a URL returns a 7-character code, and visiting the code redirects to the long URL.

### Acceptance criteria

1. A valid URL returns a 7-character code in under 200 ms.
2. Visiting the code redirects with a 302.

## Engineering

### Dependencies on prior phases

Phase 1: the form, the list and `linkService.ts`.

### Manual prerequisites

None.

### File reference table

| File | Change |
| ---- | ------ |
| `server/src/linkService.ts` | Changed: generates a code |
| `server/src/redirect.ts` | New: looks up a code |
| `web/src/App.tsx` | Changed: shows the short link |
