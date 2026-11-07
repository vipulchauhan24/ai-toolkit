import type { Express } from "express";

export interface AppDeps {
  readonly createApp: () => Express;
}

export function start(deps: AppDeps, port: number): void {
  const app = deps.createApp();
  app.listen(port);
}
