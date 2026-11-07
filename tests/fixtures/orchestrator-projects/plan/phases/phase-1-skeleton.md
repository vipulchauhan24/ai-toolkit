# Phase 1: Walking skeleton

## Decisions and assumptions

- Greenfield. Stack pinned here: TypeScript, React 18 with Vite for the page, Node.js 20 with Express for the service, SQLite for storage.
- Pattern: layered
- Reason: Express with a small service, the framework default.
- Branch: `phase-1-skeleton`.

## Product

### Phase goal

A person opens the page, pastes a long URL, and sees it saved and listed.

### Acceptance criteria

1. The form posts a URL and the list shows it.
2. The service stores it in SQLite.

## Engineering

### Dependencies on prior phases

None.

### Manual prerequisites

None.

### File reference table

| File | Change |
| ---- | ------ |
| `web/src/App.tsx` | New: the form and the list |
| `web/src/api.ts` | New: typed client for the service |
| `server/src/linkService.ts` | New: saves and lists links |
| `server/src/db.ts` | New: SQLite connection |
| `package.json` | New |
