# Phase 3: Deployment

## Decisions and assumptions

- Hosting target: a small VPS with Docker. Decided by the owner.
- Branch: `phase-3-deploy`.

## Product

### Phase goal

The app works at a live URL and a push to main redeploys it.

### Acceptance criteria

1. `https://links.example.com` serves the page.
2. A push to main redeploys within 5 minutes.

## Engineering

### Dependencies on prior phases

Phase 2: the working redirect.

### Manual prerequisites

| Step | Where the result goes | How to verify |
| ---- | --------------------- | ------------- |
| Buy the domain `links.example.com` and point its A record at the VPS. | The DNS provider. | `dig +short links.example.com` prints the VPS address. |
| Create the VPS and add its SSH key as the repository secret `DEPLOY_KEY`. | The repository secrets. | The secret appears in the repository settings. |

### File reference table

| File | Change |
| ---- | ------ |
| `Dockerfile` | New |
| `.github/workflows/deploy.yml` | New |
