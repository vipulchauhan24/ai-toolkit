# Team Links: Phase Plan

Source: spec.approved.md. Greenfield, delivery type deployed. Each phase document is self-contained and lands as one pull request.

## Phases

- [Phase 1: Walking skeleton](phase-1-skeleton.md). A React page with a form that saves a long URL through a Node.js service and shows it back.
- [Phase 2: Short codes and redirect](phase-2-redirect.md). The service returns a 7-character code and redirects it.
- [Phase 3: Deployment](phase-3-deploy.md). The app runs at a live URL and a push to main redeploys it.

## Dependencies

```text
P1 -> P2 -> P3
```

## Parallelization

None. The phases are sequential.
